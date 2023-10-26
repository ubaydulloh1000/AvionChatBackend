FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV HOME_DIR=/app

WORKDIR $HOME_DIR

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install --no-root && poetry add gunicorn

COPY . /app

RUN chmod +x /app/entrypoint.sh
#ENTRYPOINT ["/app/entrypoint.sh"]
