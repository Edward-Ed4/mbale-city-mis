# Mbale City Sanitation Analytics

Flask and SQLite dashboard for sanitation coverage analytics, ward survey records, beta-regression prediction, intervention tracking, and CSV export.

The city coverage KPI (59.85%), unimproved gap KPI (40.18%), and beta-regression coefficients are fixed reported benchmarks. The ward register is seeded with the 58 ward-level records from the supplied `dashboard-1.pdf`; sanitation percentages are calculated from improved counts and total households, and vulnerability tiers use the 40%/60% thresholds.

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder and create/activate a virtual environment:
   - Windows PowerShell: `py -m venv .venv` then `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the website: `python app.py`
5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

SQLite is stored beside `database.py` at `mbale_city.db`. The schema is initialized automatically. On its first startup with the updated schema, the application replaces the previous generated sample ward rows with the 58 source records and preserves unrelated custom ward records. Counts, average household size, unemployment, and population are included in the ward register, CSV export, and ward-backed simulator. Risk tiers are assigned automatically: **High** below 40%, **Medium** from 40% through 60%, and **Low** above 60%. The source includes an open-defecation count so that improved, unimproved, and open-defecation counts reconcile to total households.

The optional terminal menu uses the same database: `python cli_menu.py`.

## Deploy to Render

1. Connect the GitHub repository `Edward-Ed4/mbale-city-mis` to Render as a Blueprint.
2. Let Render read `render.yaml`, then create/deploy the service.
3. Open the `onrender.com` address shown on the service page.

Render's free service uses an ephemeral filesystem. A restart or deployment can lose SQLite changes; startup restores the 58 source ward records. Use a persistent disk or managed database and a backup plan if edits must survive deployments. A public instance should not be used for real citizen or household information until authentication, access controls, secure storage, and operational data governance are implemented.

## PythonAnywhere

Deploy this Flask application using a PythonAnywhere web app configured with `wsgi.py`/`app:app`, or follow the platform's current Flask setup instructions. Ensure the project directory is writable if SQLite changes must persist. Back up the database before replacing code or changing hosting configuration.

## Dashboard modules

- **Analytics Overview** — coverage KPIs, database-driven ward charts, division comparison, and priority records.
- **Ward Data & Surveys** — instant search and filters, add/edit/delete survey records, sanitation counts and demographic measures, automatically calculated coverage and vulnerability, CSV export.
- **Vulnerability Simulator** — interactive inverse-logit prediction using the displayed beta-regression coefficients; select a seeded ward to load its household size and unemployment rate.
- **Intervention Tracker** — add/edit/delete programmes, coverage progress, and status updates.
- **Database & CSV Export** — SQLite schemas, row counts, sample rows, and downloadable CSV files.

Every page offers a print action. CSV exports are available for the ward register, model results, interventions, and database data dictionary.
