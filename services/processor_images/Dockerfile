FROM python:3.9-slim

ARG SERVICE_DIR=processor_images
# Set environment variables for Python and ensure Python outputs everything
# to stdout and stderr without buffering (e.g. for Docker logs)
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container to /app
WORKDIR /app

# Copy only the dependency files to avoid caching issues
COPY $SERVICE_DIR/poetry.lock $SERVICE_DIR/pyproject.toml /app/

# Install Poetry
RUN pip install poetry

# Something can screw up during the development process, so rebuild lockfile
RUN poetry lock --no-update

# Install project dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi
