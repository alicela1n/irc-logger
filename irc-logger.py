from irc import *
import os
import platform
import cherrypy
import yaml
import argparse
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

                  .name {{
                        color: #EB3562;
                        display: inline;
                  }}

                  .msg {{
                        color: #660033;
                        display: inline;
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
                html_block += f"""<div class="name">&lt;{name}&gt;</div> <div class="msg">{message}</div></br>\n"""
            elif "JOIN" in line and f"{channel}" in line:
                line_segments = line.split("!", 1)
                name = line_segments[0]
                name = name.lstrip(":")
                html_block += f"""<div class="name">&#8594 {name}</div> <div class="msg"> joined this channel</div></br>\n"""
            elif "QUIT" in line and f"{channel}" in line:
                line_segments = line.split("!", 1)
                name = line_segments[0]
                name = name.lstrip(":")
                html_block += f"""<div class="name">&#8592 {name}</div> <div class="msg"> left this channel</div></br>\n"""


        html_block += f"""</body>\n"""
        html_site = header + html_block + footer
        return html_site

class irc_connection(IRC):
    proc = None
    def __init__(self, server, server_name, channel, nickname, description):
        super().__init__(server, channel, nickname, description)
        super().connect()

        self.server = server
        self.server_name = server_name
        self.channel = channel
        self.log_dir = f"logs/{self.server_name}"
        self.log_name = f"logs/{self.server_name}/{self.channel}.txt"

        # Create the log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        self.log_file = open(self.log_name, "a+")

    def write_log(self):
        text = super().get_text()
        self.log_file.write(text.decode())
        self.log_file.flush()

    def loop(self):
        while True:
            self.write_log()


# Command line argument parser
parser = argparse.ArgumentParser()
parser.add_argument("servers_file", type=str, help="A yaml file containing servers and channels to load into the logger")

# run_cherrypy(): Function to run web service
def run_cherrypy():
    cherrypy.quickstart(web_logger())

def main():
    args = parser.parse_args()
    servers_file_path = args.servers_file
    
    with open(servers_file_path, 'r') as server_file:
        servers = yaml.safe_load(server_file)

    irc_connections = []

    # Bot specific information
    nickname = "nanologger"
    description = "This is a bot that logs things"

    for server in servers:
        server_url = server['url']
        server_name = server['name']

        for channel in server['channels']:
            irc_connections.append(irc_connection(server_url, server_name, channel, nickname, description))

    # Initialize web server
    web_server_proc = Process(target=run_cherrypy, daemon=True)
    web_server_proc.start()

    connection_processes = []
    # Log each connection
    for connection in irc_connections:
        connection.proc = Process(target=connection.loop(), daemon=True)
        connection.proc.start()

if __name__ == "__main__":
    main()
