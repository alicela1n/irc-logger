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

def run_cherrypy(server, channel, log_file):
    cherrypy.quickstart(web_logger())

def main():
    channel = "##alicela1n"
    server = "irc.oftc.net"
    nickname = "nanologger"
    description = "This is a bot that logs things"

    if not os.path.exists(f"logs/{server}"):
        os.mkdir(f"logs/{server}")

    log_file = open(f"logs/{server}/{channel}.txt", "a+")

    # Initialize web server
    web_server_proc = Process(target=run_cherrypy, args=(server, channel, log_file.read()), daemon=True)
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
