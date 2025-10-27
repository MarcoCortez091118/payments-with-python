FROM python:3.12-slim

WORKDIR /app

COPY . ./mock_api

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastapi uvicorn[standard]

CMD ["uvicorn", "mock_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
