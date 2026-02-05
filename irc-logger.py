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
    def log(self, server, channel):
        html_block = ""
        log_file = open(f"logs/{server}/{channel}.txt", "r")
        css = f"""body {{
                        color: #660033;
                        background-color:  #ffffb3;
                  }}
               """
        header = f"""<html>\n
                         <head>\n
                         <style>\n
                                {css}\n
                         </style>\n
                         </head>\n
                  """
        footer = f"""</html>\n"""
        html_block = f"""<body>\n"""

        # Process the log file line by line
        for line in log_file:
            if "PRIVMSG" in line and f"{channel}" in line:
                line_segments = line.split("!", 1)
                name = line_segments[0]
                name = name.lstrip(":")
                message = line_segments[1].split(f"PRIVMSG {channel} :", 1)
                message = message[1]
                print(f"{name}\n {message}")
                html_block += f"""&lt;{name}&gt; {message}</br>\n"""

        html_block += f"""</body>\n"""
        html_site = header + html_block + footer
        return html_site

class irc_connection(IRC):
    def __init__(self, server, server_name, channel, nickname, description):
        super().__init__(server, channel, nickname, description)
        super().connect()

        self.server = server
        self.server_name = server_name
        self.channel = channel
        self.log_dir = f"logs/{self.server_name}"
        self.log_name = f"logs/{self.server_name}/{self.channel}.txt"

def run_cherrypy():
    cherrypy.quickstart(web_logger())

def main():
    irc_connections = []
    channel = "##alicela1n"
    server = "irc.oftc.net"
    server_name = "OFTC"

    # Bot specific information
    nickname = "nanologger"
    description = "This is a bot that logs things"

    irc_connections.append(irc_connection(server, server_name, channel, nickname, description))

    if not os.path.exists(f"logs/{irc_connections[0].server_name}"):
        os.mkdir(f"{irc_connections[0].log_dir}")

    log_file = open(f"{irc_connections[0].log_name}", "a+")

    # Initialize web server
    web_server_proc = Process(target=run_cherrypy, daemon=True)
    web_server_proc.start()

    print(f"Logging to: {irc_connections[0].log_dir}")

    # Main loop
    while True:
        text = irc_connections[0].get_text()
        log_file.write(text.decode())
        log_file.flush()

        if "PRIVMSG" in text.decode() and channel in text.decode() and "!loggerinfo" in text.decode():
            irc_connections[0].send(f"{nickname} {version} Running on {platform.node()} {platform.system()} {platform.release()}")

if __name__ == "__main__":
    main()
