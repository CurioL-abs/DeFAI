FROM python:3.11-slim
WORKDIR /usr/src/ai
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "inference:app", "--host", "0.0.0.0", "--port", "8001"]
