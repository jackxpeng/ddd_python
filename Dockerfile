FROM python:3.13.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

# 3. Copy entire appliaton tree into /code
COPY . .

# 4. Put the virtual environment on the system PATH. 
# This ensures that when we call "flask", it uses the one installed by uv.
ENV PATH="/code/.venv/bin:$PATH"

# Set Flask environment variables
ENV FLASK_APP=flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]