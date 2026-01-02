from irc import *
import os
import platform

version = "0.01"

def main():
    channel = "##alicela1n"
    server = "irc.oftc.net"
    nickname = "nanologger"
    description = "This is a bot that logs things"

    irc = IRC()
    irc.connect(server, channel, nickname, description)

    if not os.path.exists(f"logs/{server}"):
        os.mkdir(f"logs/{server}")

    log_file = open(f"logs/{server}/{channel}.txt", "w")

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
