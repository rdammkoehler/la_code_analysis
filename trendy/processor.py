import json
import os
from sys import stderr
from dateutil import parser as du_parser

from trendy import analyze


class LACodeAnalysisStatisticsReader:
    ex = {
        "method_lines": [
            {
                "datetime": "2017-12-21T13:42:29-05:00",
                "mean": 12.067264573991032,
                "median": 8,
                "mode": 3,
                "min": 3,
                "max": 240,
                "stdev": 20.12774417879417,
                "max_method": [
                    {
                        "name": "setUp",
                        "file": "/components/aar-library/src/test/java/com/ford/aar/weather/scheduler/unittesting/WeatherInfoServiceSchedulerTests.java"
                    }
                ]
            },
        ],
    }

    def load(self, filename, measure='method_lines', statistic='mean'):
        exes = list()
        whys = list()
        with open(filename) as fin:
            statistics = json.load(fin)
            if measure not in statistics:
                print(f'measurement {measure} not found in input file {filename}', file=stderr)
                os.exit(1)
            measurement_data = statistics.get(measure)
            for measurement in measurement_data:
                exes.append(du_parser.parse(measurement.get('datetime')))
                whys.append(measurement.get(statistic))
            return exes, whys
        raise Exception(f'Failed to load statistics file {filename}')


def pap_print(parr):
    for pair in zip(*parr):
        print(f'{pair[0]}\t=>\t{pair[1]}')


def date_to_linear_offset(dates):
    return [date.timestamp() for date in dates]


def process(args):
    verbose = False if args.quite is None else False if args.quite else True
    data = LACodeAnalysisStatisticsReader().load(args.inputfile, args.measure)
    # pap_print(data)
    data = (date_to_linear_offset(data[0]), data[1])
    result = analyze(data, verbose)
    print(result)

