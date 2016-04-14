from arimeval.settings import settings
from arimeval.state.gamestate import GameState
import arimeval.bulkdata
import csv
import os


output_fieldnames = 'id', 'height', 'label', 'features'
max_height = 60
num_games = 37297 # old dataset was 12014


def games():
    fn = os.path.join(settings['data-base'], 'expert', 'expert.csv')
    expert_reader = csv.DictReader(
        open(fn),
        fieldnames=arimeval.bulkdata.output_fieldnames,
        dialect='unix')
    for e in expert_reader:
        yield e


def rows():
    gs = games()
    gs.__next__()  # advance past the header
    for g in gs:
        moves = g['movelist'].split('\\n')
        gb = GameState()
        res = 1 if g['result'] in ['g', 'w'] else -1
        if len(moves) > 1:
            for m in moves:
                gb.move(m)
            h = 0
            while len(gb) > 0 and h < max_height:
                yield h, gb.features(), res * (1 if gb.turn() == 'g' else -1)
                gb.takeback()
                h += 1


def fem(f):
    return '1' if f == 1 else '0'

b83 = tuple("23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")

b83d = dict(zip(b83, range(1, 84)))


def featencode(feats):
    s = ""
    i = 0
    for f in feats:
        if f == 0:
            i += 1
            if i == 83:
                s += b83[82]
                i = 0
        else:
            if i > 0:
                s += b83[i - 1]
                i = 0
            s += fem(f)
    if i > 0:
        s += b83[i - 1]
    return s


def featdecode(text):
    feats = []
    for c in text:
        if c in b83d:
            feats.extend(b83d[c] * [0])
        else:
            feats.append(1 if c == '1' else -1)
    return feats

# if __name__ == '__main__':
#     # dump positions
#     # fn = os.path.join(settings['data-base'], 'positions2.csv')
#     # writer = csv.writer(open(fn, 'w'), dialect='unix')
#     # writer.writerow(output_fieldnames)
#     # for i, (h, feats, label) in enumerate(rows(), 1):
#     #     writer.writerow((i, h, label, featencode(feats)))
#     #     if i % 1000 == 0:
#     #         print('%.2f%%' % ((100. * i) / (max_height*num_games)))
#
#     # for i, (h, feats, label) in enumerate(rows(), 1):
#     #     print(list(feats))
#     #     exit(0)
#
#     # v = [0, -1, 1]
#     # print(v)
#     # print(featencode(v))
#     # print(featdecode(featencode(v)))
#     # print()
#     #
#     # t = featencode(v)
#     # print(t)
#     # print(featdecode(t))
#     # print(featencode(featdecode(t)))
#
#     # import numpy as np
#     # v = '0203020205090N1213114121411C00c131O091E1D0P1~z190T'
#     # print(v)
#     # print(np.array(featdecode(v)).reshape((6, 8, 8)))
#
#     #
#     # import numpy as np
#     # print(np.array(featdecode(v)))
#     # print(len(featdecode(v)))
#
#     # x = [-1, 0, -1, -1, 0, 0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, -1, 0, 0, -1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#     # z = featencode(x)
#     # print(z)
#     # print("0200300811Y131030511B0F1Q1E1D0~m0~7031")
#     # print(x)
#     # print(featdecode(z))
