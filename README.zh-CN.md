# 目录大小扫描器

**语言：** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

Windows 桌面应用，用于查找超过指定大小的文件夹。扫描直接子文件夹、按阈值筛选、深入目录、标记系统文件夹、切换主题并复制路径。

## 功能

- 扫描任意目录的直接子文件夹（如 `C:\` 或 `AppData\Local`）
- 设置大小阈值（B、KB、MB、GB）
- 结果按大小降序排列
- 双击文件夹可扫描其子文件夹
- 返回、复制路径（按钮、右键菜单、Ctrl+C）、在资源管理器中打开文件夹（按钮、右键）
- 高亮系统文件夹（Windows、Program Files 等）
- 浅色与柔和深色主题
- 界面语言：EN、RU、ZH、ES、DE、FR、JA、PT

## 现成 EXE

本地构建后，可执行文件位于：

```
dist/serch_size.exe
```

没有 Python 的用户可从 **GitHub Releases** 下载 `serch_size.exe`（发布版本时请附上该文件）。

运行：双击 `serch_size.exe`，无需安装。Windows 10 及以上。

设置（主题、语言）保存在 `%USERPROFILE%\.serch_size\settings.json`。

## 从源码运行

```powershell
pip install -r requirements.txt
python main.py
```

## 自行构建 EXE

方式 1 — 运行批处理：

```powershell
build.bat
```

方式 2 — 手动：

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

输出：`dist\serch_size.exe`（约 25 MB）。

## 系统要求

- Windows 10 或更高版本
- Python 3.11+（从源码运行或构建时需要）

## 许可证

见 [LICENSE](LICENSE)。
