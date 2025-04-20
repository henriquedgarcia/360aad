import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import load_pd_pickle

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


class SitiData:
    def __init__(self, filename, context: AnalysisBase):
        self.level = ['name', 'projection', 'tiling', 'tile', 'quality', 'frame']
        self.columns = ['si', 'ti']
        self.context = context
        self.data: pd.DataFrame = load_pd_pickle(Path(filename))

    def __getitem__(self, column) -> pd.Series:
        levels = self.level
        key = tuple(getattr(self.context, level) for level in levels)

        if key[-1] is None:
            levels = self.level[:-1]
            key = key[:-1]
        return self.data.xs(key=key, level=levels)[column]

    def group_by(self, level: list[str], operation) -> pd.DataFrame:
        grouped = self.data.groupby(level=level)
        return grouped.apply(operation)


def frame_to_chunk(frame_serie):
    filtered = []
    for i in range(60):
        idx = i * 30
        filtered.append(frame_serie[idx:idx + 30].mean())
    return filtered


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
        if self.stats_csv.exists(): return

        for self.group, video_list in self.video_list_by_group.items():
            for self.name in video_list:
                for self.tile in self.tile_list:
                    si = self.siti['si']
                    ti = self.siti['ti']

                    self.stats_defaultdict['Group'].append(self.group)
                    self.stats_defaultdict['Name'].append(self.name)
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

        self.save_stats()

    def plots(self):
        # self.plot1()
        # self.plot2()
        # self.boxplot1()
        # self.boxplot2()
        self.scatter_mean_x_std()

    def plot1(self):
        tile_map = {0: 'left', 1: 'front', 2: 'right', 3: 'down', 4: 'back', 5: 'top'}

        def plot_path():
            filename = self.graphs_workfolder / 'plot_tiles' / f'plot_{self.group}_{self.name}_by_frame.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        for self.group, video_list in self.video_list_by_group.items():
            for self.name in video_list:
                fig = plt.Figure(figsize=(8, 5), dpi=300, tight_layout=True)
                ax1 = fig.add_subplot(2, 1, 1)
                ax2 = fig.add_subplot(2, 1, 2)

                for self.tile in self.tile_list:
                    si = self.siti['si']
                    ti = self.siti['ti']

                    ax1.plot(si, label=f'{tile_map[self.tile]}')
                    ax2.plot(ti, label=f'{tile_map[self.tile]}')
                ax1.legend()
                ax1.set_title(f'SI')
                ax1.set_xlabel(f'Frame')
                ax2.legend()
                ax2.set_title(f'TI')
                ax2.set_xlabel(f'Frame')
                fig.suptitle(f'{self.name}')
                fig.savefig(plot_path())
                plt.close()

    def plot2(self):
        tile_map = {0: 'left', 1: 'front', 2: 'right', 3: 'down', 4: 'back', 5: 'top'}

        def plot_path():
            filename = self.graphs_workfolder / 'plot_tiles' / f'plot_{self.group}_{self.name}_by_chunk.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        for self.group, video_list in self.video_list_by_group.items():
            for self.name in video_list:
                fig = plt.Figure(figsize=(8, 5), dpi=300, tight_layout=True)
                ax1 = fig.add_subplot(2, 1, 1)
                ax2 = fig.add_subplot(2, 1, 2)

                for self.tile in self.tile_list:
                    si = self.siti['si']
                    ti = self.siti['ti']

                    ax1.plot(frame_to_chunk(si), label=f'{tile_map[self.tile]}')
                    ax2.plot(frame_to_chunk(ti), label=f'{tile_map[self.tile]}')
                ax1.legend()
                ax1.set_title(f'SI')
                ax1.set_xlabel(f'Chunk')
                ax2.legend()
                ax2.set_title(f'TI')
                ax2.set_xlabel(f'Chunk')
                fig.suptitle(f'{self.name}')
                fig.savefig(plot_path())
                plt.close()

    def boxplot1(self):
        def plot_path(m):
            filename = self.graphs_workfolder / 'boxplot1' / f'bar_{m}_mean.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        data = self.siti.group_by(['name', 'tile'], 'mean')
        ticks_position = list(range(1, len(self.name_list) + 1))

        for metric in ['si', 'ti']:
            sorted_names = data.groupby('name').mean()[metric].sort_values().reset_index()['name'].to_list()
            metric_list = [data.loc[(self.name,)][metric] for self.name in sorted_names]
            legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, sorted_names)]

            fig = plt.figure(figsize=(14, 6), dpi=300, layout="constrained")
            ax1 = fig.add_subplot(1, 1, 1)
            ax1.boxplot(metric_list, widths=0.8)
            ax1.set_title(metric.upper())
            ax1.set_xticklabels(ticks_position)

            legend = fig.legend(legends_list, loc='outside right center', handlelength=0, handletextpad=0)
            for handler in legend.legend_handles:
                handler.set_visible(False)

            fig.savefig(plot_path(metric))
            plt.close()

    def boxplot2(self):
        def plot_path(m):
            filename = self.graphs_workfolder / 'boxplot1' / f'bar_{m}_std.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        data = self.siti.group_by(['name', 'tile'], 'std')
        ticks_position = list(range(1, len(self.name_list) + 1))

        for metric in ['si', 'ti']:
            sorted_names = data.groupby('name').mean()[metric].sort_values().reset_index()['name'].to_list()
            metric_list = [data.loc[(self.name,)][metric] for self.name in sorted_names]
            legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, sorted_names)]

            fig = plt.figure(figsize=(14, 6), dpi=300, layout="constrained")
            ax1 = fig.add_subplot(1, 1, 1)
            ax1.boxplot(metric_list, widths=0.8)
            ax1.set_title(metric.upper())
            ax1.set_xticklabels(ticks_position)

            legend = fig.legend(legends_list, loc='outside right center', handlelength=0, handletextpad=0)
            for handler in legend.legend_handles:
                handler.set_visible(False)

            fig.savefig(plot_path(metric))
            plt.close()

    def scatter_mean_x_std(self):
        def plot_path():
            filename = self.graphs_workfolder / 'scatter_mean_x_std' / f'scatter_mean_x_std.png'
            filename.parent.mkdir(parents=True, exist_ok=True)
            return filename

        data:pd.DataFrame = self.siti.group_by(['name', 'tile'], 'mean')
        data_mean = data.groupby(['name']).mean()
        data_std = data.groupby(['name']).std()
        fig = plt.figure(figsize=(14, 7), dpi=300, layout="constrained")
        ax = fig.add_subplot(1, 1, 1)
        for idx, (mean, std) in enumerate(zip(data_mean['si'], data_std['si'])):
            ax.plot(mean, std, 'o', label=data_mean.reset_index()['name'].to_list()[idx])
            ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
        ax.set_title('SI')
        ax.set_xlabel('mean')
        ax.set_ylabel('std')
        plt.show()

        fig.savefig(plot_path())
        plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    AnalysisSiti(config)
