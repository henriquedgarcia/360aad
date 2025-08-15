import argparse
import json

from scripts.serie_analysis_tiling_quality_chunk import SerieAnalysisTilingQualityChunk
from scripts.utils.config import Config

workers = {0: SerieAnalysisTilingQualityChunk.__name__,
           }

help_txt = 'WORKERS = ' + json.dumps(workers, indent=4) + ': '


def main():
    worker_class = menu()
    worker_class(Config())


def menu():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=help_txt)
    parser.add_argument('worker', type=int, metavar='WORKER', nargs='?', default=None, help=f'A worker name.')

    worker_id = parser.parse_args().worker
    while True:
        if worker_id in workers:
            break
        try:
            worker_id = int(input(help_txt))
        except ValueError:
            worker_id = None

    worker_str = workers[worker_id]
    return globals()[worker_str]


if __name__ == '__main__':
    main()
