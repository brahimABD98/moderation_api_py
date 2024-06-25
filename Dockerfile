FROM python:3.12-slim-bullseye

LABEL authors="march"

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade --no-cache-dir -r /app/requirements.txt

COPY . .

EXPOSE 9095

CMD ["fastapi","run","app/main.py","--port","9095"]