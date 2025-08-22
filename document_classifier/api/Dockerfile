# api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Skopiuj requirements
COPY api/requirements.txt ./requirements.txt

# Upgrade pip do najnowszej wersji
RUN pip install --upgrade pip

# Zainstaluj DOKŁADNIE te wersje
RUN pip install --only-binary=all -r requirements.txt

# Skopiuj folder core
COPY core ./core

# Skopiuj ZAWARTOŚĆ folderu api
COPY api/ ./

# Stwórz folder data dla SQLite
RUN mkdir -p data

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]