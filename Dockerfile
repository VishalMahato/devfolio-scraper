FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required by psycopg2 or other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Setting python path so src.main runs correctly
ENV PYTHONPATH="/app"

CMD ["python", "-m", "src.main"]
