# Ordnergrößen-Scanner

**Sprache:** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

Windows-Desktop-App zum Finden von Ordnern, die eine bestimmte Größe überschreiten. Scannt direkte Unterordner, filtert nach Schwellenwert, ermöglicht Navigation, markiert Systemordner, Theme-Umschaltung und Pfad kopieren.

## Funktionen

- Scan direkter Unterordner eines beliebigen Verzeichnisses (z. B. `C:\` oder `AppData\Local`)
- Größenschwellenwert (B, KB, MB, GB)
- Ergebnisse nach Größe absteigend sortiert
- Doppelklick auf Ordner scannt dessen Unterordner
- Zurück, Pfad kopieren (Schaltfläche, Kontextmenü, Strg+C), Ordner im Explorer öffnen (Schaltfläche, Rechtsklick)
- Systemordner hervorgehoben (Windows, Program Files usw.)
- Helles und weiches dunkles Theme
- UI-Sprachen: EN, RU, ZH, ES, DE, FR, JA, PT

## Fertige EXE

Nach lokalem Build liegt die ausführbare Datei hier:

```
dist/serch_size.exe
```

Nutzer ohne Python laden `serch_size.exe` von **GitHub Releases** herunter (Datei beim Release anhängen).

Start: Doppelklick auf `serch_size.exe`. Keine Installation. Windows 10+.

Einstellungen (Theme, Sprache) werden in `%USERPROFILE%\.serch_size\settings.json` gespeichert.

## Aus Quellcode starten

```powershell
pip install -r requirements.txt
python main.py
```

## EXE selbst bauen

Option 1 — Batch-Datei:

```powershell
build.bat
```

Option 2 — manuell:

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

Ergebnis: `dist\serch_size.exe` (~25 MB).

## Voraussetzungen

- Windows 10 oder neuer
- Python 3.11+ (für Quellcode oder Build)

## Lizenz

Siehe [LICENSE](LICENSE).
