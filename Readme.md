# 🎲 Kennerliga – Board Game League Tracker

Kennerliga is a board game league tracking system for organizing, recording, and analyzing board game sessions in structured leagues and seasons. Built with a **Django REST Framework** backend and a **Quasar (Vue.js)** frontend  for managing a board game community.

---

## 🚀 Features

- 🧑‍🤝‍🧑 League and season organization  
- 🎯 Game result tracking  
- 🗂️ Player profiles and user authentication  
- 💬 In-app chat and announcements  
- 📊 Swagger/OpenAPI auto-generated API docs  
- 🧱 Clean frontend/backend separation for flexibility  

---

## 🛠️ Getting Started

### 🔧 Backend Setup (Django)

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/kennerliga.git
cd kennerliga/api
```

#### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the development server

```bash
./manage.py runserver
```

#### 5. Visit the app

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📘 API Documentation

Kennerliga provides fully browsable and testable API documentation using **Swagger UI**.

- Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- OpenAPI schema: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- Redoc (optional): [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

---

## 🧩 Frontend Setup (Quasar – WIP)

The frontend is built using the [Quasar Framework](https://quasar.dev) (Vue.js) and will be served separately. To set it up:

```bash
cd ../frontend
npm install
quasar dev
```

_This part is still under development. Stay tuned!_

---

## 🔔 Push Notifications

Installed users are prompted to enable notifications for registration openings,
season starts, and when it is their turn. Configure the following environment
variables on the Django host before deploying:

```env
VAPID_PUBLIC_KEY=<base64url VAPID public key>
VAPID_PRIVATE_KEY=<VAPID private key PEM or path to a .pem file>
VAPID_SUBJECT=mailto:admin@example.com
```

Generate a VAPID key pair with the `vapid --gen` utility installed by
`pywebpush`. Keep the private key secret.

**All three variables must be set** — if any is missing the backend logs a
warning naming it and silently sends nothing. They are only read through the
production settings module, so run the server with
`DJANGO_SETTINGS_MODULE=django_rest.settings_production` (which loads `.env`);
under the plain dev `settings.py` the `VAPID_*` values stay unset.

### Storing the private key in `.env`

`VAPID_PRIVATE_KEY` accepts either form:

- **A path** to the `.pem` file, which avoids multi-line issues entirely:

  ```env
  VAPID_PRIVATE_KEY=/etc/kennerliga/vapid_private_key.pem
  ```

- **The PEM inlined**. Since a `.env` value must stay on one line, escape the
  newlines as `\n` and wrap the value in double quotes; the backend restores
  the real newlines before use:

  ```env
  VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIGT...\n-----END PRIVATE KEY-----\n"
  ```

Make sure `VAPID_PUBLIC_KEY` is the base64url public key derived from that same
private key — a mismatched pair lets the browser subscribe but the push server
rejects every send.

Run the Django migrations before deploying the frontend so subscriptions can be
stored.

### Verifying the pipeline

Once configured, a logged-in user can confirm the end-to-end chain without
waiting for a real game event by POSTing to the test endpoint:

```bash
curl -X POST https://<host>/api/notifications/test/ \
  -H "Authorization: Token <your-token>"
```

It returns `{"targeted": N, "succeeded": M}` (how many of your own
subscriptions were reached), or `503` if VAPID is not configured.

> **iOS:** web push only reaches a PWA on iOS 16.4+ **when it is installed to
> the home screen** — it will not arrive in Safari tabs. This is an Apple
> platform requirement, not a bug.

---

## 📂 Project Structure

```
kennerliga/
├── api/                   # Django REST backend
│   ├── game/              # Game models and views
│   ├── user/              # User auth and profiles
│   ├── season/league/     # League and season logic
│   ├── chat/              # Chat module
│   ├── announcement/      # Announcements and info posts
│   ├── result/            # Game results handling
│   ├── api/urls.py        # API route aggregation
│   └── manage.py
├── frontend/              # Quasar frontend (optional)
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🔐 Authentication

Kennerliga uses token-based authentication with optional login/logout endpoints:

- `/api/login/` – custom login  
- `/api/logout/` – logout  
- `/api/api-token-auth/` – DRF token endpoint  

Tokens are required for most write actions (CRUD, posting results, etc.).

---

## 🧪 Development Notes

- Python 3.11+  
- Django 5+  
- Quasar 2.x  
- Uses `drf-spectacular` for OpenAPI 3.0 documentation  
- Modular Django app structure  
