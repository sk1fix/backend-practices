FROM python:3.13-slim

WORKDIR /backend-practices
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5050

CMD [ "python3", "./app/main.py"]