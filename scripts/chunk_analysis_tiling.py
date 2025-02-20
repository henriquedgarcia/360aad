import asyncio
import os
from collections import defaultdict

import numpy as np
import pandas as pd
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
        self.make_boxplot_tiling()
        self.make_violinplot_tiling()

    def make_boxplot_tiling(self):
        print(f'make_boxplot_tiling.')
        for self.metric in self.dataset_structure:
            # Check files (do not use pdf. very much object)
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            serie_list = [self.get_chunk_data()
                          for self.tiling in self.tiling_list]

            fig = plt.figure(figsize=(6, 2.4), layout='tight', dpi=300)

            ax: plt.Axes = fig.add_subplot(1, 1, 1)
            ax.boxplot(serie_list, tick_labels=list(self.tiling_list))
            ax.set_xlabel(f'Tiling')
            ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
            if self.metric == 'dash_m4s':
                ax.ticklabel_format(axis='y', style='scientific',
                                    scilimits=(6, 6))

            fig.suptitle(f'{self.metric}')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_tiling(self):
        print(f'make_violinplot_tiling')
        for self.metric in self.dataset_structure:
            # Check files (do not use pdf. very much object)
            violinplot_path = self.violinplot_folder / f'violinplot_{self.metric}.png'
            if violinplot_path.exists():
                print(f'\t{violinplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            serie_list = [self.get_chunk_data()
                          for self.quality in self.tiling_list]

            fig = plt.figure(figsize=(6, 2.4), layout='tight', dpi=300)

            ax: plt.Axes = fig.add_subplot(1, 1, 1)
            ax.violinplot(serie_list, showmeans=False, showmedians=True)
            ax.set_xticks(list(range(1, len(self.tiling_list) + 1)), self.tiling_list)
            ax.set_xlabel(f'Tiling')
            ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
            if self.metric == 'dash_m4s':
                ax.ticklabel_format(axis='y', style='scientific',
                                    scilimits=(6, 6))

            fig.suptitle(f'{self.metric}')
            fig.savefig(violinplot_path)
            fig.clf()
            plt.close()

    def get_chunk_data(self) -> pd.Series:
        chunk_data: pd.Series = self.database.xs((self.tiling,), level=('tiling',))['value']
        return chunk_data


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisTiling(config)
