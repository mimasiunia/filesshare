FROM python:3.9-slim

WORKDIR /script

COPY script /script

# Install system dependencies and MariaDB Connector/C
RUN apt-get update && apt-get install -y \
    libmariadb-dev-compat \
    libmariadb-dev \
    gcc \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "script.py"]
