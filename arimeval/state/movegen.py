# not used.


class MoveGen(object):
    def __init__(self, gs):
        self.gs = gs

    all_pieces = {
        'g': 'RCDHME',
        'w': 'RCDHME',
        's': 'rcdhme',
        'b': 'rcdhme'
    }

    piece_hierarchy = {
        'R': 'CDHME',
        'C': 'DHME',
        'D': 'HME',
        'H': 'ME',
        'M': 'E',
        'E': ''
    }

    bb_ranks = {
        1: 255,
        2: 65280,
        3: 16711680,
        4: 4278190080,
        5: 1095216660480,
        6: 280375465082880,
        7: 71776119061217280,
        8: 18374686479671623680
    }

    bb_files = {
        'a': 72340172838076673,
        'b': 144680345676153346,
        'c': 289360691352306692,
        'd': 578721382704613384,
        'e': 1157442765409226768,
        'f': 2314885530818453536,
        'g': 4629771061636907072,
        'h': 9259542123273814144
    }

    def adjacents(self, mask):
        v = (mask & ~MoveGen.bb_ranks[8]) << 8
        v |= (mask & ~MoveGen.bb_files['h']) << 1
        v |= mask >> 8
        v |= (mask & ~MoveGen.bb_files['a']) >> 1
        return v

    def frozenmask(self, side=None):
        if not side:
            side = self.gs.turn()
        # first mask all pieces
        v = self.gs.mask(MoveGen.all_pieces[side])
        # next mask all missing friendly adjacents
        v &= ~self.adjacents(v)
        return v

    def get_moves(self, side=None):
        cache = {}  # maps (what, where) -> when, i.e. piece and square to move #

    @staticmethod
    def debug(mask):
        s = ' +-----------------+\n'
        for r in range(7, -1, -1):
            s += '%s| ' % (r + 1)
            for f in range(8):
                if mask & (1 << (8 * r + f)) != 0:
                    s += 'O '
                else:
                    if (r, f) in {(2, 2), (5, 2), (2, 5), (5, 5)}:
                        s += 'x '
                    else:
                        s += '  '
            s += '|\n'
        s += ' +-----------------+\n   %s\n' % ' '.join('abcdefgh')
        print(s)

