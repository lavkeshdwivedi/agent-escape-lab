FROM python:3.11-slim

WORKDIR /app

RUN pip install mitmproxy pyyaml

COPY mitm_filter.py .
COPY filter_rules.yaml .

EXPOSE 8080 8443

CMD ["mitmdump", "-s", "mitm_filter.py", "--listen-port", "8080", "--ssl-insecure"]
