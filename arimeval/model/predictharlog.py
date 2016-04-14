from arimeval.settings import settings
from arimeval.state.gamestate import GameState
import numpy as np
import pickle
import os

# mlp = sknn.mlp.Regressor(
#     layers=[
#         sknn.mlp.Convolution('Rectifier', channels=6, kernel_shape=(3, 3)),
#         sknn.mlp.Layer('Rectifier'),
#     ],
#     parameters=params,
#     random_state=0,
#     n_iter=3,
#     n_stable=3,
#     verbose=True
# )
#
# mlp.set_parameters(params)

fn = os.path.join(settings['data-base'], 'nn.pickle')
mlp = pickle.load(open(fn, 'rb'))

movelist = \
    """1g Ra2 Mb2 Dc2 Ed2 He2 Df2 Hg2 Rh2 Ra1 Rb1 Rc1 Cd1 Ce1 Rf1 Rg1 Rh1
1s ra7 hb7 dc7 md7 ee7 df7 hg7 rh7 ra8 rb8 rc8 cd8 ce8 rf8 rg8 rh8
2g Ra2n Ra3n Ra4n Ra5n
2s hb7s hg7s hb6n Ra6e
3g Rh2n Rh3n Rh4n Rh5n
3s hg6n Rh6w Rb6e Rc6x hb7s
4g Rh1n Rh2n Rh3n Rh4n
4s Rg6w Rf6x hg7s ee7s ee6s
5g Ra1n Ra2n Ra3n Rh5n
5s hg6n Rh6w Rg6w Rf6x hg7s
6g Ra4e Rb4e Rc4e Rd4n
6s Rd5w ee5w Rc5n Rc6x ed5w
7g Rg1e Rh1n Rh2n Rh3n
7s ec5w eb5s eb4s
8g Rh4n Rb1w Ra1n Rh5n
8s hg6n Rh6w Rg6w Rf6x hg7s
9g Ra2n Mb2w Ra3n Ra4n
9s eb3s Dc2n Dc3x eb2e
10g Ra5n Rc1w Rb1n Rb2n
10s ec2w hb6s hb5s
11g Rf1e Rg1e Rh1n Ra6e
11s dc7w Rb6e Rc6x db7s db6s
12g Rh2n Rh3n Rh4n Rh5n
12s hg6n Rh6w Rg6w Rf6x hg7s
13g Ed2w Ec2n Rb3w Ec3x Ra3n
13s hb4e Ra4e eb2s Ma2e
14g He2n Ce1e Cf1e Cg1e
14s Mb2n eb1n Mb3e Mc3x eb2n
15g He3w Ch1w Cg1e Ch1n
15s eb3e ec3s Hd3w Hc3x hg6s
16g Ch2n Cd1e Ce1e Cf1e
16s ec2e ed2e Df2n Df3x ee2e
17g Ch3n Cg1e Ch1w Cg1w
17s hg5s
18g""".split('\n')

import matplotlib.pyplot as plt

gs = GameState()
gold, goldmove, goldharlog = [], [], []
silver, silvermove, silverharlog = [], [], []
gs.move(movelist[0])
gs.move(movelist[1])
movelist = movelist[2:-1]
movenum = 3
for move in movelist:
    prediction = mlp.predict(np.array([gs.npfeats()]))[0][0]
    print(gs.boardstr(flippable=False))
    if gs.turn() == 'g':
        gold.append(prediction)
        goldmove.append(movenum)
        goldharlog.append(gs.harlog())
    else:
        silver.append(prediction)
        silvermove.append(movenum)
        silverharlog.append(gs.harlog())
    print(prediction)
    print(gs.harlog(normalize=False))
    print()
    gs.move(move)
    movenum += 1

plt.rcParams['font.size'] = 12
plt.title("Game ### Static Goodness Scores")
plt.xlabel("Halfmove")
plt.ylabel("Goodness")
plt.xticks(range(1, 1 + len(movelist), 1))
plt.plot(goldmove, gold, linewidth=3, color='gold', label='Gold Player')
plt.plot(goldmove, goldharlog, linewidth=3, color='tan', label='HarLog (g)')
plt.plot(silvermove, silver, linewidth=3, color='silver', label='Silver Player')
plt.plot(silvermove, silverharlog, linewidth=3, color='gray', label='HarLog (s)')
plt.legend(loc='best')
plt.grid(which='major', linestyle='dotted')

plt.show()
# plt.savefig(open(os.path.join(settings['data-base'], 'figures', 'figure-goodness_###.png'), 'w'))