FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir setuptools && \
    pip install --no-cache-dir -e .

EXPOSE 7860

CMD ["serve"]
