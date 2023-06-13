import pygame
import io
import sys
import time
import random
import chess
import chess.svg

from string import ascii_lowercase
from svglib.svglib import svg2rlg 
from reportlab.graphics import renderPM

from moves import MoveTree

SIZE = 800
BORDER_SIZE = int(0.0375 * SIZE)
BOARD_SIZE = SIZE - 2 * BORDER_SIZE
FIELD_SIZE = BOARD_SIZE // 8

class OpeningPractice:

    def __init__(self, is_player_white) -> None:
        self._board = chess.Board()
        self._is_player_white = is_player_white
        self._move_tree = MoveTree('prep/as_white.txt' if is_player_white else 'prep/as_black.txt', is_player_white)
        self._cols = list(ascii_lowercase)[0:8] if is_player_white else list(ascii_lowercase)[0:8][::-1]
        self._rows = [str(i) for i in (range(8,0,-1) if is_player_white else range(1,9))]
        self.game_over = False
        if not is_player_white:
            self.play_opponent_move()

    def calculate_field(self, x, y):
        x -= BORDER_SIZE
        y -= BORDER_SIZE
        col = self._cols[x//FIELD_SIZE]
        row = self._rows[y//FIELD_SIZE]
        return col + row
    
    def get_board_surface(self):
            return load_svg_from_string(
                chess.svg.board(
                    board=self._board,
                    size=SIZE,
                    lastmove=self._board.peek() if self._board.move_stack else None,
                    check=self._board.king(self._board.turn) if self._board.is_check() else None,
                    flipped=not self._is_player_white))
    
    def move(
            self,
            move_uci: str = None,
            move_san: str = None):
        if move_uci:
            move = chess.Move.from_uci(move_uci)
            san = self._board.san(move)
            try:
                res = self._move_tree.check_and_play_move(san)
                if res == 'gg':
                    print('Nice')
                    self.game_over = True
            except ValueError:
                print("Wrong move")
                self.game_over = True
            self._board.push(move)
        elif move_san:
            move = self._board.parse_san(move_san)
            self._board.push(move)

    def play_opponent_move(self):
        move = self._move_tree.get_opponent_move()
        if move == 'gg':
            print('Nice')
            self._game_over = True
            return
        self.move(move_san=move)


def load_svg_from_string(svg_content):
    drawing = svg2rlg(io.StringIO(svg_content))
    image_data = io.BytesIO()
    renderPM.drawToFile(drawing, image_data, fmt="PNG")
    image_data.seek(0)
    image_surface = pygame.image.load(image_data, "temp.png")
    return image_surface

def maintain_aspect_ratio(new_width, new_height):
    aspect_ratio = 1
    if new_width / new_height != aspect_ratio:
        # Calculate the desired height based on the aspect ratio
        desired_height = int(new_width / aspect_ratio)
        # If the desired height is greater than the available height, adjust the width instead
        if desired_height > new_height:
            desired_width = int(new_height * aspect_ratio)
            return desired_width, new_height
        else:
            return new_width, desired_height
    else:
        return new_width, new_height

def main(is_player_white: bool):
    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE))
    game = OpeningPractice(is_player_white)
    svg_surface = game.get_board_surface()
    screen.blit(svg_surface, (0, 0))
    pygame.display.flip()

    mouse_pressed = False
    move_start_field = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not mouse_pressed:
                mouse_pressed = True
                move_start_field = game.calculate_field(*event.dict['pos'])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and mouse_pressed:
                move_end_field = game.calculate_field(*event.dict['pos'])
                game.move(move_uci=move_start_field + move_end_field)
                screen.blit(game.get_board_surface(), (0, 0))
                pygame.display.flip()
                time.sleep(0.3)
                game.play_opponent_move()
                screen.blit(game.get_board_surface(), (0, 0))
                pygame.display.flip()
                mouse_pressed = False
            elif game.game_over:
                game = OpeningPractice(is_player_white)
                svg_surface = game.get_board_surface()
                screen.blit(svg_surface, (0, 0))
                pygame.display.flip()

if __name__ == "__main__":
    is_player_white = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '-w':
            is_player_white = True
        elif sys.argv[1] == '-b':
            is_player_white = False
    else:
        is_player_white = random.randint(0,1) == 0

    main(is_player_white)