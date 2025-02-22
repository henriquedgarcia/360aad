import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict


class ChunkAnalysisTilingQuality(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    chunk_data = self.get_chunk_data()
                    self.stats_defaultdict['Metric'].append(self.metric)
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['n_arquivos'].append(len(chunk_data))
                    self.stats_defaultdict['Média'].append(chunk_data.mean())
                    self.stats_defaultdict['Desvio Padrão'].append(chunk_data.std())
                    self.stats_defaultdict['Mínimo'].append(chunk_data.quantile(0.00))
                    self.stats_defaultdict['1º Quartil'].append(chunk_data.quantile(0.25))
                    self.stats_defaultdict['Mediana'].append(chunk_data.quantile(0.50))
                    self.stats_defaultdict['3º Quartil'].append(chunk_data.quantile(0.75))
                    self.stats_defaultdict['Máximo'].append(chunk_data.quantile(1.00))

    def get_chunk_data(self) -> pd.Series:
        chunk_data: pd.Series = self.database.xs(key=(self.tiling, self.quality),
                                                 level=('tiling', 'quality'))['value']
        return chunk_data

    def plots(self):
        self.make_boxplot_quality_tiling()
        self.make_boxplot_tiling_quality()
        self.make_violinplot_quality_tiling()
        self.make_violinplot_tiling_quality()
        self.make_barplot_quality_tiling()
        self.make_barplot_tiling_quality()

    def make_barplot_quality_tiling(self):
        print(f'make_barplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            barplot_path = self.barplot_folder / f'barplot_quality_tiling_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            # Load Database
            self.load_database()
            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            for i, self.quality in enumerate(self.quality_list, 1):
                ax: plt.Axes = fig.add_subplot(3, 2, i)
                data = []
                for x, self.tiling in enumerate(self.tiling_list):
                    data.append(self.get_chunk_data().mean())
                    ax.bar(x, data[-1])

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)),
                              [f"{tiling}" for tiling in self.tiling_list])

                if self.metric == 'mse':
                    ma = max(data)
                    mi = min(data)
                    rg = (ma - mi) * 0.05
                    ax.set_ylim(bottom=mi + rg, top=ma + rg)
                elif self.metric == 'ssim':
                    ax.set_ylim(bottom=0.8)
                elif 'dectime' in self.metric:
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(-3, -3))
                elif self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.suptitle(f'{self.metric}')
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_barplot_tiling_quality(self):
        print(f'make_barplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            barplot_path = self.barplot_folder / f'barplot_tiling_quality_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            # Load Database
            self.load_database()
            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            for i, self.tiling in enumerate(self.tiling_list, 1):
                ax: plt.Axes = fig.add_subplot(3, 2, i)
                data = []
                for x, self.quality in enumerate(self.quality_list):
                    data.append(self.get_chunk_data().mean())
                    ax.bar(x, data[-1])

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality (QP)')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.quality_list)),
                              [f"qp{quality}" for quality in self.quality_list])

                if self.metric == 'mse':
                    ma = max(data)
                    mi = min(data)
                    rg = (ma - mi) * 0.05
                    ax.set_ylim(bottom=mi + rg, top=ma + rg)
                elif self.metric == 'ssim':
                    ax.set_ylim(bottom=0.8)
                elif 'dectime' in self.metric:
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(-3, -3))
                elif self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.suptitle(f'{self.metric}')
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_quality_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'\r\tPlot qp{self.quality}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data()
                              for self.tiling in self.tiling_list]
                ax.boxplot(serie_list, tick_labels=list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            print(f'\n\tSaving.')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_tiling_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'\r\tPlot {self.tiling}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data()
                              for self.quality in self.quality_list]
                ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            print(f'\n\tSaving.')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_quality_tiling(self):
        print(f'make_violinplot_quality_tiling_frame.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.violinplot_folder / f'violinplot_quality_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'\r\tPlot qp{self.quality}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data()
                              for self.tiling in self.tiling_list]
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            print(f'\n\tSaving.')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_tiling_quality(self):
        print(f'make_violinplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.violinplot_folder / f'violinplot_tiling_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'\r\tPlot {self.tiling}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data()
                              for self.quality in self.quality_list]
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            print(f'\n\tSaving.')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisTilingQuality(config)
