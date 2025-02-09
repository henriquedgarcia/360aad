import argparse
import json
import os

from scripts.chunk_analysis_general import ChunkAnalysisGeneral
from scripts.chunk_analysis_tiling import ChunkAnalysisTiling
from scripts.chunk_analysis_quality import ChunkAnalysisQuality
from scripts.chunk_analysis_tiling_quality import (ChunkAnalysisTilingQuality, ChunkAnalysisTilingQualityQuality, ChunkAnalysisTilingQualityTime)
from scripts.chunk_analysis_tiling_quality_name import ChunkAnalysisTilingQualityName
from scripts.config import Config
from scripts.fix_database import FixDatabase
from scripts.tile_analysis_tiling_quality import TileAnalysisTilingQuality, TileAnalysisTilingQualityTime, TileAnalysisTilingQualityQuality

workers = {0: FixDatabase.__name__,
           1: ChunkAnalysisGeneral.__name__,
           2: ChunkAnalysisTiling.__name__,
           3: ChunkAnalysisQuality.__name__,
           4: ChunkAnalysisTilingQuality.__name__,
           5: ChunkAnalysisTilingQualityName.__name__,
           6: TileAnalysisTilingQuality.__name__,
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
