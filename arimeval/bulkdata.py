from arimeval.settings import settings
import glob
import csv
import sys
import os

input_fieldnames = \
    ('id', 'wplayerid', 'bplayerid', 'wusername', 'busername',
     'wtitle', 'btitle', 'wcountry', 'bcountry', 'wrating',
     'brating', 'wratingk', 'bratingk', 'wtype', 'btype',
     'event', 'site', 'timecontrol', 'postal', 'startts',
     'endts', 'result', 'termination', 'plycount', 'mode',
     'rated', 'corrupt', 'movelist', 'events')

output_fieldnames = \
    ('id', 'game', 'wrating', 'brating', 'result', 'termination', 'movelist')


def process(row, writer, rid):
    if row['id'] != 'id' and row['corrupt'] == '0' and \
                    int(row['wrating']) >= settings['min-rating'] and \
                    int(row['brating']) >= settings['min-rating'] and (
                    row['termination'] == 'g' or
                    row['termination'] == 'm'):
        writer.writerow(dict(zip(
            output_fieldnames,
            (rid, row['id'], row['wrating'], row['brating'],
             row['result'], row['termination'], row['movelist']))))
        rid += 1
    return rid


def main(argv):
    csv.field_size_limit(1600000)
    fn = os.path.join(settings['data-base'], 'games', '*.txt')
    games_glob = glob.glob(fn)
    fn = os.path.join(settings['data-base'], 'expert', 'expert.csv')
    games_writer = csv.DictWriter(open(fn, 'w'), output_fieldnames, dialect='unix')
    games_writer.writeheader()
    rid = 1
    for gl in games_glob:
        with open(gl) as games_file:
            games_reader = csv.DictReader(
                games_file,
                delimiter='\t',
                fieldnames=input_fieldnames)
            for row in games_reader:
                rid = process(row, games_writer, rid)


if __name__ == '__main__':
    main(sys.argv)
