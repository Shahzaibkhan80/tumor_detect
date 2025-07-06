# Use official Python base image
FROM python:3.12-slim

# Install system packages required by OpenCV
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Start the app with gunicorn
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000"]
