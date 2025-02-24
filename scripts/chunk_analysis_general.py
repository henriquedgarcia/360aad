import asyncio
from collections import defaultdict

import numpy as np

from scripts.analysisbase import AnalysisBase
from scripts.utils.utils import AutoDict

lock = asyncio.Lock()


class ChunkAnalysisGeneral(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_stats(self):
        self.stats_defaultdict = defaultdict(list)
        for self.metric in self.dataset_structure:
            self.load_database()

            bucket = list(self.database['value'])

            self.stats_defaultdict['Metric'].append(self.metric)
            self.stats_defaultdict['n_arquivos'].append(len(bucket))
            self.stats_defaultdict['Média'].append(np.average(bucket))
            self.stats_defaultdict['Desvio Padrão'].append(np.std(bucket))
            self.stats_defaultdict['Mínimo'].append(np.quantile(bucket, 0))
            self.stats_defaultdict['1º Quartil'].append(np.quantile(bucket, 0.25))
            self.stats_defaultdict['Mediana'].append(np.quantile(bucket, 0.5))
            self.stats_defaultdict['3º Quartil'].append(np.quantile(bucket, 0.75))
            self.stats_defaultdict['Máximo'].append(np.quantile(bucket, 1))

    def plots(self):
        pass
