# ==========================================
# STAGE 1: The Builder (Has shell and tools)
# ==========================================
FROM cgr.dev/chainguard/python:latest-dev AS builder

# 1. Get uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

# 2. Install dependencies into /code/.venv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 3. Copy application code
COPY . .


# ==========================================
# STAGE 2: The Final Image (Distroless, no shell)
# ==========================================
FROM cgr.dev/chainguard/python:latest

WORKDIR /code

# 4. Copy the fully built environment from Stage 1!
COPY --from=builder /code /code

# 5. Set paths and environment variables
ENV PATH="/code/.venv/bin:$PATH"
ENV FLASK_APP=flask_app.py \
    FLASK_DEBUG=1 \
    PYTHONUNBUFFERED=1

# 6. EXECUTE
# First, wipe the base image's default entrypoint clean
ENTRYPOINT []

# Second, use the ABSOLUTE path to the virtual environment's python!
CMD ["/code/.venv/bin/python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"]
