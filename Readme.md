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

