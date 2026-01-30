FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
        curl \
            && rm -rf /var/lib/apt/lists/*

            # Copy requirements
            COPY requirements.txt .
            RUN pip install --no-cache-dir -r requirements.txt

            # Copy source code
            COPY . .

            # Create non-root user
            RUN useradd -m -u 1000 gripro && \
                chown -R gripro:gripro /app
                USER gripro

                # Health check
                HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
                    CMD curl -f http://localhost:8000/health || exit 1

                    # Run application
                    CMD ["python", "main.py"]
