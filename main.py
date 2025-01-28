from scripts.chunkgeneralanalysis import QualityChunkGeneralAnalysis, BitrateChunkGeneralAnalysis, TimeChunkGeneralAnalysis, GetTilesChunkGeneralAnalysis
from scripts.config import Config
from scripts.fix_database import FixDatabase
from scripts.tilingqualitygeneralanalysis import BitrateTilingQualityGeneralAnalysis


class App:
    def __init__(self):
        """
        metric = 'bitrate' | 'time' | 'chunk_quality' | 'get_tiles
        """
        config = Config()
        # ChunkGeneralAnalysis
        # BitrateChunkGeneralAnalysis(config)
        # TimeChunkGeneralAnalysis(config)
        QualityChunkGeneralAnalysis(config)
        # GetTilesChunkGeneralAnalysis(config)

        # print('ByTilingByQuality')
        # BitrateTilingQualityGeneralAnalysis(config)


        # ByQuality(config, 'bitrate')
        # print('ByTiling')
        # ByTiling(config, 'bitrate')
        # print('ByTilingByQuality')
        # ByTilingByQuality(config, 'bitrate')

        # config = Config()
        # FixDatabase(config)


App()
