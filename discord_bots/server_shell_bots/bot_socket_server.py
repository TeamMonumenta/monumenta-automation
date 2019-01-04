import socket
import threading
import pprint
import json

class BotSocketServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 65536
        while True:
            try:
                data = client.recv(size)
                if data:
                    data = data.decode('utf-8')
                    data_in = json.loads(data)

                    # TODO DEBUG
                    pprint.pprint(data_in)

                    # TODO Handle different types of requests
                    data_out = json.dumps({"result": 0, "message": "Request handled"})

                    # Send the response back
                    client.send(data_out.encode('utf-8'))
                else:
                    client.close()
                    return False
            except Exception as e:
                print(e)
                client.close()
                return False

if __name__ == "__main__":
    BotSocketServer("127.0.0.1", 8765).listen()
