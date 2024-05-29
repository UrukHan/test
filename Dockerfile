FROM python:3.9-slim

WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    wait-for-it

# Установка зависимостей
COPY requirements/base.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов приложения
COPY . .

# Запуск миграции и сервиса с логами
CMD ["sh", "-c", "python create_tables.py && wait-for-it postgres:5432 -- python -m app.__main__"]
