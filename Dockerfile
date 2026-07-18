FROM python:3.11-slim

WORKDIR /app
ENV HF_HOME=/data/hf

# Tầng dependency tách riêng — chỉ rebuild khi pyproject.toml đổi (torch rất nặng)
COPY pyproject.toml ./
RUN python -c "import tomllib; d = tomllib.load(open('pyproject.toml','rb'))['project']; print('\n'.join(d['dependencies'] + d['optional-dependencies']['ml']))" > /tmp/reqs.txt \
    && pip install --no-cache-dir -r /tmp/reqs.txt

COPY ingest/ ingest/
COPY engine/ engine/
COPY retrieval/ retrieval/
COPY answer/ answer/
COPY api/ api/
COPY ui/ ui/
COPY eval/ eval/
RUN pip install --no-cache-dir --no-deps -e .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
