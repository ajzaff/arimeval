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
        for y in range(4):
            for x in range(4):
                s += abs(conv[c][i][y][x])
        for y in range(4):
            for x in range(4):
                conv[c][i][y][x] = int((1 << 23) * abs(conv[c][i][y][x]) / s)

# print(conv)

padding = 20
scale = 10
sheet = Image.new('RGB', (8 * (4 * scale) + 9 * padding, 6 * (4 * scale) + 7 * padding), color='white')

begin = (0, 0, 0)


def mix(begin, end):
    for i in range(256):
        yield (int(b * (255 - i) / 255 + e * i / 255) for b, e in zip(begin, end))


pallets = {
    0: list(itertools.chain.from_iterable(mix(begin, (255, 255, 255)))),
    1: list(itertools.chain.from_iterable(mix(begin, (255, 255, 127)))),
    2: list(itertools.chain.from_iterable(mix(begin, (255, 127, 255)))),
    3: list(itertools.chain.from_iterable(mix(begin, (255, 127, 127)))),
    4: list(itertools.chain.from_iterable(mix(begin, (127, 255, 255)))),
    5: list(itertools.chain.from_iterable(mix(begin, (127, 255, 127))))
}

for c in range(6):
    for i in range(8):
        img = Image.fromarray(np.transpose(conv[c][i]), 'P')
        img.putpalette(pallets[c])
        img.save('../../data/figures/conv/patch_%d_%d.png' % (c, i))
        img = img.resize((4 * scale, 4 * scale))
        sheet.paste(img, box=(i * (scale * 4) + (1 + i) * padding, c * (scale * 4) + (1 + c) * padding))

sheet.save('../../data/figures/conv/figure-filters.png')