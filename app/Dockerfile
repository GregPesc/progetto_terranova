FROM python:3.13.1-alpine

RUN apk add curl

WORKDIR /deploy-dir

COPY . .

RUN pip install --no-cache-dir -r requirements-deploy.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]
