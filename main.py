import argparse
import json

from scripts.chunkgeneralanalysis import (ChunkAnalysisGeneralQuality, ChunkAnalysisGeneralBitrate, ChunkAnalysisGeneralTime, )
from scripts.chunk_analysis_tiling_quality import (ChunkAnalysisTilingQualityBitrate, ChunkAnalysisTilingQualityQuality, ChunkAnalysisTilingQualityTime)
from scripts.tile_analysis_tiling_quality import TileAnalysisTilingQualityBitrate, TileAnalysisTilingQualityTime, TileAnalysisTilingQualityQuality
from scripts.config import Config


workers = {1: ChunkAnalysisGeneralBitrate.__name__,
           2: ChunkAnalysisGeneralTime.__name__,
           3: ChunkAnalysisGeneralQuality.__name__,
           4: ChunkAnalysisTilingQualityBitrate.__name__,
           5: ChunkAnalysisTilingQualityTime.__name__,
           6: ChunkAnalysisTilingQualityQuality.__name__,
           7: TileAnalysisTilingQualityBitrate.__name__,
           8: TileAnalysisTilingQualityTime.__name__,
           9: TileAnalysisTilingQualityQuality.__name__,
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
