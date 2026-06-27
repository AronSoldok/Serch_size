from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from scanner import (
    format_size,
    parse_size_threshold,
    scan_immediate_subdirs,
)


class DirectorySizeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Сканер размеров директорий")
        self.root.geometry("1200x720")
        self.root.minsize(960, 600)

        self._cancel_event = threading.Event()
        self._scan_thread: threading.Thread | None = None
        self._progress_queue: queue.Queue = queue.Queue()
        self._history: list[Path] = []
        self._current_scan_root: Path | None = None
        self._item_paths: dict[str, Path] = {}

        self._build_ui()
        self._poll_progress_queue()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        path_frame = ttk.Frame(main)
        path_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(path_frame, text="Директория:").pack(side=tk.LEFT)

        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))

        browse_btn = ttk.Button(path_frame, text="Обзор…", command=self._browse_folder)
        browse_btn.pack(side=tk.LEFT)

        threshold_frame = ttk.Frame(main)
        threshold_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(threshold_frame, text="Порог:").pack(side=tk.LEFT)

        self.threshold_var = tk.StringVar(value="250")
        threshold_entry = ttk.Entry(threshold_frame, textvariable=self.threshold_var, width=10)
        threshold_entry.pack(side=tk.LEFT, padx=(8, 8))

        self.unit_var = tk.StringVar(value="МБ")
        unit_combo = ttk.Combobox(
            threshold_frame,
            textvariable=self.unit_var,
            values=["Б", "КБ", "МБ", "ГБ"],
            state="readonly",
            width=6,
        )
        unit_combo.pack(side=tk.LEFT)

        actions_frame = ttk.Frame(main)
        actions_frame.pack(fill=tk.X, pady=(0, 8))

        self.scan_btn = ttk.Button(actions_frame, text="Сканировать", command=self._start_scan)
        self.scan_btn.pack(side=tk.LEFT)

        self.back_btn = ttk.Button(
            actions_frame,
            text="Назад",
            command=self._go_back,
            state=tk.DISABLED,
        )
        self.back_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.cancel_btn = ttk.Button(
            actions_frame,
            text="Отмена",
            command=self._cancel_scan,
            state=tk.DISABLED,
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.status_var = tk.StringVar(value="Выберите директорию и нажмите «Сканировать»")
        status_label = ttk.Label(main, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=(0, 4))

        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        columns = ("folder", "size", "note", "path")
        self.tree = ttk.Treeview(main, columns=columns, show="headings")
        self.tree.heading("folder", text="Папка")
        self.tree.heading("size", text="Размер")
        self.tree.heading("note", text="Примечание")
        self.tree.heading("path", text="Путь")
        self.tree.column("folder", width=220, stretch=False)
        self.tree.column("size", width=110, stretch=False)
        self.tree.column("note", width=180, stretch=False)
        self.tree.column("path", width=620, stretch=True)
        self.tree.tag_configure("system", foreground="#888888")

        scrollbar = ttk.Scrollbar(main, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_folder_double_click)

    def _browse_folder(self) -> None:
        selected = filedialog.askdirectory(title="Выберите директорию для сканирования")
        if selected:
            self.path_var.set(selected)
            self._history.clear()
            self._current_scan_root = None
            self._update_back_button_state()

    def _validate_inputs(self) -> Path | None:
        path_text = self.path_var.get().strip()
        if not path_text:
            messagebox.showerror("Ошибка", "Укажите директорию для сканирования.")
            return None

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror("Ошибка", "Указанный путь не существует.")
            return None
        if not path.is_dir():
            messagebox.showerror("Ошибка", "Указанный путь не является директорией.")
            return None

        try:
            threshold_value = float(self.threshold_var.get().strip().replace(",", "."))
            parse_size_threshold(threshold_value, self.unit_var.get())
        except ValueError as exc:
            messagebox.showerror("Ошибка", f"Некорректный порог: {exc}")
            return None

        return path

    def _start_scan(self, push_history: bool = True) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            return

        path = self._validate_inputs()
        if path is None:
            return

        try:
            threshold_value = float(self.threshold_var.get().strip().replace(",", "."))
            min_bytes = parse_size_threshold(threshold_value, self.unit_var.get())
        except ValueError:
            return

        if push_history and self._current_scan_root is not None and self._current_scan_root != path:
            self._history.append(self._current_scan_root)

        self._current_scan_root = path
        self._update_back_button_state()

        self._clear_results()
        self._cancel_event.clear()
        self._set_scanning_state(True)
        self.progress["value"] = 0
        self.status_var.set(f"Сканирование: {path}")

        def worker() -> None:
            def on_progress(current: int, total: int, folder_name: str) -> None:
                self._progress_queue.put(("progress", current, total, folder_name, path))

            try:
                results = scan_immediate_subdirs(
                    path,
                    min_bytes,
                    on_progress=on_progress,
                    cancel_event=self._cancel_event,
                )
                self._progress_queue.put(("done", results, path))
            except Exception as exc:
                self._progress_queue.put(("error", str(exc)))

        self._scan_thread = threading.Thread(target=worker, daemon=True)
        self._scan_thread.start()

    def _go_back(self) -> None:
        if not self._history or (self._scan_thread is not None and self._scan_thread.is_alive()):
            return

        previous_path = self._history.pop()
        self.path_var.set(str(previous_path))
        self._update_back_button_state()
        self._start_scan(push_history=False)

    def _on_folder_double_click(self, _event: tk.Event) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            return

        selected = self.tree.selection()
        if not selected:
            return

        folder_path = self._item_paths.get(selected[0])
        if folder_path is None or not folder_path.is_dir():
            return

        self.path_var.set(str(folder_path))
        self._start_scan(push_history=True)

    def _cancel_scan(self) -> None:
        self._cancel_event.set()
        self.status_var.set("Отмена сканирования…")

    def _set_scanning_state(self, scanning: bool) -> None:
        state = tk.DISABLED if scanning else tk.NORMAL
        self.scan_btn.configure(state=state)
        self.back_btn.configure(state=tk.DISABLED if scanning or not self._history else tk.NORMAL)
        self.cancel_btn.configure(state=tk.NORMAL if scanning else tk.DISABLED)

    def _update_back_button_state(self) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            self.back_btn.configure(state=tk.DISABLED)
            return
        self.back_btn.configure(state=tk.NORMAL if self._history else tk.DISABLED)

    def _clear_results(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_paths.clear()

    def _poll_progress_queue(self) -> None:
        try:
            while True:
                message = self._progress_queue.get_nowait()
                self._handle_queue_message(message)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_progress_queue)

    def _handle_queue_message(self, message: tuple) -> None:
        kind = message[0]

        if kind == "progress":
            _, current, total, folder_name, scan_path = message
            if total > 0:
                self.progress["maximum"] = total
                self.progress["value"] = current
            self.status_var.set(f"Сканирование ({current}/{total}): {folder_name} — {scan_path}")
            return

        self._set_scanning_state(False)
        self._scan_thread = None
        self._update_back_button_state()

        if kind == "error":
            _, error_text = message
            self.status_var.set("Ошибка сканирования")
            messagebox.showerror("Ошибка", error_text)
            return

        if kind == "done":
            _, results, scan_path = message
            if self._cancel_event.is_set():
                self.status_var.set("Сканирование отменено")
                return

            for result in results:
                note = "Системная папка" if result.is_system else ""
                tags = ("system",) if result.is_system else ()
                item_id = self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        result.path.name,
                        format_size(result.size_bytes),
                        note,
                        str(result.path),
                    ),
                    tags=tags,
                )
                self._item_paths[item_id] = result.path

            if results:
                self.status_var.set(f"Сканирование: {scan_path} — найдено папок: {len(results)}")
            else:
                self.status_var.set(f"Сканирование: {scan_path} — папки ≥ порога не найдены")
                messagebox.showinfo("Результат", "Папки ≥ порога не найдены")


def run_app() -> None:
    root = tk.Tk()
    DirectorySizeApp(root)
    root.mainloop()
