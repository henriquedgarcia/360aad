import os
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Generator

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.database import (Data, DectimeData, BitrateData,
                                    ChunkQualitySSIMData, ChunkQualityMSEData,
                                    ChunkQualityWSMSEData, ChunkQualitySMSEData)

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


class ChunkAnalysisTilingQuality(AnalysisBase):
    metrics_datasets: dict[str, Data]
    metric_list: list = None

    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.metrics_datasets = {'dectime': DectimeData(self),
                                 'bitrate': BitrateData(self),
                                 'ssim': ChunkQualitySSIMData(self),
                                 'mse': ChunkQualityMSEData(self),
                                 's-mse': ChunkQualitySMSEData(self),
                                 'ws-mse': ChunkQualityWSMSEData(self)}
        self.metric_list = list(self.metrics_datasets.keys())

    def make_stats(self):
        print(f'make_stats.')
        if self.stats_csv.exists(): return
        for self.projection in self.projection_list:
            for self.metric in self.metric_list:
                for self.tiling in self.tiling_list:
                    for self.quality in self.quality_list:
                        chunk_data = self.get_chunk_data(level=('tiling', 'quality'))

                        self.stats_defaultdict['Projection'].append(self.projection)
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

        self.save_stats_csv()

    def get_chunk_data(self, level: tuple[str, ...]) -> pd.Series:
        dataset = self.metrics_datasets[self.metric]
        filtered = dataset.xs(level)
        series = filtered[dataset.columns[0]]
        return series

    def plots(self):
        self.make_boxplot_quality_tiling()
        self.make_boxplot_tiling_quality()
        self.make_violinplot_quality_tiling()
        self.make_violinplot_tiling_quality()
        self.make_barplot_quality_tiling()
        self.make_barplot_tiling_quality()

    def make_boxplot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.metric_list:
            boxplot_path = self.boxplot_folder / 'quality_tiling' / f'boxplot_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):

                print(f'\r\tPlot qp{self.quality}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality'))
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

    def make_boxplot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.metric_list:
            # Check files
            boxplot_path = self.boxplot_folder / 'tiling_quality' / f'boxplot_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'\r\tPlot {self.tiling}', end='')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality'))
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

    config = Config()
    ChunkAnalysisTilingQuality(config)
