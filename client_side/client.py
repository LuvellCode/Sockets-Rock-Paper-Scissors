import pygame
import logging

from client_side.network import Network


class Color:
    # R  G  B
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    AQUA = (0, 255, 255)


class Font:
    def __init__(self, name: str = "comicsans", size: int = 50):
        pygame.font.init()
        self.font = pygame.font.SysFont(name, size)

    def render(self, string, color, *args, **kwargs):
        return self.font.render(string, True, color, *args, **kwargs)

    def black(self, string, *args, **kwargs):
        return self.render(string, Color.BLACK, *args, *kwargs)

    def white(self, string, *args, **kwargs):
        return self.render(string, Color.WHITE, *args, *kwargs)

    def gray(self, string, *args, **kwargs):
        return self.render(string, Color.GRAY, *args, *kwargs)

    def red(self, string, *args, **kwargs):
        return self.render(string, Color.RED, *args, *kwargs)

    def aqua(self, string, *args, **kwargs):
        return self.render(string, Color.AQUA, *args, *kwargs)


class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, window, font):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        text = font.white(self.text)
        window.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


class Display:
    BUTTONS = [
        Button("Rock", 50, 500, Color.BLACK),
        Button("Scissors", 250, 500, Color.RED),
        Button("Paper", 450, 500, Color.GREEN)
    ]

    def __init__(self, width: int = 700, height: int = 700, caption: str = "Client",
                 font_name: str = "comicsans", font_size: int = 50):
        self.caption("Client")

        self.font = Font(font_name, font_size)
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height))

    def clear(self):
        self.window.fill(Color.GRAY)

    def redraw(self, game, player_id):
        self.clear()

        if not (game.connected()):
            text = self.font.red("Waiting for Player...", True)
            self.window.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))
        else:
            text = self.font.aqua("Your Move")
            self.window.blit(text, (80, 200))

            text = self.font.aqua("Opponents")
            self.window.blit(text, (380, 200))

            move1 = game.get_player_move(0)
            move2 = game.get_player_move(1)
            if game.both_went():
                text1 = self.font.black(move1)
                text2 = self.font.black(move2)
            else:
                if game.p1Went and player_id == 0:
                    text1 = self.font.black(move1)
                elif game.p1Went:
                    text1 = self.font.black("Locked In")
                else:
                    text1 = self.font.black("Waiting...")

                if game.p2Went and player_id == 1:
                    text2 = self.font.black(move2)
                elif game.p2Went:
                    text2 = self.font.black("Locked In")
                else:
                    text2 = self.font.black("Waiting...")

            if player_id == 1:
                self.window.blit(text2, (100, 350))
                self.window.blit(text1, (400, 350))
            else:
                self.window.blit(text1, (100, 350))
                self.window.blit(text2, (400, 350))

            for btn in self.BUTTONS:
                btn.draw(self.window, self.font)

        pygame.display.update()

    def result(self, text: str):
        self.clear()

        text = self.font.red(text)

        self.window.blit(text, (
            self.width / 2 - text.get_width() / 2,
            self.height / 2 - text.get_height() / 2
        ))

    def caption(self, text: str):
        pygame.display.set_caption(text)


class Client:
    def __init__(self):
        self.show_menu = True
        self.main_script = True
        self.id = None
        self.dp = Display()
        logging.debug("Entering main menu...")
        self.menu()

    def menu(self):
        clock = pygame.time.Clock()

        while self.show_menu:
            clock.tick(60)

            self.dp.clear()
            text = self.dp.font.red("Click to Play!")

            self.dp.window.blit(text, (self.dp.width / 2 - round(text.get_width() / 2), self.dp.height / 2 - round(text.get_height() / 2)))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.show_menu = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.main()

    def main(self):
        logging.debug("Executing main script...")
        logging.debug("---")
        run = True
        clock = pygame.time.Clock()
        n = Network()

        player_id = int(n.get_player_id())
        logging.debug(f"Received player id: {player_id}")

        while run:
            clock.tick(60)
            try:
                game = n.send("get")
                self.dp.caption(f"Client #{player_id} | Room: #{game.id}")
            except:
                run = False
                break

            if game.both_went():
                self.dp.redraw(game, player_id)
                pygame.time.delay(500)

                game.get_winner()

                if (game.winner == 1 and player_id == 1) or (game.winner == 0 and player_id == 0):
                    text = "You Won!"
                elif game.winner == -1:
                    text = "Tie!"
                else:
                    text = "You Lost :("

                logging.debug(f"Game result: {text}")
                self.dp.result(text)

                try:
                    logging.debug("Trying to reset the game..")
                    game = n.send("reset")
                except:
                    run = False
                    break

                pygame.display.update()
                pygame.time.delay(2000)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    break

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for btn in self.dp.BUTTONS:
                        if btn.click(pos) and game.connected():
                            success = False

                            if player_id == 0:
                                if not game.p1Went:
                                    success = True
                            else:
                                if not game.p2Went:
                                    success = True

                            if success:
                                logging.debug(f"Sent: {btn.text}")
                                n.send(btn.text)

            if run:
                self.dp.redraw(game, player_id)

        logging.error("Couldn't get game.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s | %(message)s')
    Client()
