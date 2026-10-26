# Hajz — Deployment

| Part | Host | Address |
|---|---|---|
| Frontend | Vercel (Hobby) | https://hajz-booking.vercel.app |
| Backend | Render (Free, Docker) | https://hajz-api.onrender.com |
| Database | TiDB Cloud Serverless | `gateway01.<region>.prod.aws.tidbcloud.com:4000` |

```text
Browser ──► Vercel (Angular) ──/api/*──► Render (Flask) ──TLS──► TiDB Cloud
```

The browser only ever talks to Vercel. Vercel forwards `/api/*` to Render
(`frontend/vercel.json`), so cookies stay first-party.

Secrets (the database password) are typed **only** into the Render dashboard.
They never go in the repo, in chat, or in `render.yaml`.

---

## 1. TiDB Cloud (database)

1. https://tidbcloud.com → **Create Cluster** → **Serverless** (free).
2. Region: **Singapore (ap-southeast-1)**, the same region as Render.
3. Cluster name: `hajz`. Create.
4. On the cluster page click **Connect**:
   - Connection type: **Public**
   - Connect with: **General**
   - Click **Generate Password** and keep the tab open (you'll copy it in step 2.5).
5. Note the four values shown: **Host**, **Port** (4000), **User** (looks like
   `xxxxxxxx.root`), **Password**.

The `hajz` database is created automatically on the first deploy.

## 2. Render (backend)

1. https://dashboard.render.com → **New** → **Blueprint**.
2. Pick the `aldahmashi/hajz` repo. Render reads `render.yaml` and shows one
   service, `hajz-api`.
3. It asks for **MYSQL_DB**. Build it from the TiDB values, separated by colons:

   ```text
   HOST:USER:PASSWORD:4000:hajz
   ```

   Example shape: `gateway01.ap-southeast-1.prod.aws.tidbcloud.com:abc123.root:PASSWORD:4000:hajz`

   > The password must not contain `:`. If it does, generate a new one in TiDB.
4. Click **Apply**. The first build takes about 5 minutes. On every start the
   container runs `python manage.py migrate`, then `python manage.py seed`
   (idempotent upserts of cities, amenities, FX rates and demo personas), then gunicorn.
5. When the status is **Live**, open
   https://hajz-api.onrender.com/api/health. It should show `"status": "ok"`.

If Render gave the service a different address (the name was taken), update the
`/api` destination in `frontend/vercel.json` and push.

## 3. Vercel (frontend)

1. https://vercel.com/new → import `aldahmashi/hajz`. Project domain: **Settings → Domains → `hajz-booking.vercel.app`** (`hajz.vercel.app` belongs to someone else; per-deployment URLs sit behind Vercel login).
2. **Root Directory: `frontend`**. Leave the preset on Angular and leave build
   settings alone (they come from `frontend/vercel.json`).
3. Deploy. Every push to `main` redeploys automatically.

Open the site → "System status" should say **All systems operational**.

## 4. Running manage.py against production from your PC

Use sparingly, e.g. to check the production database.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:APP_ENV = "production"
$env:MYSQL_DB = "HOST:USER:PASSWORD:4000:hajz"
$env:DB_SSL_CA = "C:\Program Files\Git\mingw64\etc\ssl\certs\ca-bundle.crt"
python manage.py db-status
python manage.py seed
Remove-Item Env:MYSQL_DB, Env:APP_ENV, Env:DB_SSL_CA
```

`reset-db` refuses to run in production.

## 5. Things to know

| Topic | Detail |
|---|---|
| Cold starts | Render Free sleeps after 15 min idle; the first request then takes ~1 minute. UptimeRobot pinging `/api/health` keeps it awake (milestone M7). |
| Deploy order | Push → GitHub Actions CI → if green, Render deploys (`autoDeployTrigger: checksPass`). Vercel deploys on every push. |
| Migrations and seeds | Run automatically on every Render start (seeds re-apply reference values, e.g. FX rates). A failing migration stops the deploy and the old version keeps serving. |
| TiDB compatibility | Migrations, seeds and tests were verified against TiDB v8.5 locally before the first deploy. |
