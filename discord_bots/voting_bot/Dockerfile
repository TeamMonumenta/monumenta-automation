FROM python:3.12-slim

ARG VOTING_UID=1000

RUN useradd --uid "${VOTING_UID}" --create-home --shell /bin/bash voting \
    && mkdir -p /data /config \
    && chown voting:voting /data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY voting/ voting/
COPY main.py bot.py ./

USER voting

ENV CONFIG_PATH=/config/config.yml

CMD ["python", "main.py"]
