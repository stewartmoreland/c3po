FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc && \
    pip install --upgrade pip

COPY ./ /app/

WORKDIR /app
RUN pip install --no-cache-dir --editable .

ENTRYPOINT [ "gunicorn" ]
CMD [ "c3po_api.main:main()", "--workers 2", "--threads 2", "-b 0.0.0.0:8000" ]
