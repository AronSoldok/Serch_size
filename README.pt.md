# Scanner de tamanho de pastas

**Idioma:** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

Aplicativo Windows para encontrar pastas que excedem um tamanho definido. Varre subpastas diretas, filtra por limite, permite navegar, marca pastas do sistema, alterna tema e copia caminhos.

## Recursos

- Varredura de subpastas diretas de qualquer diretório (ex.: `C:\` ou `AppData\Local`)
- Limite de tamanho (B, KB, MB, GB)
- Resultados ordenados por tamanho (maior primeiro)
- Duplo clique em uma pasta para varrer suas subpastas
- Voltar, copiar caminho (botão, menu de contexto, Ctrl+C), abrir pasta no Explorer (botão, botão direito)
- Pastas do sistema destacadas (Windows, Program Files, etc.)
- Tema claro e escuro suave
- Idiomas da interface: EN, RU, ZH, ES, DE, FR, JA, PT

## EXE pronto

Após compilar localmente, o executável fica em:

```
dist/serch_size.exe
```

Para usuários sem Python, baixe `serch_size.exe` em **GitHub Releases** (anexe o arquivo ao publicar uma release).

Execução: duplo clique em `serch_size.exe`. Sem instalação. Windows 10+.

As configurações (tema, idioma) ficam em `%USERPROFILE%\.serch_size\settings.json`.

## Executar a partir do código-fonte

```powershell
pip install -r requirements.txt
python main.py
```

## Compilar o EXE

Opção 1 — arquivo batch:

```powershell
build.bat
```

Opção 2 — manual:

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

Resultado: `dist\serch_size.exe` (~25 MB).

## Requisitos

- Windows 10 ou superior
- Python 3.11+ (para executar ou compilar)

## Licença

Consulte [LICENSE](LICENSE).
