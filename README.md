# dictation-web

Hệ thống luyện nghe chép chính tả. Backend FastAPI, frontend React + Vite,
PostgreSQL, Redis, worker xử lý media.

## Yêu cầu

- Docker Engine 24+ và Docker Compose v2 (`docker compose`, không phải `docker-compose`)
- Chạy được bằng **Docker Desktop trên Windows** hoặc **Docker engine trong WSL**, không cần đổi file cấu hình

## Chạy lần đầu

```bash
cp .env.example .env
# Mở .env, đổi POSTGRES_PASSWORD và SECRET_KEY
docker compose up -d --build
```

Sinh `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Sau khi lên:

| Thành phần | Địa chỉ |
|---|---|
| API | http://localhost:8000/api/v1/health |
| API docs | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

Container `api` tự chạy `alembic upgrade head` khi khởi động, nên không cần
migrate tay.

## Windows vs WSL

Repo không dùng bind mount hay đường dẫn tuyệt đối nào, nên cùng một
`docker-compose.yml` chạy được ở cả hai nơi.

- **Docker Desktop (Windows):** bật WSL 2 backend trong Settings → General.
  Chạy lệnh trong PowerShell tại thư mục repo.
- **Docker trong WSL:** repo nằm ở `D:\other\ktpm\ck` thì vào WSL bằng
  `cd /mnt/d/other/ktpm/ck`. Build từ `/mnt/...` chậm hơn; muốn nhanh thì
  clone repo vào filesystem của WSL (ví dụ `~/projects/`).
- `.gitattributes` buộc mọi file text dùng `LF`. Đừng tắt nó: `CRLF` trong
  `Dockerfile` hoặc shell script sẽ làm container crash khi chạy trên Linux.

## Lệnh hay dùng

```bash
docker compose logs -f api         # xem log API
docker compose ps                  # trạng thái container
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "mô tả"
docker compose exec postgres psql -U app_user -d dictation_db
docker compose down                # dừng, giữ dữ liệu
docker compose down -v             # dừng và xóa luôn database
```

## Chạy backend ngoài Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # sửa DATABASE_URL trỏ về localhost
alembic upgrade head
uvicorn app.main:app --reload
```

## Cấu trúc

```text
backend/app/
├── api/              # router, endpoint, schema, middleware
├── application/      # use case, DTO
├── domain/           # entity, value object, ports (interface)
│   └── ports/        # BaseRepository, MediaSource, TranscriberPort, ScoringStrategy
├── infrastructure/   # DB, storage, messaging, AI provider, config
└── worker/           # tiến trình xử lý nền
```

Quy ước code, commit, branch: xem [CONTRIBUTING.md](CONTRIBUTING.md).
Kế hoạch và phân công: xem [PLAN_Dictation_App.md](PLAN_Dictation_App.md).
