import os
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Generator

import matplotlib.patches as mpatches
import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.database import (Data)

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


class ChunkAnalysisTilingQuality(AnalysisBase):
    metrics_datasets: dict[str, Data]
    metric_list: list = None

    def __init__(self, config):
        print(f'{self.class_name} initializing...')
        self.config = config
        self.setup()
        # self.make_stats()
        # self.make_corr()
        self.plots()

    def setup(self):
        self.chunk_data: pd.DataFrame = pd.read_hdf('dataset/chunk_data_qp.hd5')
        self.viewport_quality: pd.DataFrame = pd.read_hdf('dataset/viewport_quality_by_chunk_qp.hd5')

    def make_stats(self):
        print(f'make_stats.')
        stats_csv = self.stats_workfolder / f'{self.class_name}_{self.rate_control}_stats.csv'
        # if stats_csv.exists(): return

        self.stats_defaultdict = defaultdict(list)

        for self.tiling in self.tiling_list:
            for self.quality in self.quality_list:
                for column in self.chunk_data.columns:
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['Metric'].append(column)
                    for self.projection in self.projection_list:
                        data = self.chunk_data[column].xs(key=(self.projection, self.tiling, self.quality),
                                                          level=('projection', 'tiling', 'quality',))
                        self.stats_defaultdict[f'{self.projection} n_samples'].append(len(data))
                        self.stats_defaultdict[f'{self.projection} Média'].append(data.mean())
                        self.stats_defaultdict[f'{self.projection} Desvio Padrão'].append(data.std())
                        self.stats_defaultdict[f'{self.projection} Mínimo'].append(data.quantile(0.00))
                        self.stats_defaultdict[f'{self.projection} Mediana'].append(data.quantile(0.50))
                        self.stats_defaultdict[f'{self.projection} Máximo'].append(data.quantile(1.00))

                for column in self.viewport_quality.columns:
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['Metric'].append(f'{column}_vp')
                    for self.projection in self.projection_list:
                        data = self.viewport_quality[column].xs(key=(self.projection, self.tiling, self.quality),
                                                                level=('projection', 'tiling', 'quality',))
                        self.stats_defaultdict[f'{self.projection} n_samples'].append(len(data))
                        self.stats_defaultdict[f'{self.projection} Média'].append(data.mean())
                        self.stats_defaultdict[f'{self.projection} Desvio Padrão'].append(data.std())
                        self.stats_defaultdict[f'{self.projection} Mínimo'].append(data.quantile(0.00))
                        self.stats_defaultdict[f'{self.projection} Mediana'].append(data.quantile(0.50))
                        self.stats_defaultdict[f'{self.projection} Máximo'].append(data.quantile(1.00))

        stats_df = pd.DataFrame(self.stats_defaultdict)
        stats_df.to_csv(stats_csv, index=False)

    def make_corr(self):
        print(f'make_corr.')
        stats_csv = self.stats_workfolder / f'corr_{self.class_name}_{self.rate_control}_stats.csv'
        stats_defaultdict = []

        # chunk_data_groupby = self.chunk_data.groupby(['name', 'projection', 'tiling', 'quality', 'chunk'])
        # viewport_quality_groupby = self.viewport_quality.groupby(['name', 'projection', 'tiling', 'quality', 'chunk'])

        # chunk_data = pd.DataFrame()
        # chunks
        # chunk_data[['bitrate', 'dectime_serial']] = chunk_data_groupby[['bitrate', 'dectime']].apply()
        # chunk_data[['bitrate', 'dectime_serial']] = chunk_data_groupby[['bitrate', 'dectime']].sum()
        # chunk_data[['dectime_max']] = chunk_data_groupby[['dectime']].max()
        # chunk_data[['ssim', 'mse', 's-mse', 'ws-mse']] = chunk_data_groupby[['ssim', 'mse', 's-mse', 'ws-mse']].mean()
        # # Viewport
        # chunk_data[['vp_mse', 'vp_ssim']] = viewport_quality_groupby[['mse', 'ssim']].mean()
        for self.tiling in self.tiling_list:
            for self.quality in self.quality_list:
                for self.name in self.name_list:
                    for self.projection in self.projection_list:
                        print(f'{self.tiling} qp{self.quality} {self.name} {self.projection} ')
                        data = self.chunk_data.xs(key=(self.name, self.projection, self.tiling, self.quality),
                                                  level=('name', 'projection', 'tiling', 'quality',))

                        corr1 = data.corr(method='pearson')
                        corr2 = data.corr(method='kendall')
                        corr3 = data.corr(method='spearman')

                        if corr1.isna().any().any(): corr1 = corr1.fillna(0)
                        if corr2.isna().any().any(): corr2 = corr2.fillna(0)
                        if corr3.isna().any().any(): corr3 = corr3.fillna(0)

                        unique = [(self.projection, self.tiling, self.quality, self.name, self.tile,
                                   corr1.index[i], corr1.columns[j], corr1.iat[i, j], corr2.iat[i, j], corr3.iat[i, j])
                                  for i in range(len(corr1)) for j in range(i)]

                        stats_defaultdict.extend(unique)

        stats_df = pd.DataFrame(stats_defaultdict, columns=('projection', 'tiling', 'quality', 'name', 'tile',
                                                            'metric1', 'metric2', 'pearson', 'kendall', 'spearman'))
        stats_df.set_index(['projection', 'tiling', 'quality', 'name', 'tile', 'metric1', 'metric2'], inplace=True)
        stats_df_mean = stats_df.groupby(['projection', 'tiling', 'quality', 'metric1', 'metric2']).mean()
        stats_df_mean.to_csv(stats_csv, index=True)

    def plots(self):
        # self.rc_config()

        # self.make_boxplot_quality_tiling()
        self.make_boxplot_tiling_quality()
        #
        # self.make_violinplot_quality_tiling()
        # self.make_violinplot_tiling_quality()
        # self.make_barplot_quality_tiling()
        # self.make_barplot_tiling_quality()

    def make_boxplot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.chunk_data.columns:
            boxplot_path = self.boxplot_folder / 'quality_tiling' / f'boxplot_{self.metric}.png'
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            # if boxplot_path.exists():
            #     print(f'\t{boxplot_path} exists.')
            #     continue

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'\r\tPlot {self.metric} - qp{self.quality}', end='')

                ax: plt.Axes = fig.add_subplot(3, 2, n)

                self.projection = 'erp'
                serie_list = [self.chunk_data[self.metric].xs(key=(self.projection, self.tiling, self.quality), level=('projection', 'tiling', 'quality'))
                              for self.tiling in self.tiling_list]
                ax.boxplot(serie_list, sym='b.', positions=[0 - 0.2, 1 - 0.2, 2 - 0.2, 3 - 0.2, 4 - 0.2], widths=0.4,patch_artist=True, boxprops={"facecolor": "blue"})

                self.projection = 'cmp'
                serie_list = [self.chunk_data[self.metric].xs(key=(self.projection, self.tiling, self.quality), level=('projection', 'tiling', 'quality'))
                              for self.tiling in self.tiling_list]
                ax.boxplot(serie_list, sym='b.', positions=[0 + 0.2, 1 + 0.2, 2 + 0.2, 3 + 0.2, 4 + 0.2], widths=0.4, patch_artist=True, boxprops={"facecolor": "red"})

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks([0,1,2,3,4], list(self.tiling_list))

                azul_patch = mpatches.Patch(color='blue', label='erp')
                red_patch = mpatches.Patch(color='red', label='cmp')
                ax.legend(handles=[azul_patch, red_patch])
                if self.metric == 'bitrate':
                    ax.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                elif 'dectime' in self.metric:
                    ax.ticklabel_format(axis='y', style='scientific', scilimits=(-3, -3))
            print(f'\n\tSaving.')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.chunk_data.columns:
            boxplot_path = self.boxplot_folder / 'tiling_quality' / f'boxplot_{self.metric}.png'
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'\r\tPlot {self.metric} - {self.tiling}', end='')

                ax1: plt.Axes = fig.add_subplot(2, 5, n)
                ax2: plt.Axes = fig.add_subplot(2, 5, n+5)

                self.projection = 'erp'
                positions = [0 - 0.2, 1 - 0.2, 2 - 0.2, 3 - 0.2, 4 - 0.2]
                serie_list = [self.chunk_data[self.metric].xs(key=(self.projection, self.tiling, self.quality), level=('projection', 'tiling', 'quality')).mean()
                              for self.quality in self.quality_list]
                ax1.boxplot(serie_list, sym='b.', positions=positions, widths=0.4,patch_artist=True, boxprops={"facecolor": "blue"})
                ax2.bar(positions, serie_list, color='blue', label=f'{self.tiling}')

                self.projection = 'cmp'
                positions = [0 + 0.2, 1 + 0.2, 2 + 0.2, 3 + 0.2, 4 + 0.2]
                serie_list = [self.chunk_data[self.metric].xs(key=(self.projection, self.tiling, self.quality), level=('projection', 'tiling', 'quality')).mean()
                              for self.quality in self.quality_list]
                ax1.boxplot(serie_list, sym='b.', positions=positions, widths=0.4, patch_artist=True, boxprops={"facecolor": "red"})
                ax2.bar(positions, serie_list, color='red', label=f'{self.tiling}')

                ax1.set_title(f'{self.tiling}')
                ax1.set_xlabel(f'Quality (QP)')
                ax1.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax1.set_xticks([0,1,2,3,4], list(self.quality_list))

                azul_patch = mpatches.Patch(color='blue', label='erp')
                red_patch = mpatches.Patch(color='red', label='cmp')
                ax1.legend(handles=[azul_patch, red_patch])
                if self.metric == 'bitrate':
                    ax1.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                elif 'dectime' in self.metric:
                    ax1.ticklabel_format(axis='y', style='scientific', scilimits=(-3, -3))
            print(f'\n\tSaving.')
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    @contextmanager
    def barplot_context(self, barplot_path) -> plt.figure():
        fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
        try:
            yield fig
            fig.suptitle(f'{self.metric}')
            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()
        finally:
            pass

    @contextmanager
    def barplot_axes(self, fig, nrows: int, ncols: int, index: int,
                     title=None, xlabel=None, ylabel=None,
                     xticks=None, legends_list=None) -> Generator[plt.Axes, Any, None]:
        ax: plt.Axes = fig.add_subplot(nrows, ncols, index)
        try:
            yield ax
        finally:
            pass
        if title is not None:
            ax.set_title(title)
        if legends_list is not None:
            ax.legend(legends_list, loc='top right', handlelength=0, handletextpad=0)

        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if xticks is not None:
            ax.set_xticks(*xticks)

        ax.set_ylim(bottom=0)
        if self.metric == 'ssim':
            ax.set_ylim(bottom=0.8, top=1.0)
        elif self.metric == 'dectime':
            ax.ticklabel_format(axis='y', style='scientific',
                                scilimits=(-3, -3))

        elif self.metric == 'bitrate':
            ax.ticklabel_format(axis='y', style='scientific',
                                scilimits=(6, 6))

    def make_barplot_quality_tiling(self):
        print(f'make_barplot_quality_tiling.')

        barplot_folder = self.barplot_folder / 'quality_tiling'

        for self.metric in self.metric_list:
            barplot_path = barplot_folder / f'boxplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            with self.barplot_context(barplot_path) as fig:
                ticks_pos = [i * (len(self.quality_list) + 1) + (len(self.tiling_list) / 2)
                             for i in range(len(self.tiling_list))]
                x_ticks = (ticks_pos, list(self.tiling_list))

                with self.barplot_axes(fig, 1, 1, 1,
                                       title='',
                                       xticks=x_ticks,
                                       xlabel=f'Tiling',
                                       ylabel=self.dataset_structure[self.metric]['quantity'],
                                       ) as ax:
                    for index, self.quality in enumerate(self.quality_list):
                        x = [i * (len(self.quality_list) + 1) + index for i in range(len(self.tiling_list))]
                        data = [self.get_chunk_data(('tiling', 'quality')).mean()
                                for self.tiling in self.tiling_list]
                        ax.bar(x, data, color=cor[index], label=f'qp{self.quality}')
                        ax.legend(loc='upper right')

    def make_barplot_tiling_quality(self):
        print(f'make_barplot_tiling_quality.')

        barplot_folder = self.barplot_folder / 'tiling_quality'

        for self.metric in self.metric_list:
            barplot_path = barplot_folder / f'barplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            with self.barplot_context(barplot_path) as fig:
                ticks_pos = [i * (len(self.tiling_list) + 1) + len(self.quality_list) / 2
                             for i in range(len(self.quality_list))]
                x_ticks = (ticks_pos, list(self.quality_list))
                with self.barplot_axes(fig, 1, 1, 1,
                                       title='',
                                       xticks=x_ticks,
                                       xlabel=f'Quality',
                                       ylabel=self.dataset_structure[self.metric]['quantity'],
                                       ) as ax:
                    for index, self.tiling in enumerate(self.tiling_list, 1):
                        x = [i * (len(self.tiling_list) + 1) + index for i in range(len(self.quality_list))]
                        data = [self.get_chunk_data(('tiling', 'quality')).mean() for self.quality in self.quality_list]
                        ax.bar(x, data, color=cor[index], label=f'{self.tiling}')
                        ax.legend(loc='upper right')

    def make_violinplot_quality_tiling(self):
        print(f'make_violinplot_quality_tiling_frame.')
        for self.metric in self.metric_list:
            violinplot_path = self.violinplot_folder / 'quality_tiling' / f'violinplot_{self.metric}.pdf'
            if violinplot_path.exists():
                print(f'\t{violinplot_path} exists.')
                continue
            violinplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'\r\tPlot qp{self.quality}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality'))
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
            fig.savefig(violinplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_tiling_quality(self):
        print(f'make_violinplot_tiling_quality.')
        for self.metric in self.metric_list:
            violinplot_path = self.violinplot_folder / 'tiling_quality' / f'violinplot_{self.metric}.pdf'
            if violinplot_path.exists():
                print(f'\t{violinplot_path} exists.')
                continue
            violinplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'\r\tPlot {self.tiling}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality'))
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
            fig.savefig(violinplot_path)
            fig.clf()
            plt.close()


if __name__ == '__main__':
    os.chdir('../')

    ChunkAnalysisTilingQuality(Config())
