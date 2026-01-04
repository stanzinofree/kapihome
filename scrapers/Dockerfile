FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/data_tmp /app/cache

# Set Python unbuffered for real-time logs
ENV PYTHONUNBUFFERED=1

# Run the scheduler
CMD ["python", "-u", "scheduler.py"]
