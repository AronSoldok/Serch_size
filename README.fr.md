# Analyseur de taille de dossiers

**Langue :** [English](README.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [Português](README.pt.md)

Application Windows pour trouver les dossiers dépassant une taille donnée. Analyse les sous-dossiers directs, filtre par seuil, permet de naviguer, marque les dossiers système, change le thème et copie les chemins.

## Fonctionnalités

- Analyse des sous-dossiers directs d’un répertoire (ex. `C:\` ou `AppData\Local`)
- Seuil de taille (o, Ko, Mo, Go)
- Résultats triés par taille décroissante
- Double-clic sur un dossier pour analyser ses sous-dossiers
- Retour, copier le chemin (bouton, menu contextuel, Ctrl+C), ouvrir le dossier dans l'Explorateur (bouton, clic droit)
- Dossiers système mis en évidence (Windows, Program Files, etc.)
- Thème clair et sombre doux
- Langues de l’interface : EN, RU, ZH, ES, DE, FR, JA, PT

## EXE prêt à l’emploi

Après compilation locale, l’exécutable se trouve ici :

```
dist/serch_size.exe
```

Pour les utilisateurs sans Python, téléchargez `serch_size.exe` depuis **GitHub Releases** (joignez le fichier lors d’une release).

Lancement : double-clic sur `serch_size.exe`. Aucune installation. Windows 10+.

Les paramètres (thème, langue) sont enregistrés dans `%USERPROFILE%\.serch_size\settings.json`.

## Exécution depuis les sources

```powershell
pip install -r requirements.txt
python main.py
```

## Compiler l’EXE vous-même

Option 1 — fichier batch :

```powershell
build.bat
```

Option 2 — manuel :

```powershell
pip install -r requirements-build.txt
pyinstaller --noconfirm build.spec
```

Résultat : `dist\serch_size.exe` (~25 Mo).

## Prérequis

- Windows 10 ou ultérieur
- Python 3.11+ (pour exécuter ou compiler)

## Licence

Voir [LICENSE](LICENSE).
