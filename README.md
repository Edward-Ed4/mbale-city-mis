# Mbale City Council Information System

A civic information portal for Mbale City Council, with municipal operations reporting and registers for business licences, property rates, and citizen service requests. The web portal and standalone terminal menu use the same SQLite demonstration registry.

For a non-technical walkthrough, explanation of dashboard figures, presentation script, and question guide, read [USER_GUIDE_AND_PRESENTATION.md](./USER_GUIDE_AND_PRESENTATION.md).

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in `mbale-city-mis` and create/activate a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the website: `python app.py`
5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The database is created and seeded automatically beside `app.py`.

To use the terminal menu in another terminal, activate the same environment and run `python cli_menu.py`.

## PythonAnywhere free tier (about 3 minutes)

1. Create a free account at PythonAnywhere, open **Consoles → Bash**, clone/upload this folder, then `cd` into `mbale-city-mis`.
2. Install packages: `pip3 install --user -r requirements.txt`.
3. Open **Web → Add a new web app → Manual configuration** and choose the matching Python version. In **WSGI configuration file**, replace its contents with `import sys`, `sys.path.insert(0, '/home/YOUR_USERNAME/mbale-city-mis')`, then `from app import app as application` (replace `YOUR_USERNAME` with your account name).
4. In the web app **Virtualenv** field, set `/home/YOUR_USERNAME/.virtualenvs/mbale-mis` only if you created that virtualenv; otherwise leave it blank if packages were installed with `--user`.
5. Click **Reload** and open the provided `YOUR_USERNAME.pythonanywhere.com` address. The SQLite file is stored next to `database.py`; keep that directory writable and persistent.

## Render deployment

1. Sign in or create an account at [Render](https://render.com/).
2. In the Render dashboard, choose **New → Blueprint** and connect the GitHub repository `Edward-Ed4/mbale-city-mis`. If prompted, authorize Render to access that repository.
3. Render reads `render.yaml` and shows the service settings. Choose **Apply** to create and deploy the free web service.
4. Wait for the deploy to finish, then open the `onrender.com` URL shown on the service page. Share that link with the person demonstrating the system.

The service uses Gunicorn, checks the dashboard health endpoint, generates a `SECRET_KEY`, and automatically deploys later pushes to the connected branch. Render's free service may take a short time to wake up after inactivity.

**Demo data only:** the included SQLite database is seeded automatically, but Render's free filesystem is ephemeral and can be reset when the service restarts or is redeployed. The prototype also has no sign-in screen, so anyone with the public URL can view and change its demo records. Do not enter real citizen, owner, phone, or financial information. For ongoing use, add authentication and move the database to persistent managed storage before sharing operational data.

## Demo operations and safety

- Use the sidebar to manage licenses, property payments, citizen service requests, and inspect table structure and row counts.
- Export business, property, and citizen-request registers as CSV files; print the Municipal Operations Summary as an official statement.
- The database explorer's **Restore Default Registry** action restores the original sample records.
- `SECRET_KEY` can be set in the environment; otherwise a process-specific random key is generated.
- This is a presentation prototype. Before handling real citizen or financial data, add production identity/access controls, CSRF/session configuration, auditing, backups, and a persistent managed database.
