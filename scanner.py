from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[int, int, str], None]

SIZE_UNITS = {
    "Б": 1,
    "КБ": 1024,
    "МБ": 1024**2,
    "ГБ": 1024**3,
}

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


@dataclass
class FolderResult:
    path: Path
    size_bytes: int
    is_system: bool = False


def is_system_folder(path: Path) -> bool:
    return path.name.casefold() in SYSTEM_FOLDER_NAMES_FOLDED


def get_folder_size(path: Path) -> int:
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path, followlinks=False):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
    return total


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

    for index, subdir in enumerate(subdirs, start=1):
        if cancel_event is not None and cancel_event.is_set():
            break

        if on_progress is not None:
            on_progress(index, total, subdir.name)

        try:
            size = get_folder_size(subdir)
        except OSError:
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


def parse_size_threshold(value: float, unit: str) -> int:
    multiplier = SIZE_UNITS.get(unit.strip())
    if multiplier is None:
        raise ValueError(f"Неизвестная единица измерения: {unit}")
    if value <= 0:
        raise ValueError("Порог должен быть больше нуля")
    return int(value * multiplier)


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} КБ"
    if size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} МБ"
    return f"{size_bytes / 1024**3:.2f} ГБ"
