import socket
import sys
import datetime

class IRC:
    irc = socket.socket()

    def __init__(self, server, channel, botnick, botdesc):
        self.server = server
        self.channel = channel
        self.botnick = botnick
        self.botdesc = botdesc

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, message):
            self.irc.send(f"PRIVMSG {self.channel} {message}\n".encode('utf-8'))

    def connect(self):
        print(f"Connecting to {self.server}")
        self.irc.connect((self.server, 6667))
        self.irc.send(f"USER {self.botnick} {self.botnick} {self.botnick} :{self.botdesc}\n".encode('utf-8'))
        self.irc.send(f"NICK {self.botnick}\n".encode('utf-8'))
        self.irc.send(f"JOIN {self.channel}\n".encode('utf-8'))

    def get_text(self):
        text = self.irc.recv(2020).decode()
        text = f"{text}"
        if text.find("PING") != -1:
            self.irc.send(f"PONG {text.split()[1]} \r\n".encode('utf-8'))
        return text
