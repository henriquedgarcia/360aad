import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict


class SerieAnalysisTilingQualityChunk(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        # del self.dataset_structure['dectime_std']

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    serie = self.get_chunk_data()
                    self.stats_defaultdict['Metric'].append(self.metric)
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['Média'].append(serie.mean())
                    self.stats_defaultdict['Desvio Padrão'].append(serie.std())
                    self.stats_defaultdict['Mínimo'].append(serie.quantile(0.00))
                    self.stats_defaultdict['1º Quartil'].append(serie.quantile(0.25))
                    self.stats_defaultdict['Mediana'].append(serie.quantile(0.50))
                    self.stats_defaultdict['3º Quartil'].append(serie.quantile(0.75))
                    self.stats_defaultdict['Máximo'].append(serie.quantile(1.00))

    def load_database(self):
        super(SerieAnalysisTilingQualityChunk, self).load_database()

    def get_chunk_data(self) -> pd.Series:
        chunk_data = self.database.xs((self.tiling, self.quality), level=('tiling', 'quality'))['value']
        return chunk_data

    def plots(self):
        self.make_plot_quality_tiling_frame()
        self.make_plot_tiling_quality_frame()
        self.make_boxplot_quality_tiling_frame()
        self.make_boxplot_tiling_quality_frame()
        self.make_violinplot_quality_tiling_frame()
        self.make_violinplot_tiling_quality_frame()

    def make_plot_quality_tiling_frame(self):
        print(f'make_boxplot_quality_tiling.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.series_plot_folder / f'plot_{self.metric}_quality.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.tiling in self.tiling_list:
                    serie = self.get_chunk_data()
                    ax.plot(serie, label=f'{self.tiling}')

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Chunk')
                ax.legend(loc='upper right')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()

    def make_plot_tiling_quality_frame(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.series_plot_folder / f'plot_{self.metric}_tiling.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.quality in self.quality_list:
                    serie = self.get_chunk_data()
                    ax.plot(serie, label=f'qp{self.quality}')

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Chunk')
                ax.legend(loc='upper right')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()

    def make_boxplot_quality_tiling_frame(self):
        print(f'make_boxplot_quality_tiling.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_quality.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data() for self.tiling in self.tiling_list]
                ax.boxplot(serie_list, tick_labels=list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()

    def make_boxplot_tiling_quality_frame(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_tiling.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data() for self.quality in self.quality_list]
                ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()

    def make_violinplot_quality_tiling_frame(self):
        print(f'make_violinplot_quality_tiling_frame.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_quality.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data() for self.tiling in self.tiling_list]
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()

    def make_violinplot_tiling_quality_frame(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_tiling.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data() for self.quality in self.quality_list]
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    SerieAnalysisTilingQualityChunk(config)
