from arimeval.positiondata import featdecode, max_height
from arimeval.settings import settings
from sklearn.cross_validation import KFold
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import accuracy_score
import numpy as np
import sknn.mlp
import pickle
import csv
import os


def lint(x):
    return int((int(x) + 1) / 2)


if __name__ == '__main__':

    np.random.seed(0)  # determinism

    print("initializing model...")
    mlp = sknn.mlp.Regressor(
        layers=[
            sknn.mlp.Convolution('Tanh', channels=6, kernel_shape=(4, 4)),
            sknn.mlp.Layer('Tanh', units=384),
            sknn.mlp.Layer('Rectifier'),
        ],
        random_state=0,
        batch_size=4096,
        n_iter=30,
        n_stable=3,
        regularize='L1',
        dropout_rate=None,
        learning_rule='nesterov',
        verbose=True
    )

    fn = os.path.join(settings['data-base'], 'positions.csv')
    reader = csv.reader(open(fn), dialect='unix')
    reader.__next__()  # skip headers

    print("preparing to read data...")
    nolines = 3977256
    # nolines = 400000
    feats = []
    labels = []
    print("reading data...")
    for i, row in enumerate(reader):
        feats.extend(featdecode(row[4]))
        labels.append([lint(row[3])])
        if i + 1 >= nolines:
            break
        if i % 100000 == 0:
            print(i)

    print("reshaping data...")
    samples = len(feats) // 384

    X = np.array(feats).reshape((samples, 6, 8, 8))
    y = np.array(labels)

    print("shuffling data...")
    examples = list(zip(X, y))
    X, y = list(zip(*examples))
    X = np.array(X)
    y = np.array(y)
    del examples

    kf = KFold(n=len(X), n_folds=5, shuffle=True, random_state=np.random)
    train_index, test_index = next(iter(kf))
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    del X
    del y

    print("fitting model...")
    mlp.fit(X_train, y_train)

    print("scoring model...")
    # print("predicted:", mlp.predict(X_test))
    # print("actual:", y_test)
    print("R^2 score =", mlp.score(X_test, y_test))
    y_pred = mlp.predict(X_test)
    print("MSE score =", mse(y_pred, y_test))
    print("MAE score =", mae(y_pred, y_test))
    print("accuracy_score =", accuracy_score([[round(y[0])] for y in y_pred], y_test))

    fn = os.path.join(settings['data-base'], 'nn_tanh3.pickle')
    pickle.dump(mlp, open(fn, 'wb'))




