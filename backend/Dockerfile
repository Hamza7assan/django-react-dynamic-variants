# use a lightweight Python image
FROM python:3.12-slim

# set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy rest of the project filess
COPY . .

EXPOSE 8000

# Default command to run the server (will be overridden in docker-compose to run migrations first)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]