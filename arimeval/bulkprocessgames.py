# not used.

from arimeval.settings import settings
import glob
import os


if __name__ == '__main__':
    fn = os.path.join(settings['data-base'], 'gameData', '*.txt')
    games_glob = glob.glob(fn)
    for fn in games_glob:
        print(fn)
        with open(fn, 'r+', encoding='utf-8') as games_file:
            lines = games_file.readlines()
            if 'allgames201205' in fn:
                continue
            elif 'allgames200811' in fn:
                continue
            for line in lines:
                line = str(line.encode('ascii', 'ignore'))
                # games_file.write(str('\t'.join(line.split('\t')[:-1]) + '\n'))

