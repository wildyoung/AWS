FROM python:3.12-slim

WORKDIR /app

COPY app.py requirements.txt ./
COPY static/ static/
COPY templates/ templates/

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

CMD ["python", "app.py"]
