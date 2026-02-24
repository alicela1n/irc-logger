from irc import *
from web_service import *
import os
import platform
import cherrypy
import yaml
import argparse
import datetime
from multiprocessing import Process

version = "0.01"

class channel_log():
    server = None
    channel = None
    date = None
    file = None
    def __init__(self, server, channel, dir, date):
        self.server = server
        self.channel = channel
        self.date = date
        self.file = open(f"{dir}/{self.channel}/{self.channel}-{self.date}.txt", "a+")

class IRC_Connection(IRC):
    date = datetime.datetime.now()
    connection_process = None
    log_process = None
    channels = []
    server_log_file = None
    channel_logs = {}

    def __init__(self, server, server_name, channels, nickname, description):
        date = datetime.datetime.now() # Initial datetime element

        # Populate variables
        self.server = server
        self.server_name = server_name
        self.channels = channels
        self.log_dir = f"logs/{self.server_name}"
        self.server_log_name = f"{self.log_dir}/{self.server_name}.txt"

        # Create the log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        self.server_log_file = open(self.server_log_name, "a+")

        for channel in self.channels:
            log = channel_log(self.server_name, channel, self.log_dir, self.date.strftime("%m-%d-%Y"))
            self.channel_logs[channel] = log

        # Initialize and start processes
        super().__init__(server, channels, nickname, description)
        self.connection_process = Process(target=super().connect(), daemon=True)
        self.log_process = Process(target=self.loop(), daemon=True)

    def write_log(self):
        text = super().get_text()
        # Sometimes multiple lines of text will be fetched from the IRC bot, split them and tack the date and time to each line.
        if "\n" in text:
            text_list = text.split("\n")
            for entry in text_list:
                # Filter out blank lines
                if entry != "":
                    self.server_log_file.write(f"{datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S |")} {entry}")
                    self.server_log_file.flush()
                    for channel in self.channels:
                        if channel in entry:
                            if "PRIVMSG" in entry and channel in entry or "JOIN" in entry and channel in entry or "QUIT" in entry and channel in entry:
                                self.channel_logs[channel].file.write(f"{datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S |")} {entry}")
                                self.channel_logs[channel].file.flush()

        # Otherwise tack on the date and time as the text is fetched
        else:
            self.server_log_file.write(f"{datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S |")} {text}")
            self.server_log_file.flush()

    def loop(self):
        while True:
            old_date = self.date
            self.date = datetime.datetime.now()

            # Create a new file for the new day
            if self.date.strftime("%m-%d-%Y") != old_date.strftime("%m-%d-%Y"):
                self.channel_log_files = []
                self.channel_logs = []
                for channel in self.channels:
                    log = channel_log(self.server_name, channel, self.log_dir, self.date.strftime("%m-%d-%Y"))
                    self.channel_logs[channel] = log
            
            self.write_log()


# Command line argument parser
parser = argparse.ArgumentParser()
parser.add_argument("servers_file", type=str, help="A yaml file containing servers and channels to load into the logger")

# main(): Main function
def main():
    args = parser.parse_args()
    servers_file_path = args.servers_file
    
    with open(servers_file_path, 'r') as server_file:
        servers = yaml.safe_load(server_file)

    # Initialize web server
    web_server_proc = Process(target=run_cherrypy, daemon=True)
    web_server_proc.start()

    # Bot specific information
    nickname = "nanologger"
    description = "This is a bot that logs things"

    irc_connections = []
    for server in servers:
        server_url = server['url']
        server_name = server['name']
        server_channels = server['channels']

        irc_connections.append(IRC_Connection(server_url, server_name, server_channels, nickname, description))

        # Start each process
        for connections in irc_connections:
            connection.connection_process.start()
            connection.log_process.start()

if __name__ == "__main__":
    main()
