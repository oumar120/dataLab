# Plateforme d’analyse socio‑économique (Django + Angular)

Projet full‑stack pour explorer des indicateurs socio‑économiques, simuler des scénarios (projection + corrélations), et générer une interprétation par IA avec export PDF.

## Fonctionnalités

### 1) Dashboard (visualisation)
- Visualisation des séries temporelles d’un indicateur pour un pays.
- Sélection du pays, de l’indicateur et d’une plage d’années.
- Graphiques interactifs avec **ApexCharts** (via `ng-apexcharts`).

### 2) Simulateur (projection & corrélations)
- Simulation d’un scénario (% de variation) sur un **indicateur cible**.
- **Projection directe** de l’indicateur cible sur 1, 3 et 5 ans.
- **Corrélations** avec les autres indicateurs à partir des données historiques (matrice de corrélation via `pandas`).
- Identification d’indicateurs « impactés » et calcul d’une **projection indirecte** (1/3/5 ans) basée sur la corrélation.
- Envoi des résultats à une IA pour produire une **narration** (style rapport universitaire).
- Export du rapport en **PDF** via `jspdf` + `jspdf-autotable`.

### 3) Indice composite (synthèse & comparaison)
- Calcul d’un **indice synthétique** (pondéré) regroupant plusieurs indicateurs.
- Deux modes :
	- Analyse d’un seul pays sur une période (évolution annuelle de l’indice).
	- Comparaison de plusieurs pays sur une année donnée.
- Visualisation en graphique (barres) avec ApexCharts.

### 4) Données (ingestion & nettoyage)
- Script d’import de données depuis l’API **World Bank** (indicateurs + pays + séries temporelles).
- Nettoyage/sélection (ex: conservation des pays avec meilleure complétude).
- Transformation et organisation des données pour analyses (pivot, corrélations) via **pandas**.

## Stack technique

- **Frontend**: Angular (standalone components) + Tailwind (`@ngneat/tailwind`) + ApexCharts + jsPDF
- **Backend**: Django + Django REST Framework + django-cors-headers
- **Data/Analyse**: pandas
- **IA (narration)**: Groq (modèle configuré dans le code)

## Architecture du dépôt

- `back/src/` : projet Django
- `front/` : application Angular

## API (backend)

Base URL (dev): `http://localhost:8000/api`

- `GET /api/pays/` : liste des pays
- `GET /api/indicateurs/` : liste des indicateurs
- `GET /api/donnees/` : données filtrables
	- Query params: `pays`, `indicateur`, `start_year`, `end_year`
	- Exemple: `/api/donnees/?pays=SN&indicateur=SP.POP.TOTL&start_year=2010&end_year=2024`
- `GET /api/simulation/?pays=XX&i_cible=Nom%20Indicateur&scenario_pct=10` : simulation + narration IA
- `POST /api/indice/` : calcul d’indice composite + narration IA
	- Body (JSON):
		- `pays`: `string[]`
		- `indicateur`: `string[]` (noms d’indicateurs)
		- `start_year`, `end_year` (mode analyse)
		- `start_year` (utilisé comme `year` en mode comparaison)
		- `weight`: `{[nomIndicateur: string]: number}`

## Lancer en local (développement)

### Backend (Django)

Depuis `back/src/`:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 8000
```

### Frontend (Angular)

Depuis `front/`:

```bash
npm install
npm start
```

Le front appelle l’API via `front/src/app/environments/environment.ts` (par défaut `http://localhost:8000/api`).

## Configuration IA (Groq)

La narration IA utilise une clé d’API Groq.

- Définir la variable d’environnement `GROQ_API_KEY`.
	- PowerShell:
		- `setx GROQ_API_KEY "votre_cle"`
	- Linux/macOS:
		- `export GROQ_API_KEY="votre_cle"`

Si `GROQ_API_KEY` n’est pas définie, l’API renvoie une narration de remplacement (IA indisponible).

## Import/rafraîchissement des données (World Bank)

Le script `back/src/data.py` permet d’importer pays/indicateurs/données depuis l’API World Bank et d’appliquer un nettoyage.

Depuis `back/src/`:

```bash
python data.py
```

Note: le script contient plusieurs étapes commentées (import thèmes, indicateurs, pays, données, nettoyage) — activez celles dont vous avez besoin.

## Dépannage

### VS Code / Pylance: “Import 'django.db.models' could not be resolved from source”

Généralement lié à l’environnement Python :
- Sélectionner l’interpréteur du venv (`.venv`) dans VS Code.
- Installer Django et les dépendances dans cet environnement.
- Recharger la fenêtre VS Code.

## Déploiement (à containeriser)

Le projet inclut une configuration Docker pour un déploiement simple sur un VPS.

### Démarrage via Docker (local ou VPS)

Prérequis: Docker + Docker Compose.

1) Copier `.env.example` en `.env` et renseigner au minimum :
- `DJANGO_SECRET_KEY`
- `GROQ_API_KEY` (optionnel, pour la narration)

2) Lancer:

```bash
docker compose up -d --build
```

Notes:
- Le front est servi par Nginx et proxy `/api` vers le backend.
- Le backend tourne avec Gunicorn.
