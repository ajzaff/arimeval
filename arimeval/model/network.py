from arimeval.positiondata import featdecode, max_height
from arimeval.settings import settings
import numpy as np
import sknn.mlp
import pickle
import csv
import os


def lint(x):
    return int((int(x) + 1) / 2)


if __name__ == '__main__':

    np.random.seed(0)

    print("initializing model...")
    mlp = sknn.mlp.Regressor(
        layers=[
            sknn.mlp.Convolution('Rectifier', channels=6, kernel_shape=(3, 3)),
            sknn.mlp.Layer('Rectifier'),
        ],
        random_state=0,
        batch_size=1,
        n_iter=5,
        n_stable=10,
        verbose=True,
    )

    fn = os.path.join(settings['data-base'], 'positions.csv')
    reader = csv.reader(open(fn), dialect='unix')
    reader.__next__()  # skip headers

    print("preparing to read data...")
    nolines = 3977256
    feats = [None for _ in range(nolines)]
    labels = [None for _ in range(nolines)]
    print("reading shuffled data...")
    for i, row in enumerate(reader):
        r = np.random.randint(nolines)
        feats[r] = featdecode(row[4])
        labels[r] = [lint(row[3])]
        if i % 100000 == 0:
            print(i)

    print("reshaping data...")
    samples = len(feats) // 384
    X = np.array(feats).reshape((samples, 6, 8, 8))
    y = np.array(labels)

    print("fitting model...")
    mlp.fit(X, y)

    fn = os.path.join(settings['data-base'], 'nn.pickle')
    pickle.dump(mlp, open(fn, 'wb'))




