# Escáner de tamaño de carpetas

**Idioma:** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

Aplicación de escritorio para Windows que encuentra carpetas que superan un tamaño indicado. Escanea subcarpetas directas, filtra por umbral, permite profundizar, marca carpetas del sistema, cambia el tema y copia rutas.

## Funciones

- Escaneo de subcarpetas directas de cualquier directorio (p. ej. `C:\` o `AppData\Local`)
- Umbral de tamaño (B, KB, MB, GB)
- Resultados ordenados por tamaño (mayor primero)
- Doble clic en una carpeta para escanear sus subcarpetas
- Atrás, copiar ruta (botón, menú contextual, Ctrl+C), abrir carpeta en el Explorador (botón, clic derecho)
- Carpetas del sistema resaltadas (Windows, Program Files, etc.)
- Tema claro y oscuro suave
- Idiomas de la interfaz: EN, RU, ZH, ES, DE, FR, JA, PT

## EXE listo para usar

Tras compilar localmente, el ejecutable está en:

```
dist/serch_size.exe
```

Para usuarios sin Python, descargue `serch_size.exe` desde **GitHub Releases** (adjunte el archivo al publicar una versión).

Ejecución: doble clic en `serch_size.exe`. Sin instalación. Windows 10+.

La configuración (tema, idioma) se guarda en `%USERPROFILE%\.serch_size\settings.json`.

## Ejecutar desde el código fuente

```powershell
pip install -r requirements.txt
python main.py
```

## Compilar el EXE usted mismo

Opción 1 — archivo por lotes:

```powershell
build.bat
```

Opción 2 — manual:

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

Resultado: `dist\serch_size.exe` (~25 MB).

## Requisitos

- Windows 10 o posterior
- Python 3.11+ (para ejecutar desde fuente o compilar)

## Licencia

Véase [LICENSE](LICENSE).
