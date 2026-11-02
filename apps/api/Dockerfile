FROM python:3.12-slim

WORKDIR /app
COPY apps/api ./apps/api
RUN python -m pip install --no-cache-dir ./apps/api

EXPOSE 8000
CMD ["uvicorn", "gaitmate_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

