import os
from collections import defaultdict

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import load_pd_pickle

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


class SitiData:
    def __init__(self, filename, context: AnalysisBase):
        self.level = ['name', 'projection', 'tiling', 'tile', 'quality']
        self.columns = ['si', 'ti']
        self.data: pd.DataFrame = load_pd_pickle(filename)
        self.context = context

    def __getitem__(self, column) -> pd.Series:
        key = tuple(getattr(self.context, level) for level in self.level)
        return self.data.xs(key=key, level=self.level)[column]

    def group_by(self, level: list[str, ...], operation) -> pd.DataFrame:
        groupped = self.data.groupby(level=level)
        return groupped.apply(operation)


class AnalysisSiti(AnalysisBase):
    siti: SitiData
    keys: list

    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        self.tiling = '3x2'
        self.quality = 28
        self.projection = 'cmp'
        self.keys = ['name', 'projection', 'tiling', 'tile', 'quality']
        self.tiling_list = self.tiling_list[1:]
        self.siti = SitiData(f'dataset/siti.pickle', self)

    def make_stats(self):
        for self.name in self.name_list:
            for self.tile in self.tile_list:
                si = pd.Series(self.siti['si'].iloc[0])
                ti = pd.Series(self.siti['ti'].iloc[0])
                self.stats_defaultdict['Metric'].append(self.name)
                self.stats_defaultdict['Tiling'].append(self.tiling)
                self.stats_defaultdict['Quality'].append(self.quality)
                self.stats_defaultdict['Tile'].append(self.tile)

                self.stats_defaultdict['si_Média'].append(si.mean())
                self.stats_defaultdict['si_Desvio Padrão'].append(si.std())
                self.stats_defaultdict['si_Mínimo'].append(si.quantile(0.00))
                self.stats_defaultdict['si_1º Quartil'].append(si.quantile(0.25))
                self.stats_defaultdict['si_Mediana'].append(si.quantile(0.50))
                self.stats_defaultdict['si_3º Quartil'].append(si.quantile(0.75))
                self.stats_defaultdict['si_Máximo'].append(si.quantile(1.00))

                self.stats_defaultdict['ti_Media'].append(ti.mean())
                self.stats_defaultdict['ti_Desvio Padrão'].append(ti.std())
                self.stats_defaultdict['ti_Mínimo'].append(ti.quantile(0.00))
                self.stats_defaultdict['ti_1º Quartil'].append(ti.quantile(0.25))
                self.stats_defaultdict['ti_Mediana'].append(ti.quantile(0.50))
                self.stats_defaultdict['ti_3º Quartil'].append(ti.quantile(0.75))
                self.stats_defaultdict['ti_Máximo'].append(ti.quantile(1.00))

    def plots(self):
        self.plot1()

    def plot1(self):
        tile_map = {0: 'left', 1: 'front', 2: 'right', 3: 'down', 4: 'back', 5: 'top'}

        def plot_path():
            filename = self.graphs_workfolder / 'quality_tiling' / 'plot_by_tile' / f'plot_{self.name}.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        for self.name in self.name_list:
            fig = plt.Figure(figsize=(8, 5), dpi=300, tight_layout=True)
            ax1 = fig.add_subplot(2, 1, 1)
            ax2 = fig.add_subplot(2, 1, 2)

            for self.tile in self.tile_list:
                si = pd.Series(self.siti['si'].iloc[0])
                ti = pd.Series(self.siti['ti'].iloc[0])

                ax1.plot(si, label=f'{tile_map[self.tile]}')
                ax2.plot(ti, label=f'{tile_map[self.tile]}')

            ax1.legend()
            ax1.set_title(f'SI')
            ax2.legend()
            ax2.set_title(f'TI')
            fig.suptitle(f'{self.name}')
            fig.savefig(plot_path())
            plt.close()

    def plot2(self):
        tile_map = {0: 'left', 1: 'front', 2: 'right', 3: 'down', 4: 'back', 5: 'top'}

        def plot_path():
            filename = self.graphs_workfolder / 'quality_tiling' / 'plot_by_tile' / f'plot2_{self.name}.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        for self.name in self.name_list:
            fig = plt.Figure(figsize=(8, 5), dpi=300, tight_layout=True)
            ax1 = fig.add_subplot(2, 1, 1)
            ax2 = fig.add_subplot(2, 1, 2)

            for self.tile in self.tile_list:
                si = pd.Series(self.siti['si'].iloc[0])
                ti = pd.Series(self.siti['ti'].iloc[0])
                si_ = []
                ti_ = []
                for n in range(0, len(si), 30):
                    si_.append(np.average(si[n:n + 30]))
                    ti_.append(np.average(ti[n:n + 30]))

                ax1.plot(si_, label=f'{tile_map[self.tile]}')
                ax2.plot(ti_, label=f'{tile_map[self.tile]}')

            ax1.legend()
            ax1.set_title(f'SI')
            ax2.legend()
            ax2.set_title(f'TI')
            fig.suptitle(f'{self.name}')
            fig.savefig(plot_path())
            plt.close()

    def heatmap(self):
        tile_map = {0: 'left', 1: 'front', 2: 'right', 3: 'down', 4: 'back', 5: 'top'}

        def plot_path():
            filename = self.graphs_workfolder / 'quality_tiling' / 'plot_by_tile' / f'plot_{self.name}.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        for self.name in self.name_list:
            fig = plt.Figure(figsize=(8, 5), dpi=300, tight_layout=True)
            ax1 = fig.add_subplot(2, 1, 1)
            ax2 = fig.add_subplot(2, 1, 2)

            for self.tile in self.tile_list:
                si = pd.Series(self.siti['si'].iloc[0])
                ti = pd.Series(self.siti['ti'].iloc[0])

                ax1.plot(si, label=f'{tile_map[self.tile]}')
                ax2.plot(ti, label=f'{tile_map[self.tile]}')

            ax1.legend()
            ax1.set_title(f'SI')
            ax2.legend()
            ax2.set_title(f'TI')
            fig.suptitle(f'{self.name}')
            fig.savefig(plot_path())
            plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    AnalysisSiti(config)
