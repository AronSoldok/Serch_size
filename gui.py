from __future__ import annotations

import json
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from i18n import (
    DEFAULT_LANG,
    LANGUAGES,
    default_language,
    default_unit,
    t,
    unit_labels,
)
from scanner import (
    format_size,
    parse_size_threshold,
    scan_immediate_subdirs,
)

ctk.set_default_color_theme("blue")

SETTINGS_PATH = Path.home() / ".serch_size" / "settings.json"

THEMES = {
    "light": {
        "bg": "#F3F4F6",
        "panel": "#FFFFFF",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "secondary": "#E5E7EB",
        "secondary_hover": "#D1D5DB",
        "text": "#111827",
        "muted": "#6B7280",
        "system": "#9CA3AF",
        "row_even": "#FFFFFF",
        "row_odd": "#F9FAFB",
        "heading": "#F3F4F6",
    },
    "soft_dark": {
        "bg": "#1E2430",
        "panel": "#2A3140",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "secondary": "#3D4657",
        "secondary_hover": "#4B5563",
        "text": "#E5E7EB",
        "muted": "#9CA3AF",
        "system": "#6B7280",
        "row_even": "#2A3140",
        "row_odd": "#323A4A",
        "heading": "#252B38",
    },
}


class DirectorySizeApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("1200x720")
        self.minsize(960, 600)

        self._cancel_event = threading.Event()
        self._scan_thread: threading.Thread | None = None
        self._progress_queue: queue.Queue = queue.Queue()
        self._history: list[Path] = []
        self._current_scan_root: Path | None = None
        self._item_paths: dict[str, Path] = {}
        self._item_is_system: dict[str, bool] = {}
        self._item_size_bytes: dict[str, int] = {}
        self._context_menu: tk.Menu | None = None
        self._theme_mode = "light"
        self._language = DEFAULT_LANG
        self._applying_theme = False
        self._applying_language = False
        self._is_idle = True

        settings = self._load_settings()
        self._language = settings.get("language", default_language())
        self._build_ui()
        self._apply_language(self._language)
        self._apply_theme(settings.get("theme", "light"))
        self._poll_progress_queue()

    def _colors(self) -> dict[str, str]:
        return THEMES[self._theme_mode]

    @staticmethod
    def _load_settings() -> dict:
        defaults = {"theme": "light", "language": default_language()}
        try:
            if SETTINGS_PATH.exists():
                data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
                if data.get("theme") in THEMES:
                    defaults["theme"] = data["theme"]
                if data.get("language") in LANGUAGES:
                    defaults["language"] = data["language"]
        except (OSError, json.JSONDecodeError):
            pass
        return defaults

    def _save_settings(self) -> None:
        try:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS_PATH.write_text(
                json.dumps(
                    {"theme": self._theme_mode, "language": self._language},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _current_unit_index(self) -> int:
        labels = unit_labels(self._language)
        current = self.unit_combo.get()
        if current in labels:
            return labels.index(current)
        mb = default_unit(self._language)
        return labels.index(mb) if mb in labels else 2

    def _apply_language(self, lang: str) -> None:
        if lang not in LANGUAGES:
            lang = DEFAULT_LANG

        self._applying_language = True
        self._language = lang
        unit_index = self._current_unit_index()

        self.title(t(lang, "app_title"))
        self.title_label.configure(text=t(lang, "app_title"))
        self.subtitle_label.configure(text=t(lang, "subtitle"))
        self.theme_switch.configure(text=t(lang, "soft_dark_theme"))
        self.settings_title_label.configure(text=t(lang, "settings_title"))
        self.directory_label.configure(text=t(lang, "directory_label"))
        self.threshold_label.configure(text=t(lang, "threshold_label"))
        self.browse_btn.configure(text=t(lang, "browse"))
        self.scan_btn.configure(text=t(lang, "scan"))
        self.back_btn.configure(text=t(lang, "back"))
        self.copy_btn.configure(text=t(lang, "copy_path"))
        self.open_btn.configure(text=t(lang, "open_folder"))
        self.cancel_btn.configure(text=t(lang, "cancel"))
        self.results_title_label.configure(text=t(lang, "results_title"))
        self.hint_label.configure(text=t(lang, "hint"))

        labels = unit_labels(lang)
        self.unit_combo.configure(values=labels)
        self.unit_combo.set(labels[unit_index])

        self.tree.heading("folder", text=t(lang, "col_folder"))
        self.tree.heading("size", text=t(lang, "col_size"))
        self.tree.heading("note", text=t(lang, "col_note"))
        self.tree.heading("path", text=t(lang, "col_path"))

        if self._context_menu is not None:
            self._context_menu.entryconfigure(0, label=t(lang, "copy_path_menu"))
            self._context_menu.entryconfigure(1, label=t(lang, "open_folder_menu"))

        self._refresh_result_sizes_and_notes()

        if self._is_idle:
            self._set_status(t(lang, "status_ready"))

        self.language_combo.set(LANGUAGES[lang])
        self._applying_language = False
        self._save_settings()

    def _refresh_result_sizes_and_notes(self) -> None:
        lang = self._language
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            if len(values) < 4:
                continue
            note = t(lang, "system_folder") if self._item_is_system.get(item_id, False) else ""
            size_bytes = self._item_size_bytes.get(item_id)
            size_text = format_size(size_bytes, lang) if size_bytes is not None else values[1]
            self.tree.item(item_id, values=(values[0], size_text, note, values[3]))

    def _on_language_selected(self, _choice: str) -> None:
        if self._applying_language:
            return
        for code, label in LANGUAGES.items():
            if label == self.language_combo.get():
                self._apply_language(code)
                break

    def _apply_theme(self, mode: str) -> None:
        if mode not in THEMES:
            mode = "light"

        self._applying_theme = True
        self._theme_mode = mode
        colors = self._colors()

        ctk.set_appearance_mode("dark" if mode == "soft_dark" else "light")
        self.configure(fg_color=colors["bg"])

        self.settings_frame.configure(fg_color=colors["panel"])
        self.results_frame.configure(fg_color=colors["panel"])

        self.title_label.configure(text_color=colors["text"])
        self.subtitle_label.configure(text_color=colors["muted"])
        self.settings_title_label.configure(text_color=colors["text"])
        self.results_title_label.configure(text_color=colors["text"])
        self.hint_label.configure(text_color=colors["muted"])
        self.status_label.configure(text_color=colors["text"])

        self.scan_btn.configure(
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color="#FFFFFF",
        )
        for btn in (self.browse_btn, self.back_btn, self.copy_btn, self.open_btn, self.cancel_btn):
            btn.configure(
                fg_color=colors["secondary"],
                hover_color=colors["secondary_hover"],
                text_color=colors["text"],
            )

        self._configure_tree_style(colors)
        self._refresh_tree_row_tags()

        if self._context_menu is not None:
            self._context_menu.configure(
                bg=colors["panel"],
                fg=colors["text"],
                activebackground=colors["secondary"],
                activeforeground=colors["text"],
            )

        if self.theme_switch.get() != (1 if mode == "soft_dark" else 0):
            if mode == "soft_dark":
                self.theme_switch.select()
            else:
                self.theme_switch.deselect()

        self._applying_theme = False
        self._save_settings()

    def _on_theme_toggle(self) -> None:
        if self._applying_theme:
            return
        mode = "soft_dark" if self.theme_switch.get() else "light"
        self._apply_theme(mode)

    def _configure_tree_style(self, colors: dict[str, str]) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Results.Treeview",
            background=colors["row_even"],
            fieldbackground=colors["row_even"],
            foreground=colors["text"],
            rowheight=28,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Results.Treeview.Heading",
            background=colors["heading"],
            foreground=colors["text"],
            font=("Segoe UI", 10, "bold"),
            padding=(8, 6),
        )
        style.map(
            "Results.Treeview",
            background=[("selected", colors["accent"])],
            foreground=[("selected", "#FFFFFF")],
        )

        self.tree.tag_configure("even", background=colors["row_even"])
        self.tree.tag_configure("odd", background=colors["row_odd"])
        self.tree.tag_configure("system", foreground=colors["system"])

    def _refresh_tree_row_tags(self) -> None:
        for index, item_id in enumerate(self.tree.get_children()):
            stripe = "even" if index % 2 == 0 else "odd"
            is_system = self._item_is_system.get(item_id, False)
            tags = (stripe, "system") if is_system else (stripe,)
            self.tree.item(item_id, tags=tags)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(4, weight=1)

        title_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        muted_font = ctk.CTkFont(family="Segoe UI", size=13)
        section_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        button_font = ctk.CTkFont(family="Segoe UI", size=13)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(header, text="", font=title_font, anchor="w")
        self.title_label.grid(row=0, column=0, sticky="w")

        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.grid(row=0, column=1, sticky="e")

        self.language_combo = ctk.CTkComboBox(
            controls,
            values=list(LANGUAGES.values()),
            width=130,
            state="readonly",
            command=self._on_language_selected,
        )
        self.language_combo.pack(side=tk.LEFT, padx=(0, 12))

        self.theme_switch = ctk.CTkSwitch(controls, text="", command=self._on_theme_toggle)
        self.theme_switch.pack(side=tk.LEFT)

        self.subtitle_label = ctk.CTkLabel(main, text="", font=muted_font, anchor="w")
        self.subtitle_label.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        self.settings_frame = ctk.CTkFrame(main, corner_radius=12)
        self.settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.settings_title_label = ctk.CTkLabel(
            self.settings_frame, text="", font=section_font, anchor="w"
        )
        self.settings_title_label.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 12))

        path_row = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        path_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        path_row.grid_columnconfigure(1, weight=1)

        self.directory_label = ctk.CTkLabel(path_row, text="", width=100, anchor="w")
        self.directory_label.grid(row=0, column=0, sticky="w")
        self.path_entry = ctk.CTkEntry(path_row, height=36)
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.browse_btn = ctk.CTkButton(path_row, text="", width=100, height=36, command=self._browse_folder)
        self.browse_btn.grid(row=0, column=2)

        threshold_row = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        threshold_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        self.threshold_label = ctk.CTkLabel(threshold_row, text="", width=100, anchor="w")
        self.threshold_label.grid(row=0, column=0, sticky="w")
        self.threshold_entry = ctk.CTkEntry(threshold_row, width=120, height=36)
        self.threshold_entry.grid(row=0, column=1, sticky="w", padx=(8, 8))
        self.threshold_entry.insert(0, "250")
        self.unit_combo = ctk.CTkComboBox(
            threshold_row,
            values=unit_labels(self._language),
            width=90,
            height=36,
            state="readonly",
        )
        self.unit_combo.grid(row=0, column=2, sticky="w")
        self.unit_combo.set(default_unit(self._language))

        actions_frame = ctk.CTkFrame(main, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="new", pady=(0, 12))
        actions_frame.grid_columnconfigure(5, weight=1)

        self.scan_btn = ctk.CTkButton(
            actions_frame,
            text="",
            command=self._start_scan,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=36,
            width=140,
        )
        self.scan_btn.grid(row=0, column=0, padx=(0, 8))

        self.back_btn = ctk.CTkButton(
            actions_frame,
            text="",
            command=self._go_back,
            font=button_font,
            height=36,
            width=100,
            state="disabled",
        )
        self.back_btn.grid(row=0, column=1, padx=(0, 8))

        self.copy_btn = ctk.CTkButton(
            actions_frame,
            text="",
            command=self._copy_selected_path,
            font=button_font,
            height=36,
            width=150,
            state="disabled",
        )
        self.copy_btn.grid(row=0, column=2, padx=(0, 8))

        self.open_btn = ctk.CTkButton(
            actions_frame,
            text="",
            command=self._open_selected_folder,
            font=button_font,
            height=36,
            width=150,
            state="disabled",
        )
        self.open_btn.grid(row=0, column=3, padx=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            actions_frame,
            text="",
            command=self._cancel_scan,
            font=button_font,
            height=36,
            width=100,
            state="disabled",
        )
        self.cancel_btn.grid(row=0, column=4)

        self.results_frame = ctk.CTkFrame(main, corner_radius=12)
        self.results_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 12))
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(2, weight=1)

        self.results_title_label = ctk.CTkLabel(
            self.results_frame, text="", font=section_font, anchor="w"
        )
        self.results_title_label.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        self.hint_label = ctk.CTkLabel(self.results_frame, text="", font=muted_font, anchor="w")
        self.hint_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        table_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = ("folder", "size", "note", "path")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Results.Treeview")
        self.tree.heading("folder", text="")
        self.tree.heading("size", text="")
        self.tree.heading("note", text="")
        self.tree.heading("path", text="")
        self.tree.column("folder", width=220, stretch=False)
        self.tree.column("size", width=110, stretch=False)
        self.tree.column("note", width=180, stretch=False)
        self.tree.column("path", width=620, stretch=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self._on_folder_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.bind("<Control-c>", self._on_copy_shortcut)

        self._context_menu = tk.Menu(self, tearoff=0)
        self._context_menu.add_command(label="", command=self._copy_selected_path)
        self._context_menu.add_command(label="", command=self._open_selected_folder)

        status_frame = ctk.CTkFrame(main, fg_color="transparent")
        status_frame.grid(row=5, column=0, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(status_frame, text="", font=muted_font, anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.progress = ctk.CTkProgressBar(status_frame, height=12)
        self.progress.grid(row=1, column=0, sticky="ew")
        self.progress.set(0)

    def _set_path_entry(self, value: str) -> None:
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, value)

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def _get_selected_path(self) -> Path | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return self._item_paths.get(selected[0])

    def _open_in_explorer(self, path: Path) -> None:
        try:
            os.startfile(str(path))
        except OSError:
            messagebox.showerror(
                t(self._language, "error_title"),
                t(self._language, "error_open_folder", path=path),
            )

    def _open_selected_folder(self) -> None:
        path = self._get_selected_path()
        if path is not None:
            self._open_in_explorer(path)

    def _copy_path_to_clipboard(self, path: Path) -> None:
        self.clipboard_clear()
        self.clipboard_append(str(path))
        self._is_idle = False
        self._set_status(t(self._language, "status_path_copied", path=path))

    def _copy_selected_path(self) -> None:
        path = self._get_selected_path()
        if path is not None:
            self._copy_path_to_clipboard(path)

    def _on_copy_shortcut(self, _event: tk.Event) -> str | None:
        if self.tree.selection():
            path = self._get_selected_path()
            if path is not None:
                self._copy_path_to_clipboard(path)
                return "break"
        return None

    def _show_context_menu(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        self.tree.focus(item)
        self._update_selection_buttons_state()
        if self._context_menu is not None:
            self._context_menu.tk_popup(event.x_root, event.y_root)

    def _on_tree_select(self, _event: tk.Event) -> None:
        self._update_selection_buttons_state()

    def _update_selection_buttons_state(self) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            self.copy_btn.configure(state="disabled")
            self.open_btn.configure(state="disabled")
            return
        state = "normal" if self._get_selected_path() is not None else "disabled"
        self.copy_btn.configure(state=state)
        self.open_btn.configure(state=state)

    def _browse_folder(self) -> None:
        selected = filedialog.askdirectory(title=t(self._language, "dialog_browse_title"))
        if selected:
            self._set_path_entry(selected)
            self._history.clear()
            self._current_scan_root = None
            self._update_back_button_state()
            self._update_selection_buttons_state()

    def _validate_inputs(self) -> Path | None:
        lang = self._language
        path_text = self.path_entry.get().strip()
        if not path_text:
            messagebox.showerror(t(lang, "error_title"), t(lang, "error_no_directory"))
            return None

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror(t(lang, "error_title"), t(lang, "error_path_not_exists"))
            return None
        if not path.is_dir():
            messagebox.showerror(t(lang, "error_title"), t(lang, "error_not_directory"))
            return None

        try:
            threshold_value = float(self.threshold_entry.get().strip().replace(",", "."))
            parse_size_threshold(threshold_value, self.unit_combo.get(), lang)
        except ValueError as exc:
            messagebox.showerror(
                t(lang, "error_title"),
                t(lang, "error_invalid_threshold", details=str(exc)),
            )
            return None

        return path

    def _start_scan(self, push_history: bool = True) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            return

        path = self._validate_inputs()
        if path is None:
            return

        lang = self._language
        try:
            threshold_value = float(self.threshold_entry.get().strip().replace(",", "."))
            min_bytes = parse_size_threshold(threshold_value, self.unit_combo.get(), lang)
        except ValueError:
            return

        if push_history and self._current_scan_root is not None and self._current_scan_root != path:
            self._history.append(self._current_scan_root)

        self._current_scan_root = path
        self._update_back_button_state()

        self._clear_results()
        self._cancel_event.clear()
        self._set_scanning_state(True)
        self.progress.set(0)
        self._is_idle = False
        self._set_status(t(lang, "status_scanning", path=path))

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
        self._set_path_entry(str(previous_path))
        self._update_back_button_state()
        self._start_scan(push_history=False)

    def _on_folder_double_click(self, _event: tk.Event) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            return

        folder_path = self._get_selected_path()
        if folder_path is None or not folder_path.is_dir():
            return

        self._set_path_entry(str(folder_path))
        self._start_scan(push_history=True)

    def _cancel_scan(self) -> None:
        self._cancel_event.set()
        self._is_idle = False
        self._set_status(t(self._language, "status_canceling"))

    def _set_scanning_state(self, scanning: bool) -> None:
        self.scan_btn.configure(state="disabled" if scanning else "normal")
        self.back_btn.configure(state="disabled" if scanning or not self._history else "normal")
        self.cancel_btn.configure(state="normal" if scanning else "disabled")
        if scanning:
            self.copy_btn.configure(state="disabled")
            self.open_btn.configure(state="disabled")
        else:
            self._update_selection_buttons_state()

    def _update_back_button_state(self) -> None:
        if self._scan_thread is not None and self._scan_thread.is_alive():
            self.back_btn.configure(state="disabled")
            return
        self.back_btn.configure(state="normal" if self._history else "disabled")

    def _clear_results(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_paths.clear()
        self._item_is_system.clear()
        self._item_size_bytes.clear()
        self._update_selection_buttons_state()

    def _poll_progress_queue(self) -> None:
        try:
            while True:
                message = self._progress_queue.get_nowait()
                self._handle_queue_message(message)
        except queue.Empty:
            pass
        self.after(100, self._poll_progress_queue)

    def _handle_queue_message(self, message: tuple) -> None:
        kind = message[0]
        lang = self._language

        if kind == "progress":
            _, current, total, folder_name, scan_path = message
            self.progress.set(current / total if total else 0)
            self._set_status(
                t(
                    lang,
                    "status_scanning_progress",
                    current=current,
                    total=total,
                    name=folder_name,
                    path=scan_path,
                )
            )
            return

        self._set_scanning_state(False)
        self._scan_thread = None
        self._update_back_button_state()

        if kind == "error":
            _, error_text = message
            self._is_idle = True
            self._set_status(t(lang, "status_scan_error"))
            messagebox.showerror(t(lang, "error_title"), error_text)
            return

        if kind == "done":
            _, results, scan_path = message
            if self._cancel_event.is_set():
                self._is_idle = True
                self._set_status(t(lang, "status_scan_canceled"))
                return

            colors = self._colors()
            for index, result in enumerate(results):
                note = t(lang, "system_folder") if result.is_system else ""
                stripe = "even" if index % 2 == 0 else "odd"
                tags = (stripe, "system") if result.is_system else (stripe,)
                item_id = self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        result.path.name,
                        format_size(result.size_bytes, lang),
                        note,
                        str(result.path),
                    ),
                    tags=tags,
                )
                self._item_paths[item_id] = result.path
                self._item_is_system[item_id] = result.is_system
                self._item_size_bytes[item_id] = result.size_bytes

            self.tree.tag_configure("even", background=colors["row_even"])
            self.tree.tag_configure("odd", background=colors["row_odd"])
            self.tree.tag_configure("system", foreground=colors["system"])

            self._update_selection_buttons_state()

            if results:
                self._is_idle = True
                self._set_status(
                    t(lang, "status_scan_done", path=scan_path, count=len(results))
                )
            else:
                self._is_idle = True
                self._set_status(t(lang, "status_scan_empty", path=scan_path))
                messagebox.showinfo(t(lang, "result_title"), t(lang, "result_empty"))


def run_app() -> None:
    app = DirectorySizeApp()
    app.mainloop()
