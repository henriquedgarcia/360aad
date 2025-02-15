import asyncio
import os
from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict

lock = asyncio.Lock()


class ChunkAnalysisTiling(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        del self.dataset_structure['dectime_std']

    def make_stats(self):
        print(f'make_stats')
        self.stats_defaultdict = defaultdict(list)
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                bucket = list(self.database.xs(self.tiling, level='tiling')['value'])

                self.stats_defaultdict['Metric'].append(self.metric)
                self.stats_defaultdict['Tiling'].append(self.tiling)
                self.stats_defaultdict['n_arquivos'].append(len(bucket))
                self.stats_defaultdict['Média'].append(np.average(bucket))
                self.stats_defaultdict['Desvio Padrão'].append(np.std(bucket))
                self.stats_defaultdict['Mínimo'].append(np.quantile(bucket, 0))
                self.stats_defaultdict['1º Quartil'].append(np.quantile(bucket, 0.25))
                self.stats_defaultdict['Mediana'].append(np.quantile(bucket, 0.5))
                self.stats_defaultdict['3º Quartil'].append(np.quantile(bucket, 0.75))
                self.stats_defaultdict['Máximo'].append(np.quantile(bucket, 1))

    def plots(self):
        self.make_boxplot1()

    def make_boxplot1(self):
        print(f'Boxplot 1.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}.pdf'
            # if boxplot_path_tiling.exists():
            #     print(f'\t{boxplot_path_tiling} exists.')
            #     continue

            self.load_database()

            fig = plt.figure(figsize=(6, 2.4), layout='tight')
            fig.suptitle(f'{self.metric}')
            ax: plt.Axes = fig.add_subplot(1, 1, 1)

            print(f'Making bucket')
            buckets = []
            for self.tiling in self.tiling_list:
                bucket = list(self.database.xs(self.tiling, level='tiling')['value'])
                buckets.append(bucket)

            ax.violinplot(buckets, showmeans=False, showmedians=True)
            ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                          list(self.tiling_list))
            ax.set_xlabel(f'Tiling')
            ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
            fig.savefig(boxplot_path)
            fig.clf()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisTiling(config)
