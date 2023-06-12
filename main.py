import pygame
import io
import sys
import time
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

def calculate_field(x, y):
    x -= BORDER_SIZE
    y -= BORDER_SIZE
    col = list(ascii_lowercase)[0:8][x//FIELD_SIZE]
    row = list(range(8,0,-1))[y//FIELD_SIZE]
    return col + str(row)
    


def load_svg_from_string(svg_content):
    drawing = svg2rlg(io.StringIO(svg_content))
    width, height = drawing.width, drawing.height
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

def move(board: chess.Board, move_tree: MoveTree, move_uci: str = None, move_san: str = None):
    if move_uci:
        move = chess.Move.from_uci(move_uci)
        san = board.san(move)
        try:
            res = move_tree.check_and_play_move(san)
            if res == 'gg':
                print('Nice')
        except ValueError:
            print("Wrong move")
        board.push(move)
    elif move_san:
        print(move_san)
        move = board.parse_san(move_san)
        board.push(move)
    svg_content = chess.svg.board(
            board=board,
            size=SIZE,
            lastmove=board.peek() if board.move_stack else None,
            check=board.king(board.turn) if board.is_check() else None)
    return load_svg_from_string(svg_content)

pygame.init()
screen = pygame.display.set_mode((SIZE, SIZE))
board = chess.Board()
move_tree = MoveTree('prep/as_white.txt', True)
svg_surface = move(board, move_tree)

screen.blit(svg_surface, (0, 0))
pygame.display.flip()



moves = ["e4", "d5", "exd5", "Qxd5", "Nc3", "Qe5+"][::-1]
# moves = ["e2e4", "d7d5", "e4d5", "d8d5", "b1c3", "d5e5"][::-1]

mouse_pressed = False
move_start = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not mouse_pressed:
            mouse_pressed = True
            move_start = calculate_field(*event.dict['pos'])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and mouse_pressed:
            svg_surface = move(board, move_tree, move_uci=move_start + calculate_field(*event.dict['pos']))
            screen.blit(svg_surface, (0, 0))
            pygame.display.flip()
            time.sleep(0.5)
            svg_surface = move(board, move_tree, move_san=move_tree.get_opponent_move())
            screen.blit(svg_surface, (0, 0))
            pygame.display.flip()
            mouse_pressed = False