import re
import itertools
import numpy as np


class GameState(object):

    pieces = ('R', 'C', 'D', 'H', 'M', 'E')
    bb = ('R', 'C', 'D', 'H', 'M', 'E',
          'r', 'c', 'd', 'h', 'm', 'e')
    offsets = {'n': 8, 's': -8, 'e': 1, 'w': -1,
               'N': 8, 'S': -8, 'E': 1, 'W': -1,
               None: 0}
    files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    ranks = ('1', '2', '3', '4', '5', '6', '7', '8')
    traps = ('c3', 'f6', 'f3', 'c6')

    def __init__(self):
        self._bb = {}
        self._moves = []
        self.reset()

    def fullmove(self):
        if self._moves:
            move = self._moves[-1].split()[0]
            return int(move[:-1]) + (1 if move[-1] in {'s', 'b'} else 0)
        else:
            return 1

    # def getpartialmove(self):
    #     if self._moves:
    #         m = list(filter(lambda m: not m.endswith('x'), self._moves[-1].split()[1:]))
    #         return m if len(m) < 4 else []
    #     return []

    def turn(self):
        if self._moves:
            c = self._moves[-1].split()[0][-1]
            return 's' if c in {'g', 'w'} else 'g'
        else:
            return 'g'

    def reset(self):
        self['R'] = \
            self['C'] = \
            self['D'] = \
            self['H'] = \
            self['M'] = \
            self['E'] = \
            self['r'] = \
            self['c'] = \
            self['d'] = \
            self['h'] = \
            self['m'] = \
            self['e'] = 0
        self._moves.clear()

    def __len__(self):
        return len(self._moves)

    def __str__(self):
        rankfunc = reversed if self.turn() == 'g' else lambda r: r
        filefunc = reversed if self.turn() == 's' else lambda f: f
        s = '%d%s\n +-----------------+\n' % (self.fullmove(), self.turn())
        for r in rankfunc(GameState.ranks):
            s += '%s| ' % r
            for f in filefunc(GameState.files):
                sq = '%s%s' % (f, r)
                m = GameState.sq2bb(sq)
                empty = True
                for p in GameState.bb:
                    if m & self[p] != 0:
                        s += '%s ' % p
                        empty = False
                        break
                if empty:
                    if sq in GameState.traps:
                        s += 'x '
                    else:
                        s += '  '
            s += '|\n'
        s += ' +-----------------+\n   %s\n' % ' '.join(filefunc(GameState.files))
        return s

    def boardstr(self, flippable=True):
        rankfunc = reversed if flippable and self.turn() == 'g' else lambda r: r
        filefunc = reversed if flippable and self.turn() == 's' else lambda f: f
        s = '%d%s %s\n +-----------------+\n' % (self.fullmove(), self.turn(), ' '.join(self.getpartialmove()))
        for r in rankfunc(GameState.ranks):
            s += '%s| ' % r
            for f in filefunc(GameState.files):
                sq = '%s%s' % (f, r)
                m = GameState.sq2bb(sq)
                empty = True
                for p in GameState.bb:
                    if m & self[p] != 0:
                        s += '%s ' % p
                        empty = False
                        break
                if empty:
                    if sq in GameState.traps:
                        s += 'x '
                    else:
                        s += '  '
            s += '|\n'
        s += ' +-----------------+\n   %s\n' % ' '.join(filefunc(GameState.files))
        return s

    def __getitem__(self, item):
        return self._bb[item]

    def __setitem__(self, key, value):
        if key in GameState.bb:
            self._bb[key] = value
        else:
            raise KeyError()

    def takeback(self):
        if self._moves:
            self.unmove(self._moves.pop())
        else:
            raise ValueError()

    def setstate(self, turn, next=False):
        move = turn[:-1]
        color = 'g' if turn[-1] in {'g', 'w'} else 's'
        if next:
            color = 's' if color == 'g' else 'g'
            move = str(1 + int(move)) if color == 'g' else move
        self._turn = move + color

    def move(self, move):
        if 'takeback' in move:
            self.takeback()
        else:
            if re.match(r'^1[wbgs] ', move, re.IGNORECASE):
                self.setup(move)
            else:
                moves = move.split()
                if len(moves) == 1:
                    return
                for step in moves[1:]:
                    self.step(step)
            self._moves.append(move)

    def unmove(self, move):
        if re.match(r'^1[wbgs] ', move, re.IGNORECASE):
            self.unsetup(move)
        else:
            moves = move.split()
            for step in reversed(moves[1:]):
                self.unstep(step)

    def step(self, step):
        piece = step[0]
        sq = step[1:3]
        offset = step[-1]
        if offset == 'x':
            self[piece] &= ~GameState.sq2bb(sq)
        else:
            self[piece] &= ~GameState.sq2bb(sq)
            self[piece] |= GameState.sq2bb(sq, offset=offset)

    def unstep(self, step):
        piece = step[0]
        sq = step[1:3]
        offset = step[-1]
        if offset == 'x':
            self[piece] |= GameState.sq2bb(sq)
        else:
            self[piece] |= GameState.sq2bb(sq)
            self[piece] &= ~GameState.sq2bb(sq, offset=offset)

    def setup(self, move):
        moves = move.split()
        for e in moves[1:]:
            piece = e[0]
            sq = e[1:3]
            self[piece] |= GameState.sq2bb(sq)

    def unsetup(self, move):
        moves = move.split()
        self.setstate(moves[0])
        for e in moves[1:]:
            piece = e[0]
            sq = e[1:3]
            self[piece] &= ~GameState.sq2bb(sq)

    def featurenames(self):
        rankfunc = reversed if self.turn() == 'g' else lambda r: r
        filefunc = reversed if self.turn() == 's' else lambda f: f
        for p, r, f in itertools.product(GameState.pieces, rankfunc(GameState.ranks), filefunc(GameState.files)):
            yield '%s%s%s' % (f, r, p)

    def features(self):
        for sqp in self.featurenames():
            piece = sqp[-1]
            sq = sqp[:-1]
            bb = GameState.sq2bb(sq)
            if self[piece] & bb != 0:
                yield 1 if self.turn() == 'g' else -1
            else:
                bb = GameState.sq2bb(sq)
                if self[piece.lower()] & bb != 0:
                    yield -1 if self.turn() == 'g' else 1
                else:
                    yield 0

    def npfeats(self):
        return np.array(list(self.features())).reshape(6, 8, 8)


    @classmethod
    def sq2i(cls, sq, **kwargs):
        file = sq[0]
        rank = sq[1:2].lower()
        return 8 * int(rank) + ord(file) - 105 + \
            cls.offsets[kwargs.get('offset', None)]

    @classmethod
    def sq2bb(cls, sq, **kwargs):
        return 1 << cls.sq2i(sq, **kwargs)


