from arimeval.settings import settings
import itertools
import pickle
import os
import numpy as np
from PIL import Image, ImageOps

print("loading model...")
fn = os.path.join(settings['data-base'], 'nn.pickle')
mlp = pickle.load(open(fn, 'rb'))

mlp.predict(np.array([list(range(384))]).reshape((1, 6, 8, 8)))
conv = np.array(mlp.get_parameters()[0][0])

for c in range(6):
    for i in range(8):
        s = 0.
        for x in range(4):
            for y in range(4):
                s += abs(conv[c][i][x][y])
        for x in range(4):
            for y in range(4):
                conv[c][i][x][y] = int((1 << 23) * abs(conv[c][i][x][y]) / s)

# print(conv)

padding = 20
scale = 10
sheet = Image.new('RGB', (8 * (4 * scale) + 9 * padding, 6 * (4 * scale) + 7 * padding), color='white')

pallets = {
    0: list(itertools.chain.from_iterable((c, c, c) for c in range(256))),
    1: list(itertools.chain.from_iterable((c, c, c // 2) for c in range(256))),
    2: list(itertools.chain.from_iterable((c, c // 2, c) for c in range(256))),
    3: list(itertools.chain.from_iterable((c, c // 2, c // 2) for c in range(256))),
    4: list(itertools.chain.from_iterable((c // 2, c, c) for c in range(256))),
    5: list(itertools.chain.from_iterable((c // 2, c, c // 2) for c in range(256)))
}

for c in range(6):
    for i in range(8):
        img = Image.fromarray(conv[c][i], 'P')
        img.putpalette(pallets[c])
        img.save('../../data/figures/conv/patch_%d_%d.png' % (c, i))
        img = img.resize((4 * scale, 4 * scale))
        sheet.paste(img, box=(i * (scale * 4) + (1 + i) * padding, c * (scale * 4) + (1 + c) * padding))

sheet.save('../../data/figures/conv/figure-filters.png')