# admin/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Skopiuj requirements dla admin
COPY admin/requirements.txt ./requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Zainstaluj zależności
RUN pip install --only-binary=all -r requirements.txt

# Skopiuj folder core
COPY core ./core

# Skopiuj CAŁĄ zawartość admin (łącznie z templates)
COPY admin/ ./

# Stwórz folder data
RUN mkdir -p data

# Debug - sprawdź czy templates istnieją
RUN ls -la templates/

EXPOSE 8001
CMD ["uvicorn", "admin_app:app", "--host", "0.0.0.0", "--port", "8001"]