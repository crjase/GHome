import os
import time
import sys
import configuration
import tkinter as tk

from colorama import Fore
from googlecontroller import GoogleAssistant
from tkinter import filedialog as fd


# Initialize Configuration
config = configuration.Configuration()

# Global Variables
host = "host"
port = config.port
err = ""
feedback = ""


# Functions
def clear():
    try:
        os.system("cls")
    except:
        os.system("clear")


# Get array of split netstat data
ip_addr = ""
for mess in os.popen(f'netstat -na | find "{port}"'):
    ip_addr = mess.split(" ")


# Filter out the string I want
for c in range(len(ip_addr)):
    if f"{port}" in ip_addr[c]:
        # remove port at end
        ip = ip_addr[c].split(f":{port}")
        # set host to filtered ip
        host = ip[0]


# Now all that's left to do is...
# USE THE IP MALICIOUSLY HAHAHA

class Controller:
    def __init__(self):
        self.home = GoogleAssistant(host=host)
        self.home_volume = 0

    def say(self, message, lang=config.lang, speed=config.speed):
        # Say message
        self.home.say(message, lang=lang, speed=speed)

    def volume(self, percent):
        # Convert percent to int
        try:
            percent = int(percent)
        except ValueError:
            err = "Invalid value : Please use a number for this operation."
            return err
        # Set GHome volume
        if percent <= 100 and percent >= 0:
            # Set volume value
            self.home_volume = percent
            self.home.volume(percent)
        else:
            err = "Please use a value ranging from 0-100"
            return err

    def play(self, url, stop=False):
        if not stop:
            self.home.play(url, ignore=False)
        if stop:
            self.home.play("", ignore=False)

    def serve_media(self, path, name):
        self.home.serve_media(name, path)


# Use Controller
def control():

    global err, feedback

    command_list = {
        "say": {
            "description": "Make google home say something",
            "example": "say \"hello world\""
        },
        "volume": {
            "description": "Set google home volume",
            "example": "volume 100"
        },
        "play": {
            "description": "Play an audio file from a website",
            "example": "play \"https://website.com/audio.mp3\""
        },
        "playlocal": {
            "description": "Play an audio file from local files (not working yet)",
            "example": "playlocal"
        }
    }

    print("Google Home Troller By Crjase")
    print("------------------------------")
    print(f"{Fore.RED}{err}{Fore.RESET}")
    print(f"{Fore.CYAN}{feedback}{Fore.RESET}")
    print("")
    print(Fore.CYAN + "Commands" + Fore.RESET)
    print("________")
    print("")

    for command in command_list:
        print(f"| {Fore.CYAN}{command}{Fore.RESET}")
        print(f"| {Fore.MAGENTA}{command_list[command]['description']}{Fore.RESET}")
        print(f"-> {command_list[command]['example']}")
        print("")

    print("\n\n")
    inp = input("> ").lower()
    # Get arguments
    args = inp.split()
    # Clear error message
    err = ""
    feedback = ""

    for command in command_list:
        if command in inp:
            # get args length integar
            args_len = len(args)
            # execute commands
            try:
                # -- say() --
                if args[0] == "say":
                    if '"' in args[1] and '"' in args[-1]:
                        # Filter out unwanted items
                        for arg in range(len(args)):
                            if '"' in args[arg]:
                                args[arg] = args[arg].replace('"', "")
                        # Combine into whole scentance
                        msg = ' '.join(args)
                        msg = msg.replace("say ", "")
                        # Send to Controller()
                        Controller().say(msg)
                        # Continue pass other args
                        continue
                    elif args[2]:
                        err = f"The command {Fore.YELLOW}say{Fore.RED} must have quotation {Fore.YELLOW}\"\"{Fore.RED}\nExample: {Fore.CYAN}say \"hello world\""
                        continue

                # -- volume() --
                if args[0] == "volume":
                    if args[1]:
                        # Complain if more than one argument
                        try:
                            args[2]
                            err = f"The command {Fore.YELLOW}volume{Fore.RED} requires only one argument\nExample: {Fore.CYAN}volume 100"
                            continue
                        except:
                            pass
                        # Catch if value not an integar
                        try:
                            vol = int(args[1])
                            if vol >= 0 and vol <= 100:
                                Controller().volume(vol)
                            else:
                                err = "Volume can only be in the range 0-100"
                        except ValueError:
                            err = f"The command {Fore.YELLOW}volume{Fore.RED} requires an integer\nExample: {Fore.CYAN}volume 100"

                # -- play() --
                # https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3
                if args[0] == "play":
                    if '"' in args[1] and '"' in args[-1]:
                        # Filter out unwanted items
                        for arg in range(len(args)):
                            if '"' in args[arg]:
                                args[arg] = args[arg].replace('"', "")
                        # Combine into whole scentance
                        url = ' '.join(args)
                        url = url.replace("play ", "")
                        # Send to Controller()
                        if url.lower() == "stop":
                            feedback = f"{Fore.MAGENTA}Music Stopped{Fore.RESET}"
                            Controller().play(url, stop=True)
                        elif "http" not in url.lower():
                            err = f"Invalid url. If you are looking to stop the music, please type {Fore.YELLOW}play \"stop\""
                            continue
                        else:
                            feedback = f"{Fore.MAGENTA}Music is Now Playing{Fore.RESET}"
                            Controller().play(url, stop=False)
                        continue
                    elif args[2]:
                        err = f"The command {Fore.YELLOW}play{Fore.RED} must have quotation {Fore.YELLOW}\"\"{Fore.RED}\nExample: {Fore.CYAN}play \"url here\""
                        continue

                # -- serve_media() --
                if args[0] == "playlocal":
                    try:
                        args[2]
                        err = f"The command {Fore.YELLOW}playlocal{Fore.RED} requires no arguments\nExample: {Fore.CYAN}playlocal"
                        continue
                    except:
                        pass

                    root = tk.Tk()
                    root.withdraw()

                    filetypes = (
                        ('audio files', '*.mp3 *.wav'),
                        ('All files', '*.*')
                    )

                    filename = fd.askopenfilename(
                        title='Open a file',
                        initialdir='/',
                        filetypes=filetypes)

                    fpath = os.path.split(filename)[0]
                    fname = os.path.split(filename)[1]

                    Controller().serve_media(name=fname, path=fpath)

                    continue

            except SyntaxError:
                err = "Error: Invalid Arguments\nLook at the displayed commands for examples"
            except IndexError:
                err = "Error: Invalid Number of Arguments\nLook at the displayed commands for examples"
        elif inp != "":
            simplified_commandList = []
            for command2 in command_list:
                simplified_commandList.append(command2)
            if args[0] not in simplified_commandList:
                err = "Command Not Found"


# FOREVER LOOP
while True:
    time.sleep(0.1)
    clear()
    control()