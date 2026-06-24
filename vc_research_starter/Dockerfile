FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[dev]"

COPY config ./config
COPY prompts ./prompts
COPY schemas ./schemas
COPY templates ./templates
COPY data ./data
COPY *.md ./
COPY test_workbench.py ./

RUN mkdir -p data/raw data/normalized data/output

CMD ["vc-research", "--help"]
