import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config


class SerieAnalysisTilingChunkFrame(AnalysisBase):
    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                serie = self.get_chunk_data(('tiling',))
                self.stats_defaultdict['Metric'].append(self.metric)
                self.stats_defaultdict['Tiling'].append(self.tiling)
                self.stats_defaultdict['Média'].append(serie.mean())
                self.stats_defaultdict['Desvio Padrão'].append(serie.std())
                self.stats_defaultdict['Mínimo'].append(serie.quantile(0.00))
                self.stats_defaultdict['1º Quartil'].append(serie.quantile(0.25))
                self.stats_defaultdict['Mediana'].append(serie.quantile(0.50))
                self.stats_defaultdict['3º Quartil'].append(serie.quantile(0.75))
                self.stats_defaultdict['Máximo'].append(serie.quantile(1.00))

    def load_database(self):
        super(SerieAnalysisTilingChunkFrame, self).load_database()
        self.database = self.database.groupby(['tiling', 'tile', 'chunk'], sort=False).mean()

        if self.metric in ['dash_m4s', 'dectime_avg']:
            self.database = self.database.groupby(['tiling', 'chunk'], sort=False).sum()
        else:
            self.database = self.database.groupby(['tiling', 'chunk'], sort=False).mean()

    def plots(self):
        self.make_plot_tiling_frame()
        self.make_boxplot_tiling_frame()
        self.make_violinplot_tiling_frame()

    def make_plot_tiling_frame(self):
        print(f'make_plot_tiling_frame.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.series_plot_folder / f'plot_{self.metric}_tiling.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            self.load_database()

            fig = plt.figure(figsize=(6, 2.4), layout='tight', dpi=300)
            ax: plt.Axes = fig.add_subplot(1, 1, 1)

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')
                serie = self.get_chunk_data(('tiling',))
                ax.plot(serie, label=f'{self.tiling}')

            ax.set_xlabel(f'Chunk')
            ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
            ax.legend(loc='upper right')
            if self.metric == 'dash_m4s':
                ax.ticklabel_format(axis='y', style='scientific',
                                    scilimits=(6, 6))

            fig.suptitle(f'{self.metric}')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_tiling_frame(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_quality.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 2.4), layout='tight', dpi=300)
            ax: plt.Axes = fig.add_subplot(1, 1, 1)

            serie_list = [self.get_chunk_data(('tiling',)) for self.tiling in self.tiling_list]

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

    def make_violinplot_tiling_frame(self):
        print(f'make_violinplot_tiling_frame.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_tiling.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            self.load_database()

            fig = plt.figure(figsize=(6, 2.4), layout='tight', dpi=300)
            ax: plt.Axes = fig.add_subplot(1, 1, 1)

            serie_list = [self.get_chunk_data(('tiling',)) for self.tiling in self.tiling_list]
            ax.violinplot(serie_list, showmeans=False, showmedians=True)
            ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                          list(self.tiling_list))

            ax.set_xlabel(f'Tiling')
            ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
            if self.metric == 'dash_m4s':
                ax.ticklabel_format(axis='y', style='scientific',
                                    scilimits=(6, 6))

            fig.suptitle(f'{self.metric}')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    SerieAnalysisTilingChunkFrame(config)
