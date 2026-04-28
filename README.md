# PiratePhotoSite

Минимальный аналог Instagram/Twitter: пользователи, лента постов с одной картинкой, комментарии, простой `React + TSX` фронт и `FastAPI` бэкенд.

## Структура

```text
PiratePhotoSite/
|-- backend/
|   `-- app/
|       |-- config.py
|       |-- database.py
|       |-- main.py
|       |-- models.py
|       |-- presenters.py
|       |-- schemas.py
|       |-- storage.py
|       |-- repositories/
|       `-- routers/
|-- frontend/
|   |-- public/
|   |-- src/
|   `-- README.md
|-- legacy/
|   |-- code/
|   `-- misc/
|-- data/
|   `-- legacy/
|-- .env.example
|-- docker-compose.yml
|-- main.py
`-- requirements.txt
```

## Что уже работает

- `GET /api/health/`
- `GET /api/users/`
- `POST /api/users/`
- `GET /api/users/{user_id}`
- `GET /api/posts/`
- `POST /api/posts/`
- `GET /api/posts/{post_id}`
- `GET /api/posts/{post_id}/comments/`
- `POST /api/posts/{post_id}/comments/`
- `GET /media/...` для выдачи картинок из `MinIO` или локального хранилища

## Как запустить

### 1. Поднять MinIO

Скопируй пример конфига:

```powershell
Copy-Item .env.example .env
```

Запусти `MinIO`:

```powershell
docker-compose up -d
```

После запуска будут доступны:

- `http://127.0.0.1:9000` - `MinIO` API
- `http://127.0.0.1:9001` - `MinIO Console`

По умолчанию используются:

- логин: `minioadmin`
- пароль: `minioadmin`
- bucket: `pirate-photo-site`

Bucket создается автоматически при старте бэкенда.

### 2. Поднять бэкенд

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Бэкенд будет доступен на `http://127.0.0.1:8000`, документация на `http://127.0.0.1:8000/docs`.

### 3. Поднять фронт

```powershell
cd frontend
npm install
npm run dev
```

Фронт обычно будет доступен на `http://127.0.0.1:5173`.

## Где хранятся данные

- SQLite база на Windows создается в `%LOCALAPPDATA%\PiratePhotoSite\data\app.db`
- на других системах база создается в `.runtime/data/app.db`
- изображения постов по умолчанию хранятся в `MinIO`

Если временно нужен старый локальный режим без `MinIO`, можно указать в `.env`:

```text
STORAGE_BACKEND=local
```

Тогда картинки будут храниться рядом с runtime-данными:

- Windows: `%LOCALAPPDATA%\PiratePhotoSite\media\`
- другие системы: `.runtime/media/`

## Фронт и API

- `Vite` уже проксирует `/api` и `/media` на `http://127.0.0.1:8000`
- фронт не зависит от прямого доступа к `MinIO`
- URL картинок для клиента остаются обычными: `/media/posts/...`
