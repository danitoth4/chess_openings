import re
from typing import List
from treelib import Node, Tree
import random

random.seed(1000)

class MoveTree:

    def __init__(self, move_list_path: str, player_move: bool) -> None:
        tree = Tree()
        self._player_move = player_move
        # allows multiple starting moves
        tree.create_node('+', 'root')
        with open(move_list_path, 'r') as f:
            line = f.readline()
            while line.strip() != '':
                moves = [item.strip() for item in re.split(r'\d+\.', line) if item != '']
                nodes = []
                for i, move in enumerate(moves):
                    nodes.extend([('w' + str(i + 1), move.split()[0]), ('b' + str(i + 1), move.split()[1])])

                for i, node in enumerate(nodes):
                    tag=node[1]
                    identifier=node[0] + node[1]
                    parent=nodes[i - 1][0] + nodes[i - 1][1] if i > 0 else 'root'
                    if identifier not in tree:
                        if player_move and len(tree.children(parent)) >= 1:
                            # TODO customize this scenario
                            raise ValueError('Multiple responses for same move')
                        else:
                            tree.create_node(tag, identifier, parent=parent)
                    
                    player_move = not player_move
                
                line = f.readline()

        self._tree = tree
        self._current_nid = 'root'
            
    def get_opponent_move(self) -> str:
        children = self._tree.children(self._current_nid)
        if not children:
            return "gg"
        
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
