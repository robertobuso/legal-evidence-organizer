FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app /app/app

# Create upload directories
RUN mkdir -p /app/uploads/pdfs /app/uploads/chats /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV DEBUG=False

# Expose port
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]