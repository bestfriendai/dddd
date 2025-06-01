# Use Python 3.12 slim image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN /bin/uv sync --no-install-project

# Copy the rest of the application
COPY . .

# Install the application
RUN /bin/uv sync

# Expose port
EXPOSE 8000

# Run the application
CMD ["/bin/uv", "run", "python", "server.py", "--host", "0.0.0.0"]
