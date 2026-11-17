# Mbale City Sanitation Monitoring Portal

An academic dashboard prototype for **Statistical Analysis of Sanitation Inequalities in Mbale City: A Data-Driven Sanitation Monitoring Dashboard for Evidence-Based Decision-Making**. It presents the citywide sanitation figures and beta-regression results reported in the supplied presentation, along with a searchable ward register, intervention/gap analysis, CSV exports, and a SQLite data explorer.

Read [USER_GUIDE_AND_PRESENTATION.md](./USER_GUIDE_AND_PRESENTATION.md) for a non-technical page tour and presentation script.

## Important data limitations

- The presentation cites the Bugisu Sub-region Census 2024 Profile Report and reports citywide improved sanitation of **59.85%** and unimproved sanitation of **40.18%**. Verify these against the original publication before formal academic or policy use; the displayed percentages differ from 100% by 0.03 points due to source rounding/reporting.
- The presentation reports a beta regression based on 58 ward observations but does not include its ward-level source data or full model specification.
- The seeded ward names beyond the examples supplied, household counts, ward percentages, vulnerability groups, division assignments, and intervention assignments/statuses are **illustrative demonstration data**, not UBOS ward estimates or verified programme records.
- This prototype has no login or access control. Do not enter real personal, household, or sensitive administrative data.

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder and create/activate a virtual environment:
   - Windows PowerShell: `py -m venv .venv` then `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the website: `python app.py`
5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

SQLite is stored beside `database.py` at `mbale_city.db`. The schema is initialized automatically, and the 58 illustrative ward rows and five example intervention rows are inserted only when their respective tables are empty. Starting the app again does not overwrite existing rows.

The optional terminal menu uses the same database: `python cli_menu.py`.

## Deploy to Render

1. Connect the GitHub repository `Edward-Ed4/mbale-city-mis` to Render as a Blueprint.
2. Let Render read `render.yaml`, then create/deploy the service.
3. Open the `onrender.com` address shown on the service page.

Render's free service uses an ephemeral filesystem. A restart or deployment can lose SQLite changes; startup then creates fresh illustrative rows. Use a persistent disk or managed database and a backup plan if records must survive deployments. A public instance should not be used for real citizen or household information until authentication, access controls, secure storage, and operational data governance are implemented.

## PythonAnywhere

Deploy this Flask application using a PythonAnywhere web app configured with `wsgi.py`/`app:app`, or follow the platform's current Flask setup instructions. Ensure the project directory is writable if SQLite changes must persist. Back up the database before replacing code or changing hosting configuration.

## Dashboard modules

1. **Overview & Problem Statement** — citywide headline, reported benchmark figures, research purpose, and consequences.
2. **Ward-Level Sanitation Register** — searchable/filterable illustrative rows and CSV export.
3. **Statistical Beta Regression Model** — coefficients, standard errors, p-values, fit statistics, and interpretation notes.
4. **Interventions & Gap Analysis** — programme categories and the monitoring gaps from the presentation.
5. **Census Data Explorer** — SQLite table schemas, row counts, sample records, and data-dictionary CSV.

Every page offers a print action. CSV exports are available for the ward register, model results, interventions, and database data dictionary.
