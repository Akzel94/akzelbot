# Copyright (c) 2018 Patrick Csikos (https://github.com/Akzel94)

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA


import random
import time
import sys
from Read import getUser, getMessage
from Socket import openSocket, sendMessage
from Initialize import joinRoom
from Settings import CHANNEL

s = openSocket()
joinRoom(s)
readbuffer = ""


def console(line):
    # gets if it is a user or twitch server
    if "PRIVMSG" in line:
        return False
    else:
        return True


def load_lists(item_type):
    items = []
    try:
        item_list = open("../config/" + item_type + "_list.txt", "r")
    except FileNotFoundError:
        print(item_type.title() + "list not found, creating new.")
    else:
        for line in item_list:
            items.append(line.strip())
        item_list.close()
    return items


def load_commands():
    commands = {}
    try:
        command_list = open("../config/command_list.txt", "r")
    except FileNotFoundError:
        print("Command list not found, creating new.")
    else:
        for command in command_list:
            listedLine = command.strip().split()
            commands[listedLine[0]] = (' ').join(listedLine[1:])
        command_list.close()
    return commands


mods, puns, quotes = load_lists("mod"), load_lists("pun"), load_lists("quote")
commands = load_commands()


def save_list(item_type):
    item_list = open(("../config/" + item_type + "_list.txt"), "w")
    if item_type == "mod":
        for mod in mods:
            print(mod, file = item_list)
    elif item_type == "pun":
        for pun in puns:
            print(pun, file = item_list)
    elif item_type == "quote":
        for quote in quotes:
            print(quote, file = item_list)
    elif item_type == "command":
        for command in commands.keys():
            print(str(command) + " " + str(commands[command]), file = item_list)
    item_list.close()


def new_item(input):
    new_item = []
    try:
        new_item = input.split()
        new_item = (" ").join(new_item[1:])
    except IndexError:
        sendMessage(s, '/w ' + user + ' Syntax: !command argument')
    else:
        return new_item


def add_command(input):
    new_command = input.split()
    if len(new_command) <= 2:
        sendMessage(s, "Syntax: '!command !newcommand command-text'")
    elif new_command[1][0] != "!":
        sendMessage(s, "Keyword must be prefixed with '!'.")
    else:
        commands[new_command[1]] = (' ').join(new_command[2:])
        sendMessage(s, "Command added.")


def del_command(input):
    dead_command = input.split()[1]
    if dead_command in commands.keys():
        del commands[dead_command]
        sendMessage(s, "Command removed.")
    else:
        sendMessage(s, "No command found.")
    save_list("command")


def add_mod(input):
    if new_item(input) == CHANNEL:
        sendMessage(s, "...Dood, really?")
    elif new_item(input) in mods:
        sendMessage(s, "User is already a moderator.")
    else:
        mods.append(new_item(input))
        sendMessage(s, "Moderator added.")


def del_mod(input):
    if new_item(input) == CHANNEL:
        sendMessage(s, "Not possible.")
    elif new_item(input) in mods:
        mods.remove(new_item(input))
        sendMessage(s, "Moderator removed.")
    save_list("mod")


def add_item(input, item_type):
    if len(new_item(input)) >= 1:
        if item_type == "pun":
            puns.append(new_item(input))
            sendMessage(s, "Pun added.")
        elif item_type == "quote":
            quotes.append(new_item(input))
            sendMessage(s, "Quote added.")
        elif item_type == "mod":
            add_mod(input)
        elif item_type == "command":
            add_command(input)
        save_list(item_type)


while True:
    try:
        readbuffer = s.recv(1024)
        readbuffer = readbuffer.decode()
        temp = readbuffer.split("\n")
        readbuffer = readbuffer.encode()
        readbuffer = temp.pop()
    except:
        temp = ""
    for line in temp:
        if line == "":
            break
        # to prevent the bot being timed out
        if "PING" in line and console(line):
            msgg = "PONG :tmi.twitch.tv\r\n".encode()
            s.send(msgg)
            print(msgg)
            break
        # get user
        user = getUser(line)
        # get message sent by user
        message = getMessage(line)
        print(user + " : " + message)
        PMSG = "/w" + user + " "


###### COMMANDS ######


        first_word = message.split()[0]

        if first_word in commands:
            sendMessage(s, str(commands[first_word]))
        if "!pun" == first_word:
            try:
                sendMessage(s, str(random.choice(puns)))
            except IndexError:
                sendMessage(s, "Sadly, I have no puns to choose from. Try adding one with !addpun")
        if "!quote" == first_word:
            try:
                sendMessage(s, str(random.choice(quotes)))
            except IndexError:
                sendMessage(s, "Sadly, I have no quotes to choose from. Try adding one with !addquote")
        if "!addquote" == first_word:
            if user in mods or user == CHANNEL:
                add_item(message, "quote")
            elif not user in mods:
                sendMessage(s, "Only moderators can append the quote list.")
        if "!addpun" == first_word:
            if user in mods or user == CHANNEL:
                add_item(message, "pun")
            elif not user in mods:
                sendMessage(s, "Only moderators can apPUNd the pun list.")
                time.sleep(0.7)
                sendMessage(s, "Sorry, that was terrible.")
        if "!command" == first_word:
            if user == CHANNEL or user in mods:
                add_item(message, "command")
            else:
                sendMessage("Only the moderators can alter commands.")
        if "!delcommand" == first_word:
            if user == CHANNEL:
                del_command(message)
            else:
                sendMessage("Only the channel owner can remove commands.")
        if "!addmod" == first_word:
            if user == CHANNEL:
                add_item(message, "mod")
            else:
                sendMessage(s, "Only the channel owner can add mods.")
        if "!delmod" == first_word:
            if user == CHANNEL:
                del_mod(message)
            else:
                sendMessage(s, "Only the channel owner can remove mods.")

        if "!quit" == first_word:
            if user == CHANNEL:
                sendMessage(s, "Exiting.")
                time.sleep(0.7)
                sys.exit(0)

        if "!kill" == first_word:
            if user != CHANNEL and user in mods:
                sendMessage(s, "You cannot kill that which is immortal.")
            elif user == CHANNEL:
                sendMessage(s, "AAAGGGHHH!")
                time.sleep(0.7)
                sys.exit(0)

    time.sleep(0.7)
