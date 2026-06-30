# Directory Size Scanner

**Language:** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

A Windows desktop app to find folders that exceed a specified size. Scan immediate subfolders, filter by threshold, drill down into directories, mark system folders, switch themes, and copy paths.

## Features

- Scan direct subfolders of any directory (e.g. `C:\` or `AppData\Local`)
- Set a size threshold (B, KB, MB, GB)
- Results sorted by size (largest first)
- Double-click a folder to scan its subfolders
- Back navigation, copy path (button, right-click, Ctrl+C), open folder in Explorer (button, right-click)
- System folders highlighted (Windows, Program Files, etc.)
- Light and soft dark theme
- UI languages: EN, RU, ZH, ES, DE, FR, JA, PT

## Ready-made EXE

After building locally, the executable is here:

```
dist/serch_size.exe
```

For users without Python, download `serch_size.exe` from **GitHub Releases** (attach the file when publishing a release).

Run: double-click `serch_size.exe`. No installation required. Windows 10+.

Settings (theme, language) are stored in `%USERPROFILE%\.serch_size\settings.json`.

## Run from source

```powershell
pip install -r requirements.txt
python main.py
```

## Build EXE yourself

Option 1 — run the batch file:

```powershell
build.bat
```

Option 2 — manual steps:

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

Output: `dist\serch_size.exe` (~25 MB).

## Requirements

- Windows 10 or later
- Python 3.11+ (for running from source or building)

## License

See [LICENSE](LICENSE).
