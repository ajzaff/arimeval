from arimeval.state.gamestate import GameState
from arimeval.settings import settings
import numpy as np
import pickle
import os


if __name__ == '__main__':

    fn = os.path.join(settings['data-base'], 'nn.pickle')
    mlp = pickle.load(open(fn, 'rb'))

    gs = GameState()
    myside = 'g'
    while True:
        myside = input('new game (g/s): ')
        if myside in {'g', 's'}:
            break
        elif myside == 'exit':
            exit()
    while True:
        print(gs.boardstr(side=myside))
        print(mlp.predict(np.array([gs.npfeats()])))
        try:
            move = input('move: ')
            if move == 'exit':
                exit()
            gs.move(move)
        except Exception as e:
            print(e)