if __name__ == '__main__':
    import gamestate

    moves = """1g Ra1 Rb1 Rc1 Rd1 Ce1 Rf1 Rg1 Rh1 Ra2 Hb2 Dc2 Hd2 Ee2 Cf2 Mg2 Dh2
1s ha7 mb7 cc7 dd7 he7 ef7 cg7 dh7 ra8 rb8 rc8 rd8 re8 rf8 rg8 rh8
2g Ee2n Dh2n Ee3n Dh3w
2s cg7s ef7s ef6s rf8s
3g Hb2n Ee4n Ee5n Ee6w
3s mb7s ef5w ee5w ha7s
4g Ed6e dd7s Ce1n Ce2n
4s mb6s mb5s mb4n Hb3n
5g Rb1n Rb2n Hb4e Hc4s
5s dh7s cg6n dh6w ha6s
6g Rb3w Ee6s Ee5s Ee4w
6s ha5s ha4e hb4s he7s
7g Cf2w Mg2w Ed4w Ec4w
7s ed5s ed4s he6s he5s
8g Mf2n Mf3n Mf4s he4e
8s dg6w df6s hf4w rb8s
9g Eb4e mb5s Mf3n Ce2e
9s mb4n ed3n he4n ed4e
10g Dg3n Ec4w Mf4s Ce3s
10s ee4s ee3w rb7s df5n
11g Eb4e hb3n Hc3w Dg4e
11s hb4w ed3e df6e rh8s
12g Ec4n Ec5e mb5e Mf3e
12s ee3n he5n dd6w mc5w
13g Ed5w mb5s Ec5w Rd1e
13s mb4e Hb3n mc4n Hb4e
14g Eb5s mc5w Hc4s Hc3w
14s ee4w ed4w mb5e ra8s
15g Eb4n mc5e Eb5e
15s ec4e md5n rb6w dc6w
16g Ec5w Eb5s Eb4e ha4e
16s db6s hb4w md6w mc6w
17g Rg1n Ec4n db5s Ec5w
17s db4e dc4n ed4w dc5n
18g Eb5s mb6s mb5w Eb4n
18s dc6e ec4w dg6w rd8s
19g Eb5e ma5e Ec5s mb5e
19s eb4n mc5n ha4n Ra3n
20g Ra2n Ec4n Ec5e mc6s
20s eb5s eb4e mc5n ec4e
21g Ce2n Ed5w Ec5e mc6s
21s Ra4e ha5s Rb4e ha4e
22g Ce3w Ed5e Ee5w he6s
22s ed4e Cd3n he5n hb4w
23g Hd2n Rc4w mc5s Ed5w
23s Cd4n ee4w Rb4n mc4w
24g Hb3e Ec5s mb4s Ec4w
24s dd6w Cd5n ed4w ra6s
25g mb3s Eb4s Hd3n Rb5e
25s dc6w Cd6w Rc5w Cc6x ec4n
26g Dh4n Hc3e Hd4e He4e
26s ec5s ec4e ed4e df6e
27g Eb3e mb2n Ec3n mb3e mc3x
27s Hf4n ee4e Hf5n Hf6x ef4n
28g Ec4w Rb5e Eb4n ha4e
28s ef5w ee5s ee4w ed4w
29g hb4s Eb5s hb3s Eb4s
29s db6e dc6w Rc5n Rc6x ra7s
30g Mg3n Rg2n Mg4n Hd3s
30s ec4e ed4e ee4e ef4e
31g Mg5w Mf5w Me5s Me4s
31s eg4w ef4w ee4w ed4s
32g Cf2w Rf1n Me3e Hd2s
32s ra5s ra6s cc7s rc8s
33g Hd1n Mf3n Mf4n Mf5e
33s ed3n ed4e ee4e ef4e
34g Mg5w Mf5w Me5s he6s
34s eg4w Me4w ef4w he5n
35g Hd2n Md4w Hd3s Mc4s
35s ee4s ee3w he6s he5e
36g Eb3n Mc3w Re1e Dh5s
36s hf5e hg5e dg6s cc6e
37g Ce2n Rg3e Dh4w Dg4s
37s ed3n ed4w db6s hh5s
38g Hd2e Rf2e He2e Hf2n
38s hh4w Rh3n dg5e hg4n
39g Dg3n Rg2w Dg4w Df4w
39s dh5n Rh4n cd6w cc6w
40g Hf3n De4n Ce3n Hf4n
40s dh6w dg6w df6w cg7s
41g Ce4s De5s Hf5s Hf4e
41s cg6e ch6w Rh5n rd7s
42g Hg4e Hh4n Ce3s De4s
42s cg6n Rh6w Rg6w Rf6x cg7s
43g Rh1n Hh5s Hh4w Hg4s
43s db5e cb6s rc7w rb7s
44g Ra1n Dc2n Rc1n Dc3e
44s dc5e rd6w rc6s rh7s
45g Rh2n Hg3n Rf2e Ce2e
45s de6s re8s re7s rg8s
46g Rg2n Cf2w Rf1n Dd3s
46s dd5s hg5w hf5s rh6s
47g Dd2n Mb3e Rc2e Mc3s
47s hf4w he4e De3n
48g Rh3n Hg4n Hg5w rh5w
48s rg5e cg6s cg5s rg7s
49g Ce2n Ce3e Rg3e Cf3e
49s re6e cg4n Rh4w rh5s
50g Mc2n Rd2w Mc3w
50s dd4n de5n De4n hf4w
51g Hf5s cg5w Dd3n Rg4n
51s Rg5s cf5e Dd4s ec4e
52g Eb4e ra4e Ra3n Hf4n
52s Dd3s ed4s dd5s rc5e
53g Hf5s cg5w Rg4n Cg3n
53s Rg5e cf5e rg6e rf6e
54g Cg4s Hf4e cg5w Hg4n
54s de6e De5n he4n dd4e
55g cf5s Hg5w cf4s cf3x Hf5s
55s rg6s df6e de4w
56g dd4e Ec4e Hf4n de4e
56s ed3e ee3n df4e ee4e
57g rd5n Ed4n Ed5s he5w
57s hd5e Cg3w dg4s
58g Ed4e Ee4s he5s Rf2e
58s dg3n Rh3w rh4s rh3s
59g Cf3s Cf2s Cf1e Cg1e
59s Rg3e dg4s he4n
60g Dd2e De2e Df2s Df1e
60s De6n he5n rg5s dg6s
61g Mb3w hb2n hb3e hc3x Ma3e
61s Hf5n Hf6x ef4n rg4w ef5w
62g Rg2w Dg1n Ra2n
62s ee5w ed5s ed4s rb4e
63g Ee3e Ef3w dg3w Dg2n
63s Rf2e df3s rc4s cb5e
64g Mb3n Ra3e Mb4e
64s he6e De7s hf6e De6e Df6x
65g Ee3s Ee2n df2w Rg2w
65s rd6s cc5w rf4w
66g Ch1w Cg1n Mc4w
66s rd5w rc5s dg5s Rh5w
67g rc4e Mb4e Cg2s Cg1e
67s Rg5w dg4n Rf5n Rf6x dg5w
68g Dg3w Rh3w rh2n Ch1n
68s cb5s rb6s Rb3w cb4s
69g Mc4w cb3s Mb4s
69s rb5e rc5s ed3s rd4s
70g cb2s Mb3s rd3n Ee3w
70s rc3w rc4w rd4w df5s
71g Df3w re4n De3n De4w
71s Rc2s ed2w df4e hg6w
72g rh3n Ch2n rc4n Dd4w
72s Rg3w dg4s Rf2s Rf3x de2e
73g Dc4e rb4e Ra4e Rb4n
73s hf6w he6w hd6w hc6w
74g Ed3e Ee3s Dd4s Dd3s
74s Mb2w ec2w Rc1e cb1e
75g Rd1e Dd2w Ma2s Ma1e
75s Dc2n Dc3x eb2e cc1e rc4s
76g df2n Ee2e Re1n Re2w
76s ec2w rc3s rc2s
77g""".split('\n')

    gs = gamestate.GameState()

    for move in moves:
        gs.move(move)
    # gs.takeback()

    mg = MoveGen(gs)
    print(gs.boardstr(flippable=True))
    MoveGen.debug(mg.frozenmask())