# system-design-interview-python

Django + React boilerplate for interview prep. Ports: Postgres 21010, Redis 21011, backend 21012, frontend 21013.

## Backend (`backend/`)

### Install
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set DJANGO_SECRET_KEY and JWT_SECRET_KEY
```

### Run
```bash
docker compose up -d                  # Postgres + Redis
python manage.py migrate              # apply migrations (manual step)
python manage.py runserver 21012
```

### Test
```bash
pytest
```

### Migrations
```bash
python manage.py makemigrations       # after model changes; review the file
python manage.py migrate
python manage.py showmigrations
```

## Frontend (`frontend/`)

### Install
```bash
cd frontend
npm install
cp .env.example .env
```

### Run
```bash
npm run dev                           # http://localhost:21013
npm run build
npm run lint
```