if __name__ == '__main__':
    # # import itertools
    # # files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    # # ranks = (1, 2, 3, 4, 5, 6, 7, 8)
    # # for r, f in itertools.product(ranks, files):
    # #     square = '%s%s' % (f, r)
    # #     print(square, GameState.sq2i(square), GameState.sq2bb(square))
    #
    # # game 4421 (id=1)
    # gs = GameState()
    #
    moves = '1w Ha2 Cf2 Mb2 Dc2 Ed2 De2 Hg2 Ch2 Ra1 Rb1 Rc1 Rd1 Re1 Rf1 Rg1 Rh1\n1b ha7 hh7 ce7 df7 mg7 eb7 dc7 cd7 ra8 rb8 rc8 rd8 re8 rf8 rg8 rh8\n2w Ed2n Ed3n Ed4w Ec4w\n2b eb7s eb6s eb5w ea5s\n3w Mb2n Mb3e Mc3e\n3b ea4s ea3e eb3s hh7s\n4w Eb4e Md3e Me3e Mf3e\n4b Dc2n eb2e ec2e ed2n\n5w Dc3w Ec4e Ed4e Ha2e\n5b hh6n ed3s De2n ed2e\n6w De3w Ee4s Dd3s Hb2e\n6b Dd2n ee2w Dd3n ed2n\n7w Ee3n Dd4w Dc4s\n7b ed3s Dc3e ha7s ha6e\n8w Cf2w Hg2w Ee4w Db3s\n8b Ce2n ed2e Hf2n ee2e\n9w Mg3s Hf3e Ed4n Ed5w\n9b ef2w Ce3n ee2n hb6n\n10w Ec5e Ed5s Ce4e Cf4s\n10b ee3n ee4e ef4e Cf3n\n11w Ed4e Cf4s Ee4e Hg3e\n11b eg4s Hh3n eg3e hb7s\n12w Cf3s Ef4n Ef5e Eg5n\n12b eh3w eg3e Mg2n ce7s\n13w Ch2w Mg3w Mf3w Me3s\n13b Hh4n eh3n Hh5n eh4n\n14w Dd3s Me2n Me3w Md3w\n14b df7s mg7w mf7w df6n\n15w Mc3w Hc2n Hc3e Dd2e\n15b eh5w eg5w ef5w ee5s\n16w Eg6s Eg5w Ef5w Hd3s\n16b df7s me7e mf7e mg7s\n17w Ee5e Ef5e Eg5w mg6s\n17b ee4e ef4e mg5n df6n\n18w Ef5w Ee5e ce6s Hd2n\n18b eg4w ef4w ce5n hh7w\n19w Ef5e Eg5w mg6s De2n\n19b ee4e ef4e mg5n ce6n\n20w Mb3n Mb4n Mb5w hb6s\n20b Hh6n mg6e eg4w ef4w\n21w Ef5e Eg5n Db2e\n21b ee4w ed4w ec4w eb4w\n22w mh6s Eg6e Hd3n Hd4n\n22b Ma5n ea4n hb5e hg7s\n23w mh5s Eh6s Hd5n Hh7w\n23b ea5e eb5n hc5e hd5s\n24w mh4w Eh5s mg4s Eh4w\n24b df7s df6s df5s hd4e\n25w Eg4n df4e dg4e Eg5s\n25b De3e he4s rf8s\n26w Eg4w mg3n Df3e Hd6e\n26b eb6e Ma6e ec6e Mb6e Mc6x\n27w Ef4s Ef3n he3e hf3x Rb1n\n27b He6e Hf6x ed6e mg4n mg5e\n28w Ef4e Eg4n dh4w Hg7e\n28b ee6s ee5s ee4e dg4e\n29w Dg3e Hh7w Cf2w Cg2w\n29b mh5n hg6w hf6w mh6n\n30w Eg5n Eg6e Eh6w mh7s\n30b dh4n mh6n ef4n he6s\n31w rf7s Hg7w Dh3w Rh1n\n31b mh7w Hf7n mg7w rf6w\n32w Eg6n mf7s Eg7w Rh2n\n32b re6w mf6w he5s he4s\n33w Rb2n Ef7e Eg7s Rh3n\n33b Rh4s dh5s me6e mf6n\n34w Eg6s Eg5s Eg4w Ef4w\n34b dc7s dc6s dc5s ef5s\n35w Ee4w dc4s dc3x Ed4w Ec4e\n35b he3e Dg3s hf3e rc8s\n36w Ed4e Ee4n Ee5e Ce2n\n36b ef4w Ce3s ee4s rd6e\n37w Dg2e Ce2w Cf2w Ef5s\n37b mf7e Hf8s Hf7s Hf6x mg7w\n38w Ef4e Rb3w Dc2w Db2n\n38b takeback\n38w Rb3w Dc2w Db2n Cd2w\n38b hg3s hg2w Rh3w dh4s\n39w Dh2w Rg3n Rg4n Rg5e\n39b dh3n Rh5n dh4n re8e\n40w Db3n Db4n Db5n Db6n\n40b ce7n mf7w rf8s cd7s\n41w Ra3n Ra4n rb8e Db7n\n41b me7w rc7s md7w mc7w\n42w Ef4n Ef5e Eg5n dh5w\n42b hf2n Dg2w hf3e Df2n Df3x\n43w Eg6n rf7s Eg7w Rh6n\n43b dg5n dg6n ce8e rf6e\n44w Ef7w Ee7w Ed7w cd6n rc6x\n44b ee3n ee4w ed4w ec4n\n45w Ra5n Ra6n mb7s Ec7w\n45b ec5w mb6w eb5n cd7w\n46w cc7s Eb7e Ec7e Ed7s\n46b Ra7e ma6n cc6n cf8s\n47w Ed6s Ed5e Ee5e Ef5s\n47b hg3s hg2e eb6s eb5e\n48w Ef4w Ee4n Ee5w Ed5n\n48b Rb7s ma7e Rb6e mb7s\n49w Ra1n Ra2n Ra3n Ra4n\n49b hh2w hg2w rg6s rg5e\n50w Rg1e Ce2w Rf1e Cc2w\n50b rh5s rh4s rh3s rh2w\n51w Ra5n Cb2n Cb3n Re1e\n51b hf2w Rf1n Rf2n Rf3x he2e\n52w Rd1e Re1e Cb4w Ca4n\n52b ec5w eb5e Ca5e\n53w Ed6s Rc6x Ed5s Ed4s Ed3e\n53b cf7s cf6s cf5s re6s\n54w Ee3s Ee2n hf2w Rf1n\n54b ec5e ed5s ed4s re5w\n55w Ee3e Ef3w cf4s cf3x Rc1n\n55b rd5s rd4w rc4s rc3w\n56w Ee3e he2n Ef3e he3e hf3x\n56b rb3s rb2s\n57w'
    moves = moves.split('\n')

    #
    # for move in moves:
    #     print(move)
    #     gs.move(move)
    #
    # # while len(gs) > 2:
    # #     gs.takeback()
    #
    # for i, e in enumerate(gs.features(), 1):
    #     print(str(e).rjust(3), end='')
    #     if i % 8 == 0:
    #         print()
    #     if i % 64 == 0:
    #         print()
    #
    # print(gs)
    # print(len(list(gs.features())))
    # print(sum(gs.features()))
    #
    # import numpy as np
    # x = np.array(list(gs.features())).reshape(6, 8, 8)
    # print(x)
    #
    gs = GameState()
    print(gs)

    gs.move(moves[0])
    print(gs)

    gs.move(moves[1])
    print(gs)

    for move in moves[2:-1]:
        gs.move(move)
        print(gs)
