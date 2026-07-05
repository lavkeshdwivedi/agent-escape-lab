FROM python:3.13-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    curl wget nmap netcat-traditional dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH=/workspace:/experiments:/logging

CMD ["python", "-c", "import time; time.sleep(999999)"]
