# Mbale City Sanitation Analytics — Quick Reference

## Run locally

1. Activate the project virtual environment.
2. Run `python app.py`.
3. Open `http://127.0.0.1:5000`.

The application creates `mbale_city.db` beside `database.py`.

## Dashboard

- **Analytics Overview:** city benchmark KPIs, ward coverage chart, vulnerability comparison, lowest-coverage priority list.
- **Ward Data & Surveys:** search/filter, add, edit, or delete a survey record; update improved household counts; coverage and risk are calculated automatically; export CSV.
- **Vulnerability Simulator:** select a seeded ward to load its average household size and unemployment rate, or adjust the sliders manually; predicted access, gap, and risk recalculate live.
- **Intervention Tracker:** add or delete programmes and update coverage and status.
- **Database & CSV Export:** inspect SQLite schemas and download registers/model summaries.

## Reported benchmark values

- City sanitation coverage: **59.85%**
- Unimproved sanitation gap: **40.18%**
- Beta regression: household size `-0.6479` (SE `0.2188`, p `0.003`); unemployment `-0.0235` (SE `0.0098`, p `0.017`); constant `3.3527` (SE `0.8323`, p `0.000`)
- Model fit: `N = 58`, `LR chi2 = 19.29`, `p = 0.0001`, log-likelihood `17.05433`

The benchmark figures and regression are displayed as reported values. The register contains the 58 ward records from the supplied `dashboard-1.pdf`, including household totals, improved and unimproved sanitation counts, average household size, unemployment rate, and population. Coverage is calculated from improved counts divided by total households. The vulnerability tier is **High** below 40%, **Medium** from 40% through 60%, and **Low** above 60%. The source does not identify a primary vulnerable group for each ward, so the register labels that field as not specified.

## Hosting note

Render's free service uses an ephemeral filesystem. SQLite changes may be lost after a restart or redeploy. Use persistent managed storage and access controls before entering real administrative data.
