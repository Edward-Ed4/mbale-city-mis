# User Guide and Presentation Notes

## What this system is

The Mbale City Sanitation Monitoring Portal is an academic prototype that presents the research topic **“Statistical Analysis of Sanitation Inequalities in Mbale City: A Data-Driven Sanitation Monitoring Dashboard for Evidence-Based Decision-Making.”** It is designed to demonstrate how statistics can help describe sanitation gaps, examine associations, and inform questions for better-targeted interventions.

The dashboard is not an official Mbale City Council service and does not process or verify sanitation reports. It does not collect household surveys or calculate the beta regression from raw observations. The regression results shown are transcribed from the presentation.

## Read this data note before presenting

The slides cite the Bugisu Sub-region Census 2024 Profile Report and report citywide figures of **59.85% improved sanitation** and **40.18% unimproved sanitation**. Confirm the values in the original report before submitting formal academic work. Their sum is 100.03%, likely because of rounding or source reporting.

The slides report a beta regression using **58 ward observations**. All ward-level register values in this prototype—including household counts, sanitation percentages, vulnerability classifications, and some area labels—are generated illustrative examples, not UBOS ward-level estimates. Intervention target wards, agency assignments, and status values are also illustrative.

Be transparent: introduce the register as a demonstration interface, not as measured census results. Replace the illustrative data with a validated dataset before interpreting local ward rankings or recommending a real resource allocation.

## Using the portal

Open the shared website link or, if running locally, open `http://127.0.0.1:5000`. Use the numbered menu on the left. On a phone, use the menu button at the top to open navigation. Each page has a **Print** action; the relevant pages also provide a **CSV export** suitable for opening in spreadsheet or statistical software.

### 1. Overview & Problem Statement

Start here. The headline communicates the presentation's core message: roughly four in ten households lack improved sanitation. The KPI cards show the reported citywide benchmark, the reported gap, the 58 observations described in the slides, and the 14 illustrative high-vulnerability register labels.

Explain the health, environmental, privacy/dignity, and climate-resilience consequences. The division summary is computed from synthetic demo rows; do not describe it as a census estimate.

### 2. Ward-Level Sanitation Register

Use the search field to find a ward label or vulnerable group. Division and vulnerability menus can narrow the visible rows; select **Apply filters** to update the table. **Export CSV** downloads the register for spreadsheet, R, or SPSS use. The export contains illustrative values and must not be used as observed study data.

### 3. Statistical Beta Regression Model

The table reproduces the reported estimates:

| Variable | Coefficient | Standard error | p-value |
|---|---:|---:|---:|
| Household size | -0.6479 | 0.2188 | 0.003 |
| Unemployment | -0.0235 | 0.0098 | 0.017 |
| Constant | 3.3527 | 0.8323 | 0.000 |

The presentation also reports 58 ward observations, LR chi-square 19.29, model p-value 0.0001, and log likelihood 17.05433.

In plain language, the two explanatory-variable coefficients are negative, and the reported p-values are below 0.05. In this fitted model, household size and unemployment are statistically associated with lower modeled sanitation access. This does **not** prove that either factor causes lower access. The coefficient scale, variable definitions, model diagnostics, and original statistical output should be checked before interpreting the size of effects. A displayed p-value of `0.000` is rounded, not literally zero.

### 4. Interventions & Gap Analysis

This page lists the programme categories and gaps from the presentation: uneven coverage across wards; limited monitoring of sustained behaviour change; fragmented information/reporting; limited household follow-up; and inadequate maintenance/monitoring. The prototype programme-to-ward assignments, agencies, and statuses are examples, not verified current programme records.

Use the prompts to explain a possible evidence-informed workflow: validate the data, compare geographic need and programme coverage, then agree on indicators and follow-up responsibilities with the relevant authorities and partners.

### 5. Census Data Explorer

Inspect the two sanitation tables, their column structures, row counts, and sample values. The CSV button downloads a compact data dictionary. This page displays the SQLite connection status; it does not establish that the seeded rows are official census data.

## Suggested five-minute presentation

1. **Introduction (30 seconds):** “This prototype demonstrates how ward-level statistics can help make sanitation inequalities visible and support evidence-informed planning in Mbale City.”
2. **Problem and context (45 seconds):** State the presentation's reported 59.85% improved-sanitation figure and 40.18% gap. Mention the public-health, environmental, dignity, and flood-related risks.
3. **Dashboard tour (60 seconds):** Show the overview cards and make clear the division chart uses illustrative entries.
4. **Ward register (60 seconds):** Search for Namatala, show the filters and CSV download, and explicitly explain that its generated ward-level values are examples awaiting validated UBOS data.
5. **Model (75 seconds):** Explain the negative coefficients, p-values below 0.05, and the distinction between association and causation.
6. **Interventions and close (45 seconds):** Connect the programme categories to the monitoring gaps. Close with the presentation message: better statistics can support better targeting and sanitation outcomes—once the data are verified.

## Likely questions

**Are the ward-level percentages official UBOS data?**

No. The register entries are illustrative examples and clearly labeled as such.

**Did the dashboard calculate the regression?**

No. It displays the coefficient and model-fit values transcribed from the slides. Re-estimation requires the source observations, variable definitions, and model specification.

**Does a significant result prove household size or unemployment causes poor sanitation?**

No. Statistical significance indicates evidence of association under the fitted model assumptions. It does not by itself establish causality.

**Why do 59.85% and 40.18% add up to more than 100%?**

The displayed values add to 100.03%. This may reflect rounding or reporting in the cited source. Check the original census report and its definitions before drawing a conclusion.

**Can decision-makers use this version to allocate funds?**

Not yet. They would first need validated ward-level data, confirmed ward boundaries and indicators, verified programme records, appropriate analysis, and review by the responsible authorities.

**Will changes persist on the hosted free service?**

Render's free filesystem is ephemeral, so local SQLite changes can be lost when the service restarts or redeploys. The current sanitation sample tables are seeded again only if empty. Persistent operational data requires durable managed storage and backups.

## Helpful presentation tips

- Use the **Print** button to print the current page or choose “Save as PDF” in the browser's print dialog.
- Use a CSV export only as a demonstration dataset until the source data has been validated.
- Avoid entering personal or household information; this prototype has no login.
- If hosting is asleep, allow a short time for the free service to wake up and reload the page.
