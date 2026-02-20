# Multi-stage build for DICOM Middleware
FROM python:3.11-slim as builder
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app/src
ENV PATH=/root/.local/bin:$PATH
COPY --from=builder /root/.local /root/.local
COPY src /app/src
RUN mkdir -p /data/dicom
EXPOSE 8000
CMD ["uvicorn", "dicom_middleware.main:app", "--host", "0.0.0.0", "--port", "8000"]
