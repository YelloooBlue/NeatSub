FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8095

EXPOSE ${PORT}

CMD gunicorn -w 4 -b 0.0.0.0:${PORT} run:app