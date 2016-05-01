from arimeval.positiondata import featdecode, max_height
from arimeval.settings import settings
from sklearn.cross_validation import KFold
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import numpy as np
import collections
import sknn.mlp
import pickle
import csv
import os


def lint(x):
    return int((int(x) + 1) / 2)


if __name__ == '__main__':

    np.random.seed(0)  # determinism

    print("loading model...")
    fn = os.path.join(settings['data-base'], 'nn.pickle')
    mlp = pickle.load(open(fn, 'rb'))

    fn = os.path.join(settings['data-base'], 'positions.csv')
    reader = csv.reader(open(fn), dialect='unix')
    reader.__next__()  # skip headers

    print("preparing to read data...")
    nolines = 3977256
    # nolines = 1000
    feats = collections.defaultdict(list)
    labels = collections.defaultdict(list)
    print("reading data...")
    for h, row in enumerate(reader):
        feats[int(row[2])].extend(featdecode(row[4]))
        labels[int(row[2])].append([lint(row[3])])
        if h + 1 >= nolines:
            break
        if h % 100000 == 0:
            print(h)

    print("reshaping data...")
    Xs = dict()
    ys = dict()
    for h in feats:
        samples = len(feats[h]) // 384
        Xs[h] = np.array(feats[h]).reshape((samples, 6, 8, 8))
        ys[h] = np.array(labels[h])

    mse_scores = dict()
    acc_scores = dict()

    for h in feats:
        y_pred = mlp.predict(np.array(Xs[h]))
        mse_scores[h] = mse(y_pred, ys[h])
        acc_scores[h] = accuracy_score([[round(y[0])] for y in y_pred], ys[h])

    acc_data = []
    mse_data = []
    h_data = []
    for h in sorted(feats.keys()):
        h_data.append(h)
        mse_data.append(mse_scores[h])
        acc_data.append(1 - acc_scores[h])

    # fig, ax1 = plt.subplots()
    # fig.suptitle('Tree Height v. Prediction Error')
    # plt1 = ax1.plot(h_data, mse_data, color='blue', label='mse')
    # ax1.set_ylabel('mean squared regression error (MSE)')
    # ax1.set_xlabel('game tree height, h')
    # ax2 = ax1.twinx()
    # plt2 = ax2.plot(h_data, acc_data, color='red', label='err (%)')
    # ax2.set_ylabel('classification error (%)')
    # fig.legend((plt1[0], plt2[0]), ('mse', 'err (%)'), loc=4)
    # ax1.grid()
    # plt.savefig('../../data/figures/figure-hplot.png')

    plt.title('Tree Height v. Prediction Error')
    plt.plot(h_data, mse_data, color='blue', label='mse')
    plt.plot(h_data, acc_data, color='red', label='err (%)')
    plt.ylabel('error')
    plt.xlabel('game tree height, h')
    plt.legend(loc=4)
    plt.grid()
    plt.savefig('../../data/figures/figure-hplot.png')