FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY taskbot/ taskbot/
COPY cli/ cli/
COPY main.py ./

# Same uid as the automation image, so files on the existing volume keep their owner
RUN useradd -u 1000 -m taskbot
USER 1000:1000
ENV TASK_HOME=/data \
    MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "main.py"]
