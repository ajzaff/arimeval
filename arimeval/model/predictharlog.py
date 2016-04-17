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
    """1g Ra1 Rb1 Rc1 Dd1 De1 Rf1 Rg1 Rh1 Ra2 Hb2 Cc2 Ed2 Me2 Cf2 Hg2 Rh2
1s ra7 hb7 dc7 ed7 he7 df7 mg7 rh7 ra8 rb8 rc8 cd8 ce8 rf8 rg8 rh8
2g Ed2n Ed3n Ed4n Ed5n
2s mg7s mg6s mg5s mg4s
3g Ed6e Ee6s Ee5e Ef5s
3s mg3e mh3n mh4n mh5w
4g Ef4e Eg4w mg5s Me2n
4s rh7s rh6s rh5s mg4n
5g Ef4e Hb2n Dd1n Dd2n
5s ed7s ed6e ee6s ee5e
6g Eg4w mg5s mg4s Ef4e
6s ef5s he7s hb7s he6s
7g mg3w Eg4s De1n Rh2n
7s he5w hd5s hd4e Dd3n
8g De2w Dd2n Dd4w Dc4s
8s hb6s hb5s hb4e ra7s
9g Cc2e Dc3s Cd2e Hb3n
9s he4w hd4e Dd3n df7e
10g Hb4n Hb5n Hb6n Ra2n
10s ra6s ra5s dc7e dd7s
11g Hb7e Hc7e dd6w dc6x Hd7s
11s he4n he5w hd5w hc5w
12g Hd6n Hd7w Rb1n Rb2n
12s hb5s Rb3e hb4s dg7s
13g Ra1n Rc1w Rb1n
13s Rb2s hb3s Dc2e Rc3x hb2e
14g Dd2n Ra3e Ra2n
14s hc4w Rb3e hb4s hc2w
15g Dd4w Dc4w Hc7w rc8s
15s Db4e hb3n hb2n
16g rc7s rc6x Hb7e Rb1w Ra1n
16s Dc4e hb4e hb3n Ra3e
17g Ra2n Rf1w Re1w Rg1w
17s Dd4e hc4e Rb3s hb4s
18g Rd1w Rc1n Rb2w Rc3n
18s hb3n Ra3e De4n hd4e
19g Rc2n Rc4n Rc5n Ra2n
19s cd8w ce8w rf8w rg8w
20g Rc6e Rd6e De5e Rh1w
20s he4n Df5e he5e hf5n
21g Dg5w Rf1w Re1w Rg1w
21s Df5e hf6s dg6w rh8w
22g Eg3n Dg5n Eg4s Rd1w
22s Rb3s hb4s Rb2e hb3s
23g Dd3n Dd4w Dc4w Rc3n
23s Re6s df6w hb2n
24g Hc7e Hd7e de6w He7s
24s Db4n hb3n Db5n hb4n
25g dd6w dc6x He6w Rc4w Dg6n
25s hf5e Re5e Rf5n Rf6x hg5w
26g Dg7w Df7w De7w Dd7w
26s hf5w he5w hd5w
27g Eg3n Eg4s rh4w Rh3n
27s rg8e rf8e re8e hc5s
28g Dc7w cc8s cc7s cc6x Db7e
28s Rb4s hb5s Rb3e hb4s
29g Db6w Da6s Rc3e Hd6s
29s hb3n Ra3e ra4s ra3s
30g Rc1w Rb1w Rc2w
30s Rb3e hb4s Rb2e hb3s
31g Da5s Da4s Da3e ra2n
31s hc4w hb4w Db3n ra3s
32g Ce2s Ce1w Cd1w Cc1w
32s Cb1e hb2s Cf2w mf3s
33g Rc2w Rc3n Rc4n Rc5n
33s cd8s rf8w re8w rd8w
34g Rh4n Rh5n Rh6n Rh7w
34s ef4n ef5e eg5n
35g Rc6e Rd6e Re6n Hd5n
35s rc8e Re7s cd7e
36g Me3n Me4n Me5e Re6e
36s eg6s Mf5w Rf6x eg5w ce7e
37g Hd6e Rd3n Rd4n Rd5n
37s ef5n ef6s He6e Hf6x rd8s
38g Dc7w rd7w Rd6n Rd7n
38s""".split('\n')

import matplotlib.pyplot as plt

gs = GameState()
gold, goldmove, goldharlog = [], [], []
silver, silvermove, silverharlog = [], [], []
gs.move(movelist[0])
print(gs.harlog() - gs.harlog(side='s'))
gs.move(movelist[1])
print(gs.harlog() - gs.harlog(side='g'))
movelist = movelist[2:-1]
movenum = 3
for move in movelist:
    prediction = mlp.predict(np.array([gs.npfeats()]))[0][0]
    print(gs.boardstr(flippable=False))
    if gs.turn() == 'g':
        gold.append(prediction)
        goldmove.append(movenum)
        goldharlog.append(gs.harlog(normalize=False) - gs.harlog(side='s', normalize=False))
    else:
        silver.append(prediction)
        silvermove.append(movenum)
        silverharlog.append(gs.harlog(normalize=False) - gs.harlog(side='g', normalize=False))
    print(prediction)
    print(gs.harlog(normalize=False))
    print()
    gs.move(move)
    movenum += 1

plt.rcParams['font.size'] = 12
plt.title("Game ### Static Goodness Scores")
plt.xlabel("Halfmove")
plt.ylabel("Goodness")
plt.xticks(range(1, 1 + len(movelist), 4))
plt.plot(goldmove, gold, linewidth=3, color='gold', label='Gold Player')
plt.plot(silvermove, silver, linewidth=3, color='silver', label='Silver Player')
# plt.plot(goldmove, goldharlog, linewidth=3, color='tan', label='HarLog (g)')
# plt.plot(silvermove, silverharlog, linewidth=3, color='gray', label='HarLog (s)')
plt.legend(loc='best')
plt.grid(which='major', linestyle='dotted')

plt.show()
# plt.savefig(open(os.path.join(settings['data-base'], 'figures', 'figure-goodness_###.png'), 'w'))