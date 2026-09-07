FROM python:3.13-slim

# LibreOffice Writer headless: motor usado por core/visual.py para convertir
# DOCX -> PDF antes del render a imagenes. --no-install-recommends evita traer
# Impress/Calc/Base y otros paquetes que esta API no usa.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY core ./core

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
