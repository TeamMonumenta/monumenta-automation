import socket
import threading
import pprint
import json

from shell_actions import findBestMatchCommand, checkPermissionsExplicitly

class BotSocketServer(object):
    def __init__(self, host, port, bot_config):
        self.host = host
        self.port = port
        self.bot_config = bot_config
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

                    if botConfig["extraDebug"]:
                        pprint.pprint(data_in)

                    ################################################################################

                    if not "action" in data_in:
                        # Error - no action to do
                        data_out = json.dumps({"result": 1, "message": "Request missing 'action' field"})

                    elif data_in["action"] == "command":
                        if not "command" in data_in:
                            # Error - no action to do
                            data_out = json.dumps({"result": 0, "message": "Request handled"})

                        else:
                            command = data_in["command"]

                            actionClass = findBestMatchCommand(self.bot_config, command)
                            if actionClass is None:
                                data_out = json.dumps({"result": 1, "message": "No matching command '{}'".format(command)})
                            else:
                                action = actionClass(self.bot_config, command)
                                # In-game commands are those that Team Epic can use
                                if not checkPermissionsExplicitly(action.command, ["@team epic"]):
                                    data_out = json.dumps({"result": 1, "message": "You do not have permission to run this command"})
                                else:
                                    data_out = json.dumps({"result": 0, "message": "DEBUG SUCCESS"})
                                    #await action.doActions(client, command.channel, command.author)
                    else:
                        data_out = json.dumps({"result": 1, "message": "No handler for action '{}' available".format(data_in["action"])})

                    ################################################################################

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
