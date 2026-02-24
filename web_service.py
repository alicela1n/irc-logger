import os
import datetime
import cherrypy

class Server(object):
    name = None
    channel = None
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel

class Web_Logger(object):
    logs_dir = f"logs"
    server_dirs = os.listdir(f"{logs_dir}")
    server_dirs = list(filter(lambda a:a != ".DS_Store", server_dirs))
    servers = []
    for server_name in server_dirs:
        channel = os.listdir(f"{logs_dir}/{server_name}")
        channel = list(filter(lambda a:(a.startswith("#")), channel))
        servers.append(Server(server_name, channel))

    css = f"""body {{
                color: #660033;
                background-color:  #ffffb3;
          }}

          .time {{
                color: #660033;
                display: inline;
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

    @cherrypy.expose
    def index(self):
        html_block = f"""<body>\n"""
        for server in self.servers:
            html_block += f"""<div class="server">{server.name}</div>"""
            html_block += f"""<ul>"""
            for channel in server.channel:
                channel_name = channel.replace("#", "%23")
                html_block += f"""<li><div class="server"><a href="/log?server={server.name}&channel={channel_name}">{channel}</a></div></li>"""
            html_block += f"""</ul>"""
        
        html_block += f"""</body>\n"""
        html_site = self.header + html_block + self.footer
        return html_site

    @cherrypy.expose
    def log(self, server, channel, date="Today"):
        log_dir = f"{self.logs_dir}/{server}/{channel}"
        # Get log files
        log_files = os.listdir(f"{log_dir}") # List the log files in the server directory
        log_files = sorted(log_files, key=lambda a:os.path.getmtime(os.path.join(f"{log_dir}", a))) # Sort by modified time
        log_files = list(filter(lambda a:a != ".DS_Store", log_files)) # Filter out .DS_Store (thanks Apple)

        if os.path.isfile(f"{log_dir}/{channel}-{date}.txt") == -1:
            date = "Newest"

        # The date is a string, and Today is a keyword used to signify today's date
        if date == "Today":
            date = str(datetime.datetime.now().strftime("%m-%d-%Y"))
        elif date == "Yesterday":
            yesterday = datetime.datetime.now() - datetime.timedelta(1)
            date = str(yesterday.strftime("%m-%d-%Y"))
        elif date == "Oldest":
            date = str(log_files[0]).split("-", 1)[1]
            date = str(date.split(".txt", 1)[0])
        elif date == "Newest":
            date = str(log_files[-1]).split("-", 1)[1]
            date = str(date.split(".txt", 1)[0])
        
        log_file = open(f"{log_dir}/{channel}-{date}.txt", "r")

        html_block = f"""<body>\n"""

        # Process the log file line by line
        for line in log_file:
            if line.startswith(date):
                # Get just the time
                time = line.split(" | ", 1)[0] # Do initial split at | delimiter which I chose to delimit the date from the rest of the log entry
                time = time.split(" ", 1)[1] # Filter out date by getting the second element delimited by spaces
                line = line.split(" | ", 1)[1] # The line is the second element
            else:
                time = "" # Empty time string if there is no timestamp in log
            
            if "PRIVMSG" in line and f"{channel}" in line:
                line_segments = line.split("!", 1)
                name = line_segments[0]
                name = name.lstrip(":")
                message = line_segments[1].split(f"PRIVMSG {channel} :", 1)
                message = message[1]
                html_block += f"""<div class="time">{time}</div> <div class="name">&lt;{name}&gt;</div> <div class="msg">{message}</div></br>\n"""
            elif "JOIN" in line and f"{channel}" in line:
                line_segments = line.split("!", 1)
                name = line_segments[0]
                name = name.lstrip(":")
                html_block += f"""<div class="time">{time}</div> <div class="name">&#8594 {name}</div> <div class="msg"> joined this channel</div></br>\n"""
            elif "QUIT" in line and f"{channel}" in line:
                line_segments = line.split("!", 1)
                name = line_segments[0]
                name = name.lstrip(":")
                html_block += f"""<div class="time">{time}</div> <div class="name">&#8592 {name}</div> <div class="msg"> left this channel</div></br>\n"""

        html_block += f"""</body>\n"""
        html_site = self.header + html_block + self.footer
        return html_site

# run_cherrypy(): Function to run web service
def run_cherrypy():
    cherrypy.quickstart(Web_Logger())