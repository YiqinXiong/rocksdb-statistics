#!/usr/bin/env python3
import re, argparse
import os


class Statistics:
    def __init__(self):
        self.interval_stall = {
            'name': 'Interval Stall',
            'regex': 'Interval\sstall.*?(\d*\.\d*)\spercent',
            'suffix': '_interval_stall'
        }
        self.cumulative_stall = {
            'name': 'Cumulative Stall',
            'regex': 'Cumulative\sstall.*?(\d*\.\d*)\spercent',
            'suffix': '_cumulative_stall'
        }
        self.interval_writes = {
            'name': 'Interval Writes',
            'regex': 'Interval\swrites.*?(\d*\.\d*)\sMB\/s',
            'suffix': '_interval_writes'
        }
        self.cumulative_writes = {
            'name': 'Cumulative Writes',
            'regex': 'Cumulative\swrites.*?(\d*\.\d*)\sMB\/s',
            'suffix': '_cumulative_writes'
        }
        self.cumulative_compaction = {
            'name': 'Cumulative Compaction',
            'regex': 'Cumulative\scompaction.*?(\d*\.\d*)\sMB\/s',
            'suffix': '_cumulative_compaction'
        }
        self.interval_compaction = {
            'name': 'Interval Compaction',
            'regex': 'Interval\scompaction.*?(\d*\.\d*)\sMB\/s',
            'suffix': '_interval_compaction'
        }

        self.legend_list = []
        self.base_filename = ''

    def coordinates_filename(self):
        return self.base_filename + '_coordinates.log'

    def save_statistic(self, d, log):
        matches = self.get_matches(d['regex'], log)
        new_filename = self.base_filename + f'{d["suffix"]}.csv'
        self.save_to_file(matches, new_filename)

        coordinates = self.generate_coordinates(matches)
        self.save_coordinates_to_file(coordinates, self.coordinates_filename())
        self.legend_list.append(d["name"])

    def clean_log(self, log):
        regex = re.compile('(2018\S+).*\(([\d,\.]*)\).*\(([\d,\.]*)\).*\(([\d,\.]*)\)')
        path = os.path.join(os.getcwd(), 'output', log)
        with open(path, 'r') as f:

            matches = regex.findall(f.read())
        return [','.join(match) for match in matches]

    def get_matches(self, regex, log):
        regex = re.compile(regex)
        path = os.path.join(os.getcwd(), log)
        with open(path, 'r') as f:
            matches = regex.findall(f.read())
        return matches

    def generate_coordinates(self, matches, step=1):
        return [f'({i*step},{match})' for i, match in enumerate(matches)]

    def save_to_file(self, data, filename):
        os.makedirs('output', exist_ok=True)
        with open(f'output/{filename}', 'w') as f:
            f.writelines('\n'.join(data))

    def save_coordinates_to_file(self, data, filename, last=False):
        os.makedirs('output', exist_ok=True)
        with open(f'output/{filename}', 'a') as f:
            str_data = ''.join(data)
            f.write('\\addplot\n\tcoordinates {{ {0} }};\n'.format(str_data))
            if last:
                legend = ', '.join(self.legend_list)
                f.write(f'\\legend{{{legend}}}\n')

    def append_legend(self, filename):
        with open(f'output/{filename}', 'a') as f:
            legend = ', '.join(self.legend_list)
            f.write(f'\\legend{{{legend}}}\n')
            f.write(f'\\end{{axis}}\n')

    def initialize_coordinate_file(self, filename):
        axis = f"""\\begin{{axis}}[
    title={self.base_filename},
    xlabel={{}},
    ylabel={{MB/s}},
    legend style={{
        at={{(0.5,-0.2)}},
        anchor=north,legend columns=-1
    }},
    ymajorgrids=true,
    grid style=dashed,
]
"""
        with open(f'output/{filename}', 'w') as f:
            f.write(axis)

    def save_all(self, log):
        self.base_filename = log.split('.')[0]
        s.initialize_coordinate_file(self.coordinates_filename())
        s.save_statistic(self.interval_writes, log)
        s.save_statistic(self.cumulative_writes, log)
        s.save_statistic(self.interval_stall, log)
        s.save_statistic(self.cumulative_stall, log)
        s.save_statistic(self.cumulative_compaction, log)
        s.save_statistic(self.interval_compaction, log)
        s.append_legend(self.coordinates_filename())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=str, help="logfile")
    args = parser.parse_args()
    s = Statistics()
    log = args.log
    s.save_all(log)
