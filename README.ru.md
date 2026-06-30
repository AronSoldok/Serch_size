# Сканер размера папок

**Язык:** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

Windows-приложение для поиска папок, превышающих заданный размер. Сканирует прямые подпапки, фильтрует по порогу, позволяет углубляться в каталоги, помечает системные папки, переключать тему и копировать пути.

## Возможности

- Сканирование прямых подпапок любой директории (например, `C:\` или `AppData\Local`)
- Порог размера (Б, КБ, МБ, ГБ)
- Результаты по убыванию размера
- Двойной щелчок — сканирование подпапок выбранной папки
- Кнопка «Назад», копирование пути (кнопка, контекстное меню, Ctrl+C), открытие папки в проводнике (кнопка, ПКМ)
- Подсветка системных папок (Windows, Program Files и т.д.)
- Светлая и мягкая тёмная тема
- Языки интерфейса: EN, RU, ZH, ES, DE, FR, JA, PT

## Готовый EXE

После локальной сборки исполняемый файл находится здесь:

```
dist/serch_size.exe
```

Для пользователей без Python скачайте `serch_size.exe` из **GitHub Releases** (прикрепите файл при публикации релиза).

Запуск: двойной щелчок по `serch_size.exe`. Установка не требуется. Windows 10+.

Настройки (тема, язык) сохраняются в `%USERPROFILE%\.serch_size\settings.json`.

## Запуск из исходников

```powershell
pip install -r requirements.txt
python main.py
```

## Сборка EXE самостоятельно

Вариант 1 — batch-файл:

```powershell
build.bat
```

Вариант 2 — вручную:

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

Результат: `dist\serch_size.exe` (~25 МБ).

## Требования

- Windows 10 или новее
- Python 3.11+ (для запуска из исходников или сборки)

## Лицензия

См. [LICENSE](LICENSE).
