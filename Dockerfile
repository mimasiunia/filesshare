FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install system dependencies and MariaDB Connector/C
RUN apt-get update && apt-get install -y \
    libmariadb-dev-compat \
    libmariadb-dev \
    gcc \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4999

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=4999"]
