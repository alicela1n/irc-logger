from irc import *
import os
import platform
import cherrypy
from multiprocessing import Process

version = "0.01"

class web_logger(object):
    @cherrypy.expose
    def index(self):
        return "Hello World"

    @cherrypy.expose
    def log(self, server="irc.oftc.net", channel='##alicela1n'):
        html_block = ""
        log_file = open(f"logs/{server}/{channel}.txt", "r")
        for line in log_file:
            html_block += f"{line}</br>"

        print(html_block)

        return html_block

class irc_connection:
    def __init__(self, server, server_name, channel):
        self.server = server
        self.server_name = server_name
        self.channel = channel
        

def run_cherrypy():
    cherrypy.quickstart(web_logger())

def main():
    irc_connections = []
    channel = "##alicela1n"
    server = "irc.oftc.net"
    server_name = "OFTC"

    irc_connections.append(irc_connection(server, server_name, channel))

    # Bot specific information
    nickname = "nanologger"
    description = "This is a bot that logs things"

    if not os.path.exists(f"logs/{irc_connections[0].server_name}"):
        os.mkdir(f"logs/{irc_connections[0].server_name}")

    log_file = open(f"logs/{irc_connections[0].server_name}/{irc_connections[0].channel}.txt", "a+")

    # Initialize web server
    web_server_proc = Process(target=run_cherrypy, daemon=True)
    web_server_proc.start()

    irc = IRC()
    irc.connect(server, channel, nickname, description)

    print(f"Logging to: logs/{server}/{channel}.txt")

    # Main loop
    while True:
        text = irc.get_text()
        log_file.write(text.decode())
        log_file.flush()

        if "PRIVMSG" in text.decode() and channel in text.decode() and "!loggerinfo" in text.decode():
            irc.send(channel, f"{nickname} {version} Running on {platform.node()} {platform.system()} {platform.release()}")

if __name__ == "__main__":
    main()
