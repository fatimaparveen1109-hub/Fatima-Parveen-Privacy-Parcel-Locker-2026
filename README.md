# Privacy Parcel Locker

Streamlit + Supabase PostgreSQL university project. Python 3.11 is recommended.

## Important honesty notes

- The eight catalogue pictures in `assets/` are **original Pillow-made product illustrations**, not real product photographs. They are separate, color-matched images and are clearly illustrative. Replace them with photographs you own or have permission to use before presenting the catalogue as a real store.
- `hero_locker.jpg` is a cropped concept visual from the generated landing-page mockup, not a photograph of installed hardware.
- The physical locker controller is deliberately simulated. No real locker can be unlocked by this project until the other group supplies its documented API and credentials.
- Payment is demo-only. Do not enter real card numbers, bank credentials or mobile-wallet passwords.
- This is a substantial university-project implementation, not a security-certified production parcel system. Independent security review, proper encryption/key management, payment provider integration, hardware API integration and end-to-end deployment testing remain necessary before real customer data or parcels are used.
- The public page contains no product catalogue. Products are shown only inside the customer portal.

## 1. Create Supabase database

1. Create a Supabase project.
2. Open **SQL Editor** in the Supabase dashboard.
3. Open this project's `schema.sql`, copy all SQL, paste it into a new query and press **Run**.
4. Confirm that tables, the five Karachi hubs and their 40 lockers were created. The script also inserts eight illustrative catalogue products under two disabled catalogue-only seller accounts.

## 2. Get the database connection string

1. In Supabase open **Project Settings → Database**.
2. Find **Connection string** and choose **URI**.
3. Copy the PostgreSQL connection string. Replace the password placeholder with your database password. Use the session/pooler URI if your hosting network requires it.
4. Do not paste the URI into Python files or commit it to GitHub.

## 3. Run locally

Install Python 3.11, then in a terminal inside this project:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your own values. Generate an admin password hash with:

```bash
python -c "from services.auth import hash_password; print(hash_password('Choose-A-Long-Unique-Password'))"
```

Paste the printed hash as `ADMIN_PASSWORD_HASH`. Set `DATABASE_URL` to your Supabase URI. Then run:

```bash
streamlit run app.py
```

Never commit `.streamlit/secrets.toml`.

## 4. Upload to GitHub

1. Sign in to GitHub and choose **New repository**.
2. Name it `Privacy-Parcel-Locker`; choose Private if it contains any personal project information.
3. On your computer open the project folder, not its parent folder.
4. Add all project files, including `assets/`, `.streamlit/config.toml`, `schema.sql`, and `README.md`.
5. Do **not** upload `.streamlit/secrets.toml`, `.venv/`, or `__pycache__/`.
6. Commit and push. The included `.gitignore` excludes secrets and local environments.

## 5. Deploy on Streamlit Community Cloud

1. Open Streamlit Community Cloud and sign in with GitHub.
2. Choose **Create app** and select your repository, branch, and `app.py` as the main file.
3. Open **Advanced settings → Secrets**.
4. Paste the same values from your local secrets file using TOML syntax, for example:

```toml
DATABASE_URL = "postgresql://postgres:YOUR_DB_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres?sslmode=require"
ADMIN_EMAIL = "admin@your-domain.example"
ADMIN_PASSWORD_HASH = "pbkdf2_sha256$..."
APP_BASE_URL = "https://your-app-name.streamlit.app"
```

5. Save and deploy. Streamlit installs packages from `requirements.txt`.
6. Test with a new customer registration. Seller and rider registrations stay pending until an administrator approves them.

## 6. First test workflow

- Open the public home page and confirm there is no catalogue section.
- Register a customer and log in.
- Open **Catalogue / Orders** to see the eight sample products and add them to a cart.
- Choose a seeded Karachi hub and place a demo order.
- Check order history on the customer dashboard.
- Register a seller and rider with separate email addresses; their accounts require approval.
- Configure admin secrets before trying admin login. Admin is not publicly registerable.

## 7. Hardware API integration later

The adapter boundary is `integrations/locker_controller.py`. When the partner group provides official API documentation, authentication method, request/response schemas, test environment and failure behavior, implement those documented calls in the adapter. Do not guess endpoint URLs. Keep the simulated mode enabled until hardware integration is tested with permission.

## Included functionality and current limits

Implemented: PBKDF2-SHA256 password hashing, role-aware registration/login, seller/rider approval state, public landing page, customer catalogue, transactional stock reservation, hub/locker schema and initial inventory, demo payment service, hashed QR-token service, order status transition service, returns service, rider assignment service, notifications, wallets, pickup-expiry housekeeping service, and admin overview/approval screen.

Not yet complete: production-ready role-by-role CRUD for every requested admin entity; complete UI for QR scanning, returns, wallet settlement, complaints, reporting and audit review; automatic background reminders (a scheduled worker is needed); all alternative-hub fallback behavior; full QR attempt lockout/holder/hub/payment binding; customer-private-data encryption and production-grade RLS policies; verified end-to-end tests against a live Supabase project; actual payment and locker hardware integrations. The UI currently supports demo order creation and basic portals, not the full real-world parcel workflow. Do not use it to handle real parcels or sensitive customer data yet.
