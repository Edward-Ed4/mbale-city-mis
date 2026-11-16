# Mbale City Council Information System
## User Guide and Presentation Notes

**Public system:** [https://mbale-city-mis.onrender.com](https://mbale-city-mis.onrender.com)  
**Prepared for:** A non-technical presenter  
**Purpose:** Explain the system, practise its main functions, and present it clearly.

> **Important:** This is a working academic demonstration prototype. Names, telephone numbers, amounts, tickets, and registry entries shown are sample data, not verified Mbale City Council records. Do not enter real citizen, property-owner, telephone, or payment information. The portal has no user sign-in, so anyone who has the link can view and change its records. It is not an official Council service or a certified financial reporting system.

---

## 1. What the system does

The Mbale City Council Information System is a website that brings together three municipal registers:

1. **Business and trading licences** — businesses, licence numbers, owners, wards, fees, and payment status.
2. **Property and land rates** — plot numbers, owners, property types, annual rates, and payment status.
3. **Citizen service requests** — reported service problems, their locations, urgency, and progress.

The **Municipal Operations Summary** brings selected totals together on one page. Council staff can search the registers, record demonstration updates, download CSV spreadsheets, and print a dashboard summary.

### A simple way to describe it

> “This system is a shared digital register. Instead of keeping business licences, property-rate records, and citizen requests in separate paper files or spreadsheets, the prototype stores them in one database and provides a website for viewing and updating them.”

### What “database-driven” and “menu-driven” mean

- **Database-driven:** The information displayed on the site comes from stored records. When a record changes, the relevant page reads the updated information from the database.
- **Menu-driven:** The sidebar is the menu. Select a service to move between the dashboard, business licences, property rates, citizen requests, and registry records.

You do not need to understand or use programming to demonstrate the website.

---

## 2. Open the system

1. Connect the presentation laptop or phone to the internet.
2. Open [https://mbale-city-mis.onrender.com](https://mbale-city-mis.onrender.com) in a browser.
3. Wait a few seconds if the free hosting service has been inactive. Reload the page if it does not appear on the first attempt.
4. The **Municipal Operations Summary** should appear. Use the green sidebar links to open each register.

The system is hosted online. For the presentation, you only need the link and a browser; you do not need to install Python or start a local server.

### Before the presentation

- Open the website before the audience arrives and confirm that it loads.
- Check that the contact strip, Mbale City Council crest, dashboard totals, and sidebar appear.
- Keep the dashboard open in one browser tab as a fallback.
- If possible, test the internet connection and presentation screen in advance.
- Do not use the local development link `127.0.0.1`; it only works on the computer running the development server.
- Do not enter genuine personal or financial information.

---

## 3. Tour of the pages

### Municipal Operations Summary

This is the landing page. It contains four key indicators (KPI cards), a division comparison, recent activity, and links to the registers.

- **Total Revenue Collected:** Adds annual fees for business licences marked **Paid** to annual property rates marked **Cleared**.
- **Active Trading Licenses:** Counts business records whose status is **Paid**. In this prototype, “active” is a display label for that status; it is not an independent legal validation of a licence.
- **Registered Properties:** Counts all property records in the register, whether their rates are cleared or in arrears.
- **Pending Service Requests:** Counts requests whose status is **Open** or **In Progress**. Resolved requests are not included.
- **Division Overview:** Shows the number of business records, property records, and unresolved service requests for each division.
- **Recent Activity:** Shows a short list of recently logged business licences and citizen requests. It is not a full audit log.

Use **Print Official Statement** to open the browser’s print dialog for the dashboard. It prints a formatted summary; it does not create an audited, signed, or Council-certified financial statement.

### Business & Trading Licenses

The table shows the licence number, business, owner and contact, division and ward, annual fee, and status.

- Use the **division** and **status** menus, then select **Apply filters** to narrow the list.
- Use the search field to find a business by business name, owner, licence number, or phone.
- Select **Register business** to open the form. Complete all fields and choose **Save license**.
- Each new entry is assigned a licence reference by the prototype. The reference is for demonstration and does not represent an official Council-issued licence.
- Select **Edit / Renew** to change an existing sample record. Renewal here means editing the record/status; it does not process a real renewal or payment.
- Select **Delete** only during practice, and read the confirmation first.
- Select **Export CSV** to download the business register as a spreadsheet-compatible file.

### Property & Land Rates

The table shows a plot number, owner, property type, division and ward, annual rate, payment status, and last payment date.

- Search by plot number, owner, ward, or division.
- Use the status menu to show **Cleared** or **Arrears** records.
- Select **Record payment** only as a demonstration. It marks that sample record **Cleared** and gives it today’s date. It does **not** collect money, verify a receipt, contact a bank, or post a real payment.
- Select **Export CSV** to download the property register.

### Citizen Service Requests & Complaints

The table tracks reports in categories such as garbage collection, street lighting, road maintenance, and water and drainage.

- Search by ticket, citizen, category, or location; use the status menu to filter.
- Select **Log a request**, enter sample details, and save. The system assigns a ticket reference and starts the request as **Open**.
- Use **Update status** to change a ticket to **Open**, **In Progress**, or **Resolved**. The update is saved immediately.
- Select **Export CSV** to download the request register.

Logging a sample request demonstrates record keeping. It does not notify a real department or guarantee that a municipal crew will respond.

### Municipal Registry Records

This page displays the three table structures, their current row counts, and a sample of recent rows. It is a read-only view of the database design; it is not a SQL editor.

- **Restore Default Registry** deletes the current business, property, and complaint records and recreates the original sample records. Any changes made while practising will be lost.
- It does not change application code or generate verified official records.
- The displayed database connection status describes the prototype’s configured SQLite database; it is not an uptime or data-integrity certificate.

---

## 4. Understanding the sample figures

The initial demonstration registry is seeded with **9 businesses, 9 properties, and 9 citizen requests**. The sample records contain example Mbale locations such as Republic Street, Naboa Road, Pallisa Road, Kumi Road, Senior Quarters, Maluku Ward, Nkoma, Mooni, Nabuyonga, and Bugema.

The initial dashboard figures are calculated from those sample records:

| Indicator | Initial sample value | How it is calculated |
|---|---:|---|
| Total revenue collected | UGX 9,600,000 | Paid business fees (UGX 3,810,000) + cleared property rates (UGX 5,790,000) |
| Active trading licences | 5 | Business records with status “Paid” |
| Registered properties | 9 | All rows in the property register |
| Pending service requests | 7 | Open and In Progress requests; excludes Resolved |

The division breakdown starts at:

| Division | Businesses | Properties | Unresolved requests |
|---|---:|---:|---:|
| Industrial City Division | 5 | 5 | 4 |
| Northern City Division | 4 | 4 | 3 |

These are counts and sums of the **sample dataset**, not current official Mbale City Council statistics. When records are added, edited, marked paid, or restored, the dashboard totals can change.

### Why this matters to a statistics student

The dashboard illustrates basic descriptive statistics and data management:

- **Counts** summarise how many records meet a condition, such as paid licences.
- **Sums** aggregate monetary values, such as fees for paid licences.
- **Grouping** compares counts between divisions.
- **Classification** organises requests by service category, priority, and status.
- **Data quality** depends on complete, accurate, consistently entered records.

These indicators describe what is in the register. They do not by themselves prove that revenue is complete, service delivery is effective, or a change was caused by a particular policy. Real analysis would require verified records, agreed definitions, time periods, reconciliation, and appropriate oversight.

---

## 5. Suggested live demonstration

This sequence takes about **5–7 minutes**. You can present it without editing any data.

### Step 1 — Introduce the purpose (30–45 seconds)

Say:

> “This project demonstrates how a city administration could organise business licensing, property rates, and citizen service requests in connected electronic registers. I will use sample data to show the workflow; these figures are not official Council statistics.”

### Step 2 — Explain the dashboard (1 minute)

Point out the four KPI cards. Explain the revenue formula: paid licence fees plus cleared property rates. Mention that pending requests include open and in-progress tickets. Briefly compare the two division rows.

### Step 3 — Show business licensing (1 minute)

Open **Business Licenses**. Filter by one division or status and use the search box. Point to a licence reference, owner, ward, fee, and payment status. Mention that **Export CSV** can provide a spreadsheet copy.

### Step 4 — Show property rates (1 minute)

Open **Property Rates**. Filter for **Arrears** and point out the plot, location, and assessed annual rate. Explain that **Record payment** simulates a status update only; it is not a payment system.

### Step 5 — Show citizen service requests (1–2 minutes)

Open **Citizen Requests**. Search for a location or category and explain the ticket’s priority and status. If time allows, log a clearly fictional request such as “Presentation Practice Report” at “Sample location” using your own invented contact value. Do not use anyone’s real phone number or personal details. Explain that status progresses from **Open** to **In Progress** and then **Resolved**.

If you change a record, use **Restore Default Registry** afterward only if you intend to erase all practice changes and reset the entire registry.

### Step 6 — Close with limitations and next steps (30–45 seconds)

Say:

> “This prototype demonstrates the workflow and reporting concept. Before operational use, it would need authenticated staff accounts, verified Council data, persistent storage, backups, audit trails, privacy controls, and integration with approved payment and service workflows.”

---

## 6. Short presentation script

Adapt this wording to your own presentation style:

> “Good morning. My project is the Mbale City Council Information System, a database-driven municipal information portal. Its purpose is to demonstrate how three types of records—business trading licences, property rates, and citizen service requests—can be organised and viewed through one menu-driven website.
>
> The Municipal Operations Summary provides a quick overview. Its indicators are calculated from the records currently in the system. For example, the revenue figure adds annual business fees marked paid to property rates marked cleared. The division table lets us compare the number of records and unresolved requests between divisions.
>
> The business register supports searching, filtering, registration, editing, and CSV export. The property register displays plots, annual rates, and payment status. The citizen-request register assigns a ticket and allows its status to be followed from open through in progress to resolved.
>
> From a statistics perspective, the system demonstrates descriptive summaries, grouping by division, and classification by status and service category. The usefulness of every summary depends on the quality and verification of the underlying records.
>
> The records shown today are sample data for demonstration, not official Council statistics. This prototype does not process real payments, assign municipal work, or provide staff authentication. Further work would be needed for secure operational use, persistent and backed-up storage, verified data, and formal audit and privacy controls. Thank you.”

---

## 7. Likely questions and clear answers

**Is this an official Mbale City Council system?**  
No. It is an academic demonstration prototype designed around a municipal information-system use case. It is not affiliated with or certified by Mbale City Council.

**Are the displayed names, amounts, or totals official?**  
No. They are illustrative sample records. The dashboard calculations are real calculations over those sample rows, but the resulting totals are not official Council statistics.

**How does the system calculate revenue?**  
It sums the annual fees of business records marked Paid and adds the annual rates of property records marked Cleared. It does not include pending, expired, or arrears amounts as collected revenue.

**Does “Record payment” take money?**  
No. It only changes a sample property’s payment status and records today’s date. There is no bank, mobile-money, receipt, or payment-gateway connection.

**Does logging a complaint send it to Council staff?**  
No. It creates a record in this demonstration system. There is no notification, dispatch, or integration with an actual Council department.

**Can it be used by multiple staff?**  
The hosted website can be opened by multiple visitors, but it has no login, user roles, or record ownership. It should not be used for confidential or operational data.

**Will the sample data always remain?**  
Not guaranteed. The service is hosted on Render’s free tier, whose local storage can be reset when the service restarts or redeploys. The reset button also replaces current rows with the default sample set.

**What does CSV export do?**  
It downloads the corresponding register into a file that spreadsheet software can open. Check the file contents before sharing it. Do not distribute personal data.

**What would be needed before real deployment?**  
At minimum: Council approval and requirements validation, staff authentication and roles, verified data, privacy/security review, a persistent managed database, backups, audit logs, error monitoring, reconciliation of financial data, and integrations tested by authorised teams.

---

## 8. Trouble during the presentation

- **The link is slow or initially blank:** Wait a little, then reload once. Free hosting may need to wake up after inactivity.
- **The internet is unavailable:** Use pre-approved screenshots or a screen recording if available. Do not claim the live system is working offline; the hosted system needs internet.
- **A number differs from this guide:** Someone may have edited a sample record, or the host may have reset its sample data. Explain that dashboard figures are calculated from the current records. Use **Restore Default Registry** only if you are prepared to replace all rows with the sample set.
- **A form change does not save:** Check that required fields are filled and select values from the provided lists. Refresh the page to obtain a fresh form if it reports an expired session.
- **You cannot find a record:** Clear the search text and filters, then search again.
- **The browser print window appears:** Select a printer or “Save to PDF,” check the preview, and cancel if you did not intend to print.

---

## 9. Quick reference

- **Live website:** [mbale-city-mis.onrender.com](https://mbale-city-mis.onrender.com)
- **Dashboard:** Municipal Operations Summary
- **Business register:** Business Licenses
- **Property register:** Property Rates
- **Citizen request register:** Citizen Requests
- **Table details and sample reset:** Registry Records
- **Printable dashboard:** Print Official Statement
- **Spreadsheet downloads:** Export CSV on the business, property, and request pages
- **Use only:** Sample data and invented presentation entries
- **Never enter:** Real personal details, real phone numbers, real property-owner information, or actual financial records
