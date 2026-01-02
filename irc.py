import socket
import sys

class IRC:
    irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, channel, message):\
            self.irc.send(f"PRIVMSG {channel} {message}\n".encode('utf-8'))

    def connect(self, server, channel, botnick, botdesc):
        print(f"Connecting to {server}")
        self.irc.connect((server, 6667))
        self.irc.send(f"USER {botnick} {botnick} {botnick} :{botdesc}\n".encode('utf-8'))
        self.irc.send(f"NICK {botnick}\n".encode('utf-8'))
        self.irc.send(f"JOIN {channel}\n".encode('utf-8'))

    def get_text(self):
        text = self.irc.recv(2020)
        if text.decode().find('PING'):
            self.irc.send(f"PONG {text.decode().split()[1]}\r\n".encode('utf-8')) 
        return text
