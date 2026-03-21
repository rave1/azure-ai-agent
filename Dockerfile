FROM python:3.12-slim

WORKDIR /app
COPY ./src .

RUN pip install --no-cache-dir gradio ollama python-dotenv

CMD ["python", "main.py"]
