FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the kafka worker script executable
RUN chmod +x kafka_worker.py

CMD ["python", "app/app.py"]