from arimeval.positiondata import featdecode, max_height
from arimeval.settings import settings
import sklearn
import numpy as np
import sknn.mlp
import pickle
import csv
import os


def lint(x):
    return int((int(x) + 1) / 2)


if __name__ == '__main__':

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

    # limit = 5000000000
    # cv = sklearn.cross_validation.KFold(limit, 10, shuffle=True, random_state=rand)
    print("reading data...")
    rows = []
    for i, row in enumerate(reader):
        rows.append((featdecode(row[3]), [lint(row[2])]))
        if i % 100000 == 0:
            print(i)
            # if i > limit:
            #     break

    print("shuffling data...")
    np.random.shuffle(rows)

    print("reshaping data...")
    feats = []
    labels = []
    for i, (f, l) in enumerate(rows):
        feats.extend(f)
        labels.append(l)
        if i % 100000 == 0:
            print(i)
    samples = len(feats) // 384
    X = np.array(feats).reshape((samples, 6, 8, 8))
    y = np.array(labels)

    print("fitting model...")
    mlp.fit(X, y)

    # v = '0203020205090N1213114121411C00c131O091E1D0P1~z190T'
    # v1 = '4070P0300811212121312121P0V1O040O1A1h071801R0N1y1G0K'
    #
    # X = np.array(featdecode(v) + featdecode(v1)).reshape((2, 6, 8, 8))
    # y = np.array([[1], [-1]])
    # mlp.fit(X, y)
    # # print(mlp.get_parameters())
    #
    # x = np.array(featdecode(v)).reshape((1, 6, 8, 8))
    # x1 = np.array(featdecode(v1)).reshape((1, 6, 8, 8))
    # print(mlp.predict(x))
    # print(mlp.predict(x1))

    # print(mlp.get_parameters())
    # print(mlp.get_parameters()[0])
    # print(type(mlp.get_parameters()[0]))
    # print(type(mlp.get_parameters()[0][0]))

    fn = os.path.join(settings['data-base'], 'nn.pickle')
    pickle.dump(mlp, open(fn, 'wb'))




