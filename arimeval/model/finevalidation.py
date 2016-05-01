from arimeval.positiondata import featdecode, max_height
from arimeval.settings import settings
from sklearn.cross_validation import KFold
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import accuracy_score
import itertools
import numpy as np
import sknn.mlp
import pickle
import csv
import os

dropout_rate_params = (None, .005, .01, .25)
regularize_params = (None, 'L2', 'L1')
learning_rule_params = ('rmsprop', 'nesterov')
kernel_shape_params = ((6, 6),)
microsize = 30000
num_models = 8

best_models = [None for _ in range(num_models)]
best_scores = [-float('inf') for _ in range(num_models)]

def lint(x):
    return int((int(x) + 1) / 2)


def evict(i):
    for i in range(7, i, -1):
        best_models[i] = best_models[i - 1]
        best_scores[i] = best_scores[i - 1]


def insert_model(model, newr2):
    global best_models, best_scores
    for i, curr2 in enumerate(best_scores):
        if best_models[i] is None:
            best_models[i] = model
            best_scores[i] = newr2
            return True
        elif curr2 < newr2:
            evict(i)
            best_models[i] = model
            best_scores[i] = newr2
            return True
    return False


if __name__ == '__main__':

    np.random.seed(0)  # determinism

    fn = os.path.join(settings['data-base'], 'positions.csv')
    reader = csv.reader(open(fn), dialect='unix')
    reader.__next__()  # skip headers

    print("preparing to read data...")
    # nolines = 3977256
    nolines = 1800000
    # nolines = 30000
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

    X_all = np.array(feats).reshape((samples, 6, 8, 8))
    y_all = np.array(labels)

    ##################################################################################

    for dropout_rate, regularize, learning_rule, kernel_shape in \
            itertools.product(dropout_rate_params,
                              regularize_params,
                              learning_rule_params,
                              kernel_shape_params):

        kf = KFold(n=microsize, n_folds=2, random_state=np.random)
        maes = []
        r2s = []
        mses = []
        accs = []

        r = np.random.randint(0, 1 + len(X_all) - microsize)
        X = X_all[r:r + microsize]
        y = y_all[r:r + microsize]

        examples = list(zip(X, y))  # shuffle
        np.random.shuffle(examples)
        X, y = tuple(zip(*examples))
        X = np.array(X)
        y = np.array(y)

        for train_index, test_index in kf:

            mlp = sknn.mlp.Regressor(
                layers=[
                    sknn.mlp.Convolution('Tanh', channels=6, kernel_shape=kernel_shape),
                    sknn.mlp.Layer('Tanh', units=384),
                    sknn.mlp.Layer('Rectifier'),
                ],
                learning_rule=learning_rule,
                regularize=regularize,
                dropout_rate=dropout_rate,
                random_state=0,
                batch_size=1000,
                n_iter=10,
                n_stable=10,
                verbose=True)

            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            # print("fitting model...")
            mlp.fit(X_train, y_train)

            # print("scoring model...")
            # print("predicted:", mlp.predict(X_test))
            # print("actual:", y_test)
            r2s.append(mlp.score(X_test, y_test))
            y_pred = mlp.predict(X_test)
            mses.append(mse(y_pred, y_test))
            mae_score = mae(y_pred, y_test)
            maes.append(mae_score)
            # print("MAE score =", mae_score)
            accs.append(accuracy_score([[round(y[0])] for y in y_pred], y_test))

        mean_mae = np.mean(maes)
        mean_mse = np.mean(mses)
        mean_r2 = np.mean(r2s)
        mean_acc = np.mean(accs)

        model = (mean_mse, mean_mae, mean_r2, mean_acc, dropout_rate, regularize, learning_rule, kernel_shape[0], kernel_shape[1])

        if insert_model(model, mean_r2):
            print("**")
            for e in best_models:
                if e is None:
                    break
                else:
                    print("%s & %s & %s & %s & %s & %s & %s & $%d\\times %d$ \\\\" % e)
            print()
