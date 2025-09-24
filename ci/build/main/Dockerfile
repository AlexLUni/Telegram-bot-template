FROM python:3.12.11-slim-bookworm

ENV TZ=Europe/Moscow \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /data/app
COPY ci/build/dependencies/requirements.txt /data/dependencies/requirements.txt
RUN pip install --no-cache-dir -r /data/dependencies/requirements.txt 

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root --no-interaction
COPY . .

CMD ["sh", "-c", "poetry run python -m alembic upgrade head && poetry run python main.py"]
