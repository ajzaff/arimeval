from arimeval.positiondata import featdecode, max_height
from arimeval.settings import settings
import sklearn
import numpy as np
import sknn.mlp
import csv
import os


def sigmoid_t(x):
    return int((int(x) + 1) / 2)


if __name__ == '__main__':
    rand = np.random.seed(0)

    print("initializing model...")
    mlp = sknn.mlp.Regressor(
        layers=[
            sknn.mlp.Convolution('Rectifier', channels=6, kernel_shape=(3, 3)),
            sknn.mlp.Layer('Rectifier'),
        ],
        random_state=rand,
        batch_size=max_height,
        n_iter=5000,
        n_stable=10,
        verbose=True,
    )

    fn = os.path.join(settings['data-base'], 'positions.csv')
    reader = csv.reader(open(fn), dialect='unix')
    reader.__next__()  # skip headers

    # limit = 5000000000
    # cv = sklearn.cross_validation.KFold(limit, 10, shuffle=True, random_state=rand)
    print("reading data...")
    feats = []
    labels = []
    for i, row in enumerate(reader):
        feats.extend(featdecode(row[3]))
        labels.append([sigmoid_t(row[2])])
        if i % 1000 == 0:
            print(i)
            # if i > limit:
            #     break

    # X_train, y_train, X_test, y_test = cv
    # # danger shuffle does not work yet!
    # print("shuffling data...")
    # indices = np.array(list(range(len(feats))))
    # np.random.shuffle(indices)
    # for i, j in enumerate(indices):
    #     feats[i], feats[j], labels[i], labels[j] = \
    #         feats[j], feats[i], labels[j], labels[i]
    print("reshaping data...")
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

    print(mlp.get_parameters())
    import json
    fn = os.path.join(settings['data-base'], 'params.json')
    json.dump(mlp.get_parameters(), open(fn, 'w'))




