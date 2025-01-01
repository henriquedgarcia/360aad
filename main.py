from scripts.chunkgeneralanalysis import QualityChunkGeneralAnalysis, BitrateChunkGeneralAnalysis
from scripts.config import Config
from scripts.fix_database import FixDatabase


class App:
    def __init__(self):
        """
        metric = 'bitrate' | 'time' | 'chunk_quality' | 'get_tiles
        """
        config = Config()
        # ChunkGeneralAnalysis
        BitrateChunkGeneralAnalysis(config)
        # TimeChunkGeneralAnalysis(config)
        # QualityChunkGeneralAnalysis(config)
        # GetTilesChunkGeneralAnalysis(config)

        # print('ByQuality')
        # ByQuality(config, 'bitrate')
        # print('ByTiling')
        # ByTiling(config, 'bitrate')
        # print('ByTilingByQuality')
        # ByTilingByQuality(config, 'bitrate')

        # config = Config()
        # FixDatabase(config)


App()
