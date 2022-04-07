import socket
from _thread import *
import pickle

import logging
from server_side.game import Game
from host_info import *


class Server:
    def __init__(self, ip: str = None, port: int = None):
        self.ip = ip if ip is not None else '127.0.0.1'
        self.port = port if port is not None else 55555
        logging.info(f"Starting new server on {self.ip}:{self.port}...")
        logging.debug("---")

        self.games = {}
        self.players_count = 0
        self.connected = set()
        logging.debug(f"Creating new TCP socket using IPv4 address family...")
        # AF_INET     - IPv4
        # AF_INET6    - IPv6
        # ------------- -----
        # SOCK_STREAM - TCP
        # SOCK_DGRAM  - UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.debug(f"Binding socket to {self.ip}:{self.port}..")
        try:
            self.socket.bind((self.ip, self.port))
        except Exception:
            logging.exception("Binding exception occured", exc_info=True)
            exit()

        # 2 - The maximum length of the pending connections queue
        self.socket.listen(2)

        logging.info("Server started successfully!")
        logging.debug("---")

    def threaded_client(self, connection, player_id, game_id):
        logging.debug("Sending player id to connected client...")
        connection.send(str.encode(str(player_id)))

        while True:
            try:
                data = connection.recv(4096).decode()

                if game_id in self.games:
                    game = self.games[game_id]

                    if not data:
                        break
                    else:
                        if data == "reset":
                            game.reset_went()
                        elif data != "get":
                            game.play(player_id, data)
                            if game.both_went():
                                winner = game.get_winner()
                                result = f'Player {winner} won!' if winner in [0, 1] else 'Tie!'
                                logging.info(f"Game #{game_id}: {result}")

                        connection.sendall(pickle.dumps(game))
                else:
                    break
            except Exception as e:
                logging.error(f"Error occured: {str(e)}")
                logging.debug(f"Breaking receiving loop...")
                break

        logging.debug("Client lost connection")
        try:
            logging.debug(f"Closing the game #{game_id}")
            del self.games[game_id]
        except:
            pass
        self.players_count -= 1

        connection.close()
        logging.debug("Client connection closed.")
        logging.debug("---")

    def mainloop(self):
        logging.debug(f"Starting mainloop...")
        logging.debug("---")
        while True:
            conn, addr = self.socket.accept()

            logging.debug(f"New player connected on {addr[0]}:{addr[1]}, processing...")

            self.players_count += 1
            player_id = 0
            game_id = (self.players_count - 1) // 2
            if self.players_count % 2 == 1:
                logging.debug(f"No empty games found, creating new one with id #{game_id}...")
                self.games[game_id] = Game(game_id)
            else:
                logging.debug(f"Game #{game_id} found, setting game room ready to play...")
                self.games[game_id].ready = True
                player_id = 1

            logging.debug("---")
            logging.debug(f"Starting new thread for a client...")
            start_new_thread(self.threaded_client, (conn, player_id, game_id))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s | %(message)s')

    server = Server(IP_ADDRESS, PORT)
    server.mainloop()
