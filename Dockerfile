# Use a base image with Python
FROM python:3.11

# Install system dependencies for Poetry
RUN apt-get update && apt-get install -y curl git && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set working directory in the container
WORKDIR /app

# Copy only the dependency files first (leveraging Docker caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy the rest of the application files
COPY . .

# Expose the application port (e.g., Flask default is 5000)
EXPOSE 5000

# Define the command to run your application
CMD ["poetry", "run", "python", "run.py"]
