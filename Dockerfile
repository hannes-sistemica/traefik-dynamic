# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install uv (ultra-fast Python package manager)
RUN pip install uv

# Copy requirements.txt and install dependencies system-wide
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]