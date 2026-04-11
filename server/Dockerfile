FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

EXPOSE 7860

CMD ["serve"]
