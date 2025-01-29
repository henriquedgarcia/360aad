import argparse
import json

from scripts.config import Config

from scripts.app import ByTilingByQuality, ByTiling, ByQuality
from scripts.chunkgeneralanalysis import (QualityChunkGeneralAnalysis,
                                          BitrateChunkGeneralAnalysis,
                                          TimeChunkGeneralAnalysis,
                                          GetTilesChunkGeneralAnalysis)
from scripts.fix_database import FixDatabase
from scripts.tilingqualitygeneralanalysis import BitrateTilingQualityGeneralAnalysis

config = Config()

workers = {
    1: BitrateChunkGeneralAnalysis.__name__,
    2: TimeChunkGeneralAnalysis.__name__,
    3: QualityChunkGeneralAnalysis.__name__,
    4: GetTilesChunkGeneralAnalysis.__name__,
    5: BitrateTilingQualityGeneralAnalysis.__name__,
    6: FixDatabase.__name__,
    7: ByTilingByQuality.__name__,
    8: ByTiling.__name__,
    9: ByQuality.__name__
}


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='WORKERS = ' + json.dumps(workers, indent=4))

    parser.add_argument('worker', type=int, metavar='WORKER',
                        help=f'A worker name.')
    worker_id = parser.parse_args().worker
    worker_str = workers[worker_id]
    worker_class = globals()[worker_str]

    print(worker_str)
    worker_class(config)


if __name__ == '__main__':
    main()
