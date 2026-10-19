# Hajz — Running Locally

How to run the backend (Flask API) and frontend (Angular) on your own machine.
Commands are for **PowerShell** on Windows, run from the repo folder
(`C:\Users\nasse\projects\hajz`) unless a step says otherwise.

| Part | Address | Port |
|---|---|---|
| Frontend (Angular) | http://localhost:4302 | 4302 |
| Backend (Flask API) | http://localhost:8000/api/health | 8000 |
| Database (MySQL 8.4, Docker) | `127.0.0.1` | 3307 |

> Ports 3306, 4200 and 4300 are used by other projects on this machine, which is
> why Hajz uses 3307, 8000 and 4302.

---

## 1. Requirements (install once)

| Tool | Version | Check with |
|---|---|---|
| Docker Desktop | any recent | `docker --version` |
| Python | 3.13 | `py -3.13 --version` |
| Node.js | 24 | `node -v` |

---

## 2. First-time setup (do once)

### Database

```powershell
docker compose up -d
```

Wait about 20 seconds the first time while MySQL starts.

### Backend

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed
python manage.py db-status
cd ..
```

`db-status` should show `Exists True` and `Revision 0006_assistant` (or newer).

> If PowerShell says *running scripts is disabled*, run this once and try again:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Frontend

```powershell
cd frontend
npm install
cd ..
```

---

## 3. Daily: start everything

Use **two terminals**.

**Terminal 1: backend**

```powershell
docker compose up -d
cd backend
.\.venv\Scripts\Activate.ps1
python app.py
```

Leave it running. Check http://localhost:8000/api/health shows `"status": "ok"`.

**Terminal 2: frontend**

```powershell
cd frontend
npm start
```

Open **http://localhost:4302**. The "System status" section at the bottom should
say *All systems operational*.

The frontend forwards every `/api/...` request to the backend on port 8000
(`frontend/proxy.conf.json`), so both must be running.

**Stop:** press `Ctrl+C` in each terminal. `docker compose down` stops MySQL
(your data is kept).

---

## 4. After pulling new code

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py migrate
cd ..\frontend
npm install
```

---

## 5. Tests and lint (same checks as CI)

**Backend** (MySQL must be running):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
ruff check .
python manage.py migration-check
pytest -q
```

**Frontend:**

```powershell
cd frontend
npm run lint
npx ng test --watch=false
npm run build
```

GitHub Actions runs all of these on every push:
https://github.com/aldahmashi/hajz/actions

---

## 6. Database commands

Run inside `backend` with the venv active.

| Command | What it does |
|---|---|
| `python manage.py migrate` | Apply new migrations |
| `python manage.py rollback` | Undo the last migration |
| `python manage.py seed` | Insert cities, amenities, FX rates, demo personas |
| `python manage.py db-status` | Show connection, table count and revision |
| `python manage.py migration-check` | Fail if models and migrations differ |
| `python manage.py reset-db` | **Delete everything** and recreate an empty database (local only) |

Start over from scratch: `reset-db`, then `migrate`, then `seed`.

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `Port 4302 is already in use` | Another app is on it. Run `npx ng serve --port 4303` |
| Status card says *Service unavailable* | Backend isn't running, or MySQL is stopped. Start terminal 1 and `docker compose up -d` |
| `Can't connect to MySQL server on '127.0.0.1:3307'` | `docker compose up -d`, wait 20 seconds, check `docker ps` shows `hajz-mysql (healthy)` |
| `MYSQL_DB is required` | `backend/.env` is missing: `Copy-Item .env.example .env` inside `backend` |
| `ModuleNotFoundError` in the backend | Venv not active, or new packages: activate it, then `pip install -r requirements-dev.txt` |
| `.\.venv\Scripts\Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Frontend errors after a pull | `npm install` inside `frontend` |
| Copy/paste in Git Bash | Copy: select text. Paste: `Shift+Insert` or right-click |
