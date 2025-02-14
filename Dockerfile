FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Install the needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
