import re
from time import time
from typing import List
from treelib import Node, Tree
import random

random.seed(time())

class MoveTree:

    def __init__(self, move_list_path: str, player_move: bool) -> None:
        tree = Tree()
        self._player_move = player_move
        # allows multiple starting moves
        tree.create_node('+', hash(''))
        with open(move_list_path, 'r') as f:
            line = f.readline()
            while line.strip() != '':
                moves = [item.strip() for item in re.split(r'\d+\.', line) if item != '']
                nodes = []
                for i, move in enumerate(moves):
                    nodes.extend([('w' + str(i + 1), move.split()[0]), ('b' + str(i + 1), move.split()[1])])

                for i in range(len(nodes)):
                    tag=nodes[i][1]
                    parent_id = hash("".join([n[1] for n in nodes[:i]]))
                    identifier = hash("".join([n[1] for n in nodes[:i+1]]))
                    if identifier not in tree:
                        if player_move and len(tree.children(parent_id)) >= 1:
                            print(identifier, parent_id)
                            raise ValueError('Multiple responses for same move')
                        else:
                            tree.create_node(tag, identifier, parent=parent_id)
                    
                    player_move = not player_move
                
                line = f.readline()

        self._tree = tree
        self._current_nid = hash('')
            
    def get_opponent_move(self) -> str:
        children = self._tree.children(self._current_nid)
        if not children:
            return "gg"
        print(children)
        next = random.choice(children)
        self._current_nid = next.identifier
        self._player_move = not self._player_move
        return next.tag

    def get_player_moves(self) -> List[str]:
        return [n.tag for n in self._tree.children(self._current_nid)]
       
    
    def play_move(self, move: str) -> None:
        children = self._tree.children(self._current_nid)
        # By default we should only have one child but let's make it work for multiple children too
        candidates = list(filter(lambda node: node.tag == move, children))
        if len(candidates) != 1:
            raise ValueError("Invalid Move")

        self._current_nid = candidates[0].identifier
        self._player_move = not self._player_move
