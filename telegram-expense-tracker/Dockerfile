# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY expense_bot.py .
COPY credentials.json .

# Run the bot
CMD ["python", "expense_bot.py"]
