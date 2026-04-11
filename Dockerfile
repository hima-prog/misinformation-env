FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade setuptools pip && \
    pip install --no-cache-dir -e .

EXPOSE 7860

CMD ["serve"]
