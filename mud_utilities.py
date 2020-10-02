import numpy as np

class utilities:
    def __init__(self, players):
        """
            Utility methods use in a game.
            players = dict object of players, ids, and player attributes
        """
        self.players = players

    def message_all(self, message):
        for id_iter in self.players.keys():
            # mud.send_message(id_iter, message)
            print(id_iter, message)

    def notify_room(self, message):
        for id_iter in players.keys():
            if players[id_iter]['room'] == current_room:
                # mud.send_message(id_iter, message)
                print(id_iter, message)

    def enemy_hazard(self, victim_id):
        notify_room("a newly hatched creature lunges out of the darkness")

        notify_room("{} ")
