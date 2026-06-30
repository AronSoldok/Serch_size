# フォルダサイズスキャナー

**言語：** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

指定サイズを超えるフォルダを探す Windows デスクトップアプリ。直下のサブフォルダをスキャンし、閾値でフィルタ、フォルダ内へ移動、システムフォルダの表示、テーマ切替、パスコピーに対応。

## 機能

- 任意のディレクトリの直下サブフォルダをスキャン（例：`C:\` や `AppData\Local`）
- サイズ閾値（B、KB、MB、GB）
- サイズの大きい順に表示
- フォルダをダブルクリックでそのサブフォルダをスキャン
- 戻る、パスをコピー（ボタン、右クリック、Ctrl+C）、エクスプローラーでフォルダを開く（ボタン、右クリック）
- システムフォルダを強調表示（Windows、Program Files など）
- ライトテーマとソフトダークテーマ
- UI 言語：EN、RU、ZH、ES、DE、FR、JA、PT

## ビルド済み EXE

ローカルビルド後、実行ファイルは次の場所にあります：

```
dist/serch_size.exe
```

Python がないユーザーは **GitHub Releases** から `serch_size.exe` をダウンロードしてください（リリース公開時にファイルを添付）。

起動：`serch_size.exe` をダブルクリック。インストール不要。Windows 10 以降。

設定（テーマ、言語）は `%USERPROFILE%\.serch_size\settings.json` に保存されます。

## ソースから実行

```powershell
pip install -r requirements.txt
python main.py
```

## EXE を自分でビルド

方法 1 — バッチファイル：

```powershell
build.bat
```

方法 2 — 手動：

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

出力：`dist\serch_size.exe`（約 25 MB）。

## 要件

- Windows 10 以降
- Python 3.11+（ソース実行またはビルド時）

## ライセンス

[LICENSE](LICENSE) を参照。
