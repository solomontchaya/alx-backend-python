# Use Python 3.10 base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN apt-get update && \
    apt-get install -y gcc build-essential python3-dev libc-dev \
                       pkg-config default-libmysqlclient-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove -y gcc build-essential python3-dev libc-dev pkg-config && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire Django app into container
COPY . /app/

# Expose Django's default port
EXPOSE 8000

# Default command to run the Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
