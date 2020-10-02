#!/usr/bin/env python

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

Some ideas for things to try adding:
    * More rooms to explore
    * An 'emote' command e.g. 'emote laughs out loud' -> 'Mark laughs
        out loud'
    * A 'whisper' command for talking to individual players
    * A 'shout' command for yelling to players in all rooms
    * Items to look at in rooms e.g. 'look fireplace' -> 'You see a
        roaring, glowing fire'
    * Items to pick up e.g. 'take rock' -> 'You pick up the rock'
    * Monsters to fight
    * Loot to collect
    * Saving players accounts between sessions
    * A password login
    * A shop from which to buy items

author: Mark Frimston - mfrimston@gmail.com
"""

import time
import numpy as np
from collections import Counter

# import the MUD server class
from mudserver import MudServer


# structure defining the rooms in the game. Try adding more rooms to the game!
starting_var = "peace"

event_list  = ["A pressurized line has ruptured",
                        "An air lock has broken",
                        "Electrical lines are damaged",
                        "Exposed wires have shorted",
                        "Important display panels are cracked",
                        "A large fire has broken out and is spreading",
                        "Interior heat shields have broken off",
                        "Vital systems are shutting down",
                        "Multiple electrical systems have failed",
                        "A critical drop in cabin pressure has occured",
                        "A series of small explosions have caused damage",
                        "A power coupling has untethered",
                        "Falling debris has trapped crew members"]

location_list = ["cargo hold",
                "infirmary",
                "biology labratory",
                "service corridor",
                "maintenance crawlspace",
                "observatory",
                "armory"
                "cockpit",
                "command bridge",
                "living quarters",
                # "logistics facility",
                # "dormatories",
                "dining hall",
                # "tech labratory",
                # "engine room alpha",
                # "engine room beta",
                # "fore passage",
                # "aft passageway",
                # ,
                # "passenger quarters",
                # "warpdrive containment unit",
                # "captains quarters",
                # "long-distance communications hub",
                # "short-field communications console room"
                ]

rooms = {
    "hub": {
        "description": "Your party stands around a table discussing how to keep yourselves alive",
        "votes": [],
        "exits": {},
        "status": "Fixed",
        "hazards" : [],
        "items": None
    }
}

for location in location_list:
    rand_event = np.random.randint(0, len(event_list))
    event = event_list[rand_event]
    description = f"{event} in the {location}"
    rooms[location] = {'description':description,
                        "votes":[]
                        , 'status': 'Broken'
                        , "exits": {"hub":'hub'}
                        , "hazards" : []
                        , "items": []}

needed_repairs = len(location_list)


#Generate Hub Exits:
for k in rooms.keys():
    if k != 'hub':
        rooms['hub']['exits'][k] = k


# stores the players in the game
players = {}

# start the server
mud = MudServer()


#Utility functions
def message_room(msg):
    # go through every player in the game
    for pid, pl in players.items():
        # if they're in the same room as the player
        if players[pid]["room"] == players[id]["room"]:
            # send them a message telling them what the player said
            mud.send_message(pid, msg)

def message_all(msg):
    # go all the players in the game
    for pid, pl in players.items():
        # send each player a message to tell them about the new player
        mud.send_message(pid, msg)

def message_player(id,msg):
    for pid,pl in players.items():
        if players[pid] == id:
            mud.send_message(pid,msg)

def damage_player(id,ammount,msg):
    for pid, pl in players.items():
        if players[pid] == id:
            players[pid]['health'] = players[pid]['health'] - ammount
            mud.send_message(pid,msg)

def damage_room(ammount,msg):
    for pid, pl in players.items():
        # if they're in the same room as the player
        if players[pid]["room"] == players[id]["room"]:
            players[pid]['health'] = players[pid]['health'] - amount
            # send them a message telling them what the player said
            mud.send_message(pid, msg)


# main game loop. We loop forever (i.e. until the program is terminated)
while True:

    # pause for 1/5 of a second on each loop, so that we don't constantly
    # use 100% CPU time
    time.sleep(0.2)

    # 'update' must be called in the loop to keep the game running and give
    # us up-to-date information
    mud.update()


    # go through any newly connected players
    for id in mud.get_new_players():

        # add the new player to the dictionary, noting that they've not been
        # named yet.
        # The dictionary key is the player's id number. We set their room to
        # None initially until they have entered a name
        # Try adding more player stats - level, gold, inventory, etc
        players[id] = {
            "name": None,
            "room": None,
            "health": 100,
            "sabateur" : 'No',
            "temp" : np.random.randint(979, 987)/10,
        }

        # send the new player a prompt for their name
        mud.send_message(id, "What is your name?")

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # go through all the players in the game
        for pid, pl in players.items():
            # send each player a message to tell them about the diconnected
            # player
            mud.send_message(pid, "{} quit the game".format(
                                                        players[id]["name"]))

        # remove the player's entry in the player dictionary
        del(players[id])

    # go through any new commands sent from players
    for id, command, params in mud.get_commands():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue
        if players[id]['health'] <= 0:
            mud.send_message(id, "You Have Died. GAME OVER")

        #select random spy
        # for np.random.randint(0, len(players)):



        # if the player hasn't given their name yet, use this first command as
        # their name and move them to the starting room.
        elif players[id]["name"] is None:

            players[id]["name"] = command
            players[id]["room"] = "hub"

            # go all the players in the game
            for pid, pl in players.items():
                # send each player a message to tell them about the new player
                mud.send_message(pid, "{} entered the game".format(
                                                        players[id]["name"]))

            # send the new player a welcome message
            mud.send_message(id, "Welcome to the game, {}. ".format(
                                                           players[id]["name"])
                             + "Type 'help' for a list of commands. Have fun!")

            # send the new player the description of their current room
            mud.send_message(id, rooms[players[id]["room"]]["description"])

        # each of the possible commands is handled below. Try adding new
        # commands to the game!

        # 'help' command
        elif command == "help":

            # send the player back the list of possible commands
            if players[id]['sabateur'] != "Yes":
                mud.send_message(id, "Player Commands:")
                mud.send_message(id, "  say <message>  - Says something out loud, "
                                     + "e.g. 'say Hello'")
                mud.send_message(id, "  look           - Examines the "
                                     + "surroundings, e.g. 'look'")
                mud.send_message(id, "  go <exit>      - Moves through the exit "
                                     + "specified, e.g. 'go outside'")
                mud.send_message(id, "  ship_status <exit> - Check Room Statuses; Must be in 'hub'"
                                     + "specified, e.g. 'ship_status'")
                mud.send_message(id, "  dance      - Causes fun times to ensue "
                                     + "specified, e.g. 'dance'")
                mud.send_message(id, "  namechange - Causes fun times to ensue "
                                     + "specified, e.g. 'dance'")
                mud.send_message(id, "  repair      - Attempts to fix a current room "
                                     + "specified, e.g. 'repair'")
                mud.send_message(id, "  attack      - Cause harm to another player in same room "
                                     + "specified, e.g. 'attack <player_name>'")
            else:
                mud.send_message(id, "Player Commands:")
                mud.send_message(id, "  say <message>  - Says something out loud, "
                                     + "e.g. 'say Hello'")
                mud.send_message(id, "  look           - Examines the "
                                     + "surroundings, e.g. 'look'")
                mud.send_message(id, "  go <exit>      - Moves through the exit "
                                     + "specified, e.g. 'go outside'")
                mud.send_message(id, "  ship_status <exit> - Check Room Statuses; Must be in 'hub'"
                                     + "specified, e.g. 'ship_status'")
                mud.send_message(id, "  dance      - Causes fun times to ensue "
                                     + "specified, e.g. 'dance'")
                mud.send_message(id, "  repair      - Attempts to fix a current room "
                                     + "specified, e.g. 'repair'")
                mud.send_message(id, "  attack      - Cause harm to another player in same room "
                                     + "specified, e.g. 'attack <player_name>'")
                mud.send_message(id, "  sabotage      - Attempts to damage a current room "
                                     + "specified, e.g. 'repair'")
                mud.send_message(id, "  hatch_enemy    - Places an enemy which will ambush players once  "
                                     + "specified, e.g. 'attack <player_name>'")
        # 'say' command
        elif command == "say":
            msg = params
            message_room(msg)


        # 'look' command
        elif command == "look":

            # store the player's current room
            rm = rooms[players[id]["room"]]

            # send the player back the description of their current room
            mud.send_message(id, rm["description"])

            playershere = []
            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # ... and they have a name to be shown
                    if players[pid]["name"] is not None:
                        # add their name to the list
                        playershere.append(players[pid]["name"])

            # send player a message containing the list of players in the room
            mud.send_message(id, "Players here: {}".format(
                                                    ", ".join(playershere)))

            # send player a message containing the list of exits from this room
            mud.send_message(id, "Exits are: {}".format(
                                                    ", ".join(rm["exits"])))

        # 'go' command
        elif command == "go":

            # store the exit name
            ex = params.lower()

            # store the player's current room
            rm = rooms[players[id]["room"]]

            # if the specified exit is found in the room's exits list
            if ex in rm["exits"]:

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] \
                            and pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, "{} left via exit '{}'".format(
                                                      players[id]["name"], ex))

                # update the player's current room to the one the exit leads to
                players[id]["room"] = rm["exits"][ex]
                rm = rooms[players[id]["room"]]

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] \
                            and pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        mud.send_message(pid,
                                         "{} arrived via exit '{}'".format(
                                                      players[id]["name"], ex))

                # send the player a message telling them where they are now
                mud.send_message(id, "You arrive at '{}'".format(
                                                          players[id]["room"]))

            # the specified exit wasn't found in the current room
            else:
                # send back an 'unknown exit' message
                mud.send_message(id, "Unknown exit '{}'".format(ex))

            # When the player enters the room, check for hazards
            if len(rooms[players[id]['room']]['hazards']) != 0 and players[id]['sabateur'] != 'Yes':
                print("check eggs")
                if 'enemy' in rooms[players[id]['room']]['hazards']:
                    mud.send_message(id, "you hear the click of carapaced feet skitter across the metal floor")
                    time.sleep(2)
                    if np.random.randint(0,10) >=7:
                        players[id][health] -= 30
                        mud.send_message(id, "A newly hatched creature lunged from the shadows. Take 30dmg")
                        for id_iter in players.keys():
                            if players[id_iter]['room'] == current_room:
                                mud.send_message(id_iter, "a creature springs from the darkness attacking {}".format(players[id]['name']))
                                hzd_name = rooms[players[id]['room']]['hazards']
                                rooms[players[id]['room']]['hazards'].pop(hzd_name)
                    else:
                        mud.send_message(id, "Your presense appears to be unnoticed. . . for now")

            #If no hazards do nothing
            else:
                pass

        # some other, unrecognised command
        elif command == "dance":
            mud.send_message(id, "you begin dancing a merry jig")

        elif command == "playerstatus":
            print(players)

        elif command == "myhealth":
            # Check current health
            mud.send_message(id, "you currently have {} health remaining".format(str(players[id]['health'])))

        elif command == "view_inventory":
            inventory_list = Counter(players[id]['items'])
            mud.send_message(id, "You currently have: ")
            for item, count in inventory_list.items():
                mud.send_message(id, "{} :: {}".format(items, count))

        elif command == "ship_status":
            if players[id]['room'] != 'hub':
                mud.send_message(id, "ship status can only be checked in the hub")
            else:
                for r in rooms.keys():
                    mud.send_message(id, "{} :: {}".format(r, rooms[r]['status']))

        elif command == "namechange":
            previous_name = players[id]['name']
            players[id]['name'] = params
            for id in players.keys():
                mud.send_message(id, "{} will hence forth be called {}".format(previous_name, params))

            # if params == "Capt. Reynolds":
            #     mud.send_message(id, "Welcome Back Sir")

            else:
                mud.send_message(id, "The hunt has already begun")

        elif command == "repair":
            current_room = players[id]['room']
            if rooms[current_room]['status'] != "Broken":
                mud.send_message(id, "Room is Doing Fine. Must be a False Alarm")
            else:
                occupants = []
                for id_iter in players.keys():
                    if players[id_iter]['room'] == current_room:
                        mud.send_message(id_iter, "{} is attempting to conduct repairs in the {}".format(players[id]['name'], current_room))

                mud.send_message(id, "Repairs in progress - 3")
                time.sleep(1.5)
                mud.send_message(id, "Repairs in progress - 2")
                time.sleep(1.5)
                mud.send_message(id, "Repairs in progress - 1")
                time.sleep(1.5)

                success_randint = np.random.randint(0,100)
                if success_randint >= 60: #percent chance of succeeding
                    rooms[players[id]['room']]['status'] = 'Repaired'
                    rooms[players[id]['room']]['description'] = 'Everything appears in place and in good working condition'
                    for id_iter in players.keys():
                        if players[id_iter]['room'] == current_room:
                            mud.send_message(id_iter, "{} has successfully repaired the {}".format(players[id]['name'], current_room))
                            needed_repairs -= 1
                            if needed_repairs <= 0:
                                for id_iter in players.keys():
                                    mud.send_message(id_iter, "The Crew has won the game")
                            else:
                                for id_iter in players.keys():
                                    mud.send_message(id_iter, "{} rooms remaining to be repaired".format(needed_repairs))
                else:
                    players[id]['health'] -= 10
                    mud.send_message(id, "You have failed to successfully make repairs and are hurt in the process. you take 10 damage")
                    if players[id]['health'] == 0:
                        for id_iter in players.keys():
                            mud.send_message(id_iter, "{} has died in the {} attepting to conduct repairs".format(players[id]['name'], current_room))
                    for id_iter in players.keys():
                        if players[id_iter]['room'] == current_room:
                            mud.send_message(id_iter, "{} has failed to make repairs in the {}".format(players[id]['name'], current_room))

        elif command == "attack":
            # Deal damage to another player:
            for i in players.keys():
                if players[i]['name'] == params:
                    victim_id = i
            if players[id]['room'] == players[victim_id]['room'] and players[id]['room']!= 'infirmary' and players[id]['room']!= 'hub' :

                if players[id]['sabateur'] == 'Yes':
                    mud.send_message(id, "Sneaking from the shadows, you attack {}".format(params))
                else:
                    mud.send_message(id, "You attack {} !!!".format(params))

                players[victim_id]['health'] -= 20
                mud.send_message(victim_id, "You are attacked from the shadows !!! Take 20dmg!!!")
                players[victim_id]['room'] = 'infirmary'
                time.sleep(2)
                mud.send_message(victim_id, "You have been found by another crew member and you awake in the infirmary")
                if players[victim_id]['health'] <=0:
                    for id_iter in players.keys():
                        mud.send_message(id_iter, "{} has died in the {} after being ambushed".format(players[id]['name'], current_room))
            else:
                mud.send_message(id, "This room is too well guarded to make an attack here")

# Weapon specific methods

        elif command == "torch_room":
            if "flamethrower" in players[id]['items'] and "fuel" in players[id]['items']:
                current_room = players[id]['room']
                for id_iter in players.keys():
                    if players[id_iter]['room'] == current_room:
                        mud.send_message(id_iter, "{} flicks his zippo and with a grin. . . ".format(players[id]['name']))
                        time.sleep(.5)
                        mud.send_message(id_iter, "ignites his flamethrower".format(players[id]['name']))
                        if id != id_iter:
                            mud.send_message(id_iter, "Caught in the rampant flames, you take 10 damage")
                            players[id_iter]['health'] -= 10
                rooms[current_room]['hazards'] = []
                mud.send_message(id, "You have cleared the room of enemies")
                players[id]["items"].remove("fuel")
                if "fuel" not in players[id]["items"]:
                    mud.send_message(id, "however you are out of fuel")



# Sabateur Commands
        elif command == "sabotage": #Method of breaking a room
            if players[id]["sabateur"] != 'Yes':
                mud.send_message(id, "Why would you want to wreck your own ship?")
            else:
                mud.send_message(id, "A few broken hoses, a few loose wire and . . .BOOM !!!")
                rooms[players[id]['room']]['status'] = "Broken"
                needed_repairs += 1

        elif command == "hatch_enemy": #place an enemy hatchling in a room
            if players[id]['sabateur'] != 'Yes':
                mud.send_message(id, "You are not an alien")
            else:
                current_room = players[id]['room']
                rooms[current_room]['hazards'].append('enemy')
                mud.send_message(id, "You gently place an egg in the shadows of the room")

        elif command == "enemystatus":
            if players[id]['sabateur'] != "Yes":
                mud.send_message(id, "Enemies lurk in the shadows just outside of view")
            else:
                for r in rooms.keys():
                    if len(rooms[r]['hazards']) > 0:
                        mud.send_message(id, "{} Enemies in {}".format(len(rooms[r]['hazards']), r))

# Admin Commands
        elif command == "roomstatus":
            if players[id]['name'] == "Capt. Reynolds":
                print(rooms[players[id]['room']])


        elif command == "beginthechase":
            if starting_var == 'peace':
                if players[id]['name'] != "Capt. Reynolds":
                    mud.send_message(id, "Insufficient Authority")
                else:
                    mud.send_message(id, "Begin the Hunt")
                    player_ids = list(players.keys())
                    if len(player_ids) == 0:
                        players[0]['sabateur'] = "Yes"
                        break
                    else:
                        rand_int = np.random.randint(0, len(players.keys()))
                        players[player_ids[rand_int]]['sabateur'] = "Yes"
                        mud.send_message(rand_int, "You are the sabateur")
                        starting_var = "war"


        else:
            # send back an 'unknown command' message
            mud.send_message(id, "Unknown command '{}'".format(command))
