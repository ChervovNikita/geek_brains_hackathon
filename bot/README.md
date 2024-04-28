# Чат-Бот для общения с учениками

## ⚙️ Рекомендованное железо

**NOTE:** Для запуска модели нужна требовательная видеокарта. Вес модели: ~5gb

Протестировано было на железе со следующими характеристиками:

| Комплектующая | Название      | Характеристики    |
|---------------|---------------|-------------------|
| Видеокарта    | A100          | видеопамять 125gb |
| Процессор     | -             | 16 ядер           |
| ОЗУ           | Intel IceLake | 30gb              |
| Диск          | -             | 200gb             |


## 🚀 Запуск

```shell
git clone https://github.com/Riprobot/GeekBrains-chat-bot
```

Для запуска, создайте `.env` рядом с `main.py`, заполните поля как в [examples/.env](examples/.env)

### 📦 Dockerized

```shell
docker compose -p cognitutor up -d
```

### 🐍 Native

Создайте `virtualenv`:

```shell
python -m venv venv
```

Включить `venv`:

На Linux/OSX:
```shell
source venv/bin/activate
```

На Windows:

```shell
venv\Scripts\activate
```

Скачать зависимости:

```shell
pip install -r requirements.txt
```

Если `postgres` и `redis` в докере:

```shell
docker compose -p cognitutor up -d redis-cognitutor postgres-cognitutor
```

Прогнать миграции, если потребуется:

```shell
alembic upgrade head
```

Запустить:

```shell
python main.py
```
