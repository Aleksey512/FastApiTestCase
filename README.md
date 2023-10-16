# FastApiTestCase

## Используемые библиотеки/фреймворки:
- [Docker](https://www.docker.com/)
- [FastApi](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [PostgreSQL](https://www.postgresql.org/)

## Installation

- *Проверить .env файл в папке app*

```dotenv
PUBLIC_HOST=localhost                    # Хост нашего сервера
PUBLIC_PORT=8008                         # Публичный порт (Необхоимо указать так же в docker compose)
DATABASE=postgresql+asyncpg              # БД PostgreSQL + асинхронная зависимость
DATABASE_NAME=fastapi                    # Имя нашей бд (Необхоимо указать так же в docker compose)
DATABASE_USER=fastapi_secure_user        # Пользователь нашей бд (Необхоимо указать так же в docker compose)
DATABASE_PASSWORD=dj_PG!p_s(99)*74_pR_oP # Пароль нашей бд (Необхоимо указать так же в docker compose)
DATABASE_HOST=db                         # Хост нашей бд
DATABASE_PORT=5432                       # Локальный порт нашей БД внутри Docker
```

- *Проверить docker compose файл*

```yaml
version: '3.9'

services:
  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0
    ports:
      - "8008:8000"
    volumes:
      - .:/app
    env_file:
      - app/.env
    depends_on:
      - db

  db:
    image: postgres:15.4
    container_name: fastapi_db
    environment:
      POSTGRES_DB: fastapi
      POSTGRES_USER: fastapi_secure_user
      POSTGRES_PASSWORD: dj_PG!p_s(99)*74_pR_oP
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - /opt/pgsql:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

- *Запустить docker compose*

```bash
docker compose up --build
```
*or*
```bash
docker compose up -d
```



## Example

Для проверки REST методов буду использовать [Postman](https://www.postman.com/)

Посмотреть все API можно по url: ***/docs***

- POST method (http://127.0.0.1:8008/api/questions) -> body {"questions_num": int}

![1.png](img/1.png)

Вернул предыдущую запись из бд

Добавляем ещё сто элементов

![2.png](img/2.png)

- GET method (http://127.0.0.1:8008/api/questions) -> query ***size***: *int* and query ***limit***: *int*

![3.png](img/3.png)