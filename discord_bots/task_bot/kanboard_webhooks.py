import multiprocessing as mp

from flask import Flask, request, Response

app = Flask(__name__)
webhook_queue = None

@app.route('/webhook', methods=['POST'])
def respond():
    global webhook_queue
    print(f"Got request on webserver: {request.json}");
    webhook_queue.put(request.json)
    return Response(status=200)

def run():
    app.run(host= '0.0.0.0')

def start_webhook_server() -> (mp.Process, mp.Queue):
    global webhook_queue
    webhook_queue = mp.Queue()
    process = mp.Process(target=run)
    process.start()
    return (process, webhook_queue)
