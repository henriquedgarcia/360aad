import argparse
import json

from scripts.app import ByTilingByQuality, ByTiling, ByQuality
from scripts.chunkgeneralanalysis import (QualityChunkGeneralAnalysis,
                                          BitrateChunkGeneralAnalysis,
                                          TimeChunkGeneralAnalysis,
                                          GetTilesChunkGeneralAnalysis)
from scripts.config import Config
from scripts.fix_database import FixDatabase
from scripts.tilingqualitygeneralanalysis import BitrateTilingQualityGeneralAnalysis

config = Config()

workers = {
    1: BitrateChunkGeneralAnalysis,
    2: TimeChunkGeneralAnalysis,
    3: QualityChunkGeneralAnalysis,
    4: GetTilesChunkGeneralAnalysis,
}


class App:
    def __init__(self, worker):
        """
        metric = 'bitrate' | 'time' | 'chunk_quality' | 'get_tiles
        """
        worker = workers[worker]
        print(worker.__class__.__name__)
        worker(config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=json.dumps(workers, indent=4))

    parser.add_argument('worker', type=int, metavar='WORKER',
                        help=f'A worker name.')

    args = parser.parse_args()
    App(args.worker)
    print(f'\nThe end.')
