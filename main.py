import argparse
import json

from scripts.chunkgeneralanalysis import (QualityChunkGeneralAnalysis, BitrateChunkGeneralAnalysis, TimeChunkGeneralAnalysis, )
from scripts.chunktilingqualitygeneralanalysis import (BitrateTilingQualityGeneralAnalysis, QualityTilingQualityGeneralAnalysis, TimeTilingQualityGeneralAnalysis)
from scripts.config import Config

config = Config()

workers = {1: BitrateChunkGeneralAnalysis.__name__, 2: TimeChunkGeneralAnalysis.__name__, 3: QualityChunkGeneralAnalysis.__name__, 4: BitrateTilingQualityGeneralAnalysis.__name__,
    5: TimeTilingQualityGeneralAnalysis.__name__, 6: QualityTilingQualityGeneralAnalysis.__name__, }

help_txt = 'WORKERS = ' + json.dumps(workers, indent=4)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=help_txt)

    parser.add_argument('worker', type=int, metavar='WORKER', nargs='?', default=None, help=f'A worker name.')

    worker_id = parser.parse_args().worker
    while True:
        if worker_id not in workers:
            try:
                worker_id = int(input(help_txt))
            except ValueError:
                continue
            break

    worker_str = workers[worker_id]
    worker_class = globals()[worker_str]

    print(worker_str)
    worker_class(config)


if __name__ == '__main__':
    main()
