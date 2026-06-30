from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from i18n import DEFAULT_LANG, t, unit_multipliers

ProgressCallback = Callable[[int, int, str], None]

SYSTEM_FOLDER_NAMES = frozenset(
    {
        "Windows",
        "System32",
        "SysWOW64",
        "Program Files",
        "Program Files (x86)",
        "ProgramData",
        "$Recycle.Bin",
        "System Volume Information",
        "Recovery",
        "WinSxS",
        "Config.Msi",
        "MSOCache",
        "PerfLogs",
    }
)
SYSTEM_FOLDER_NAMES_FOLDED = frozenset(name.casefold() for name in SYSTEM_FOLDER_NAMES)

MAX_SCAN_WORKERS = min(8, os.cpu_count() or 4)


@dataclass
class FolderResult:
    path: Path
    size_bytes: int
    is_system: bool = False


def is_system_folder(path: Path) -> bool:
    return path.name.casefold() in SYSTEM_FOLDER_NAMES_FOLDED


def get_folder_size(path: Path) -> int:
    total = 0
    stack = [os.fspath(path)]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                        elif entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                    except OSError:
                        continue
        except OSError:
            continue
    return total


def _scan_subdir_size(subdir: Path) -> tuple[Path, int | None]:
    try:
        return subdir, get_folder_size(subdir)
    except OSError:
        return subdir, None


def scan_immediate_subdirs(
    root: Path,
    min_bytes: int,
    on_progress: ProgressCallback | None = None,
    cancel_event=None,
) -> list[FolderResult]:
    try:
        subdirs = sorted(p for p in root.iterdir() if p.is_dir())
    except OSError:
        return []

    results: list[FolderResult] = []
    total = len(subdirs)
    if total == 0:
        return results

    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_SCAN_WORKERS) as executor:
        futures = {executor.submit(_scan_subdir_size, subdir): subdir for subdir in subdirs}
        for future in as_completed(futures):
            if cancel_event is not None and cancel_event.is_set():
                for pending in futures:
                    pending.cancel()
                break

            subdir, size = future.result()
            completed += 1

            if on_progress is not None:
                on_progress(completed, total, subdir.name)

            if size is None:
                continue

            if size >= min_bytes:
                results.append(
                    FolderResult(
                        path=subdir,
                        size_bytes=size,
                        is_system=is_system_folder(subdir),
                    )
                )

    results.sort(key=lambda item: item.size_bytes, reverse=True)
    return results


def parse_size_threshold(value: float, unit: str, lang: str = DEFAULT_LANG) -> int:
    multiplier = unit_multipliers(lang).get(unit.strip())
    if multiplier is None:
        raise ValueError(t(lang, "err_unknown_unit", unit=unit))
    if value <= 0:
        raise ValueError(t(lang, "err_threshold_zero"))
    return int(value * multiplier)


def format_size(size_bytes: int, lang: str = DEFAULT_LANG) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} {t(lang, 'unit_b')}"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} {t(lang, 'unit_kb')}"
    if size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} {t(lang, 'unit_mb')}"
    return f"{size_bytes / 1024**3:.2f} {t(lang, 'unit_gb')}"
