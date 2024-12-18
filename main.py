from scripts.chunkgeneralanalysis import BitrateChunkGeneralAnalysis, TimeChunkGeneralAnalysis, QualityChunkGeneralAnalysis, GetTilesChunkGeneralAnalysis
from scripts.config import Config


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

        # print('ByQuality')
        # ByQuality(config, 'bitrate')
        # print('ByTiling')
        # ByTiling(config, 'bitrate')
        # print('ByTilingByQuality')
        # ByTilingByQuality(config, 'bitrate')


App()
