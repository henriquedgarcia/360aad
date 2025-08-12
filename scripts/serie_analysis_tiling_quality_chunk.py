import json
import os
from abc import ABC
from collections import defaultdict
from typing import Union

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config


class Methods(AnalysisBase, ABC):
    def make_plot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.series_plot_folder / 'quality_tiling' / f'plot_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.tiling in self.tiling_list:
                    serie = self.get_chunk_data(('tiling', 'quality'))
                    ax.plot(serie, label=f'{self.tiling}')

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Chunk')
                ax.set_yscale('log')
                ax.legend(loc='upper right')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                # if self.metric == 'bitrate':
                #     ax.ticklabel_format(axis='y', style='scientific',
                #                         scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_plot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.series_plot_folder / 'tiling_quality' / f'plot_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.quality in self.quality_list:
                    serie = self.get_chunk_data(('tiling', 'quality'))
                    ax.plot(serie, label=f'qp{self.quality}')

                ax.set_title(f'{self.tiling}')
                ax.set_yscale('log')
                ax.set_xlabel(f'Chunk')
                ax.legend(loc='upper right')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                # if self.metric == 'bitrate':
                #     ax.ticklabel_format(axis='y', style='scientific',
                #                         scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.boxplot_folder / 'quality_tiling' / f'boxplot_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')

                serie_list = []
                for self.tiling in self.tiling_list:
                    serie_list.append(self.get_chunk_data(('tiling', 'quality')))

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                ax.boxplot(serie_list, tick_labels=list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'bitrate':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.metric_list:
            boxplot_path = self.boxplot_folder / 'tiling_quality' / f'boxplot_{self.metric}.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')

                serie_list = []
                for self.quality in self.quality_list:
                    serie_list.append(self.get_chunk_data(('tiling', 'quality')))

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'bitrate':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_quality_tiling(self):
        print(f'make_violinplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.violinplot_folder / 'quality_tiling' / f'violinplot_{self.metric}_quality.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')

                serie_list = []
                for self.tiling in self.tiling_list:
                    serie_list.append(self.get_chunk_data(('tiling', 'quality')))

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'bitrate':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            boxplot_path = self.violinplot_folder / 'tiling_quality' / f'violinplot_{self.metric}_quality.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')

                serie_list = []
                for self.quality in self.quality_list:
                    serie_list.append(self.get_chunk_data(('tiling', 'quality')))

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'bitrate':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()


class SerieAnalysisTilingQualityChunk(Methods):
    def __init__(self, config):
        print(f'{self.class_name} initializing...')
        self.config = config
        self.create_session_dataset()
        # self.setup()
        # self.make_stats()
        # self.make_corr()
        # self.plots()

    def create_session_dataset(self):
        # Carrega os dataset
        self.start_ui(total=8 * 2 * 5 * 5 * 30 * 60, desc='create_session_dataset')

        chunk_data_qp: Union[object, pd.DataFrame] = pd.read_hdf('dataset/chunk_data.hd5')

        viewport_quality_by: Union[object, pd.DataFrame] = pd.read_hdf('dataset/viewport_quality.hd5')
        viewport_quality_by = viewport_quality_by.groupby(level=('name', 'projection', 'tiling', 'quality', 'user', 'chunk')).mean()

        tiles_seen_by_chunk: Union[object, pd.DataFrame] = pd.read_hdf('dataset/tiles_seen.hd5')
        a = tiles_seen_by_chunk.apply(set)
        tiles_seen_by_chunk = a.groupby(level=('name', 'projection', 'tiling', 'user', 'chunk')).apply(lambda x: set().union(*x))

        session_data = []
        for name, projection, tiling, quality, user, chunk in viewport_quality_by.index:
            self.update_ui(f'{name=}, {projection=}, {tiling=}, {quality=}, {user=}, {chunk=}')

            viewport = viewport_quality_by.xs(key=(name, projection, tiling, quality, user, chunk),
                                                       level=('name', 'projection', 'tiling', 'quality', 'user', 'chunk'))
            tiles_seen = tiles_seen_by_chunk.xs(key=(name, projection, tiling, user, chunk),
                                                level=('name', 'projection', 'tiling', 'user', 'chunk'))
            chunk_data = chunk_data_qp.xs(key=(name, projection, tiling, quality, chunk),
                                          level=('name', 'projection', 'tiling', 'quality', 'chunk'))
            list_of_tiles = tiles_seen['tiles_seen'][0]

            bitrate = chunk_data.loc[list_of_tiles]['bitrate'].sum()
            dectime_serial = chunk_data.loc[list_of_tiles]['dectime'].sum()
            dectime_parallel = chunk_data.loc[list_of_tiles]['dectime'].max()
            ssim = chunk_data.loc[list_of_tiles]['ssim'].mean()
            mse = chunk_data.loc[list_of_tiles]['mse'].mean()
            s_mse = chunk_data.loc[list_of_tiles]['s-mse'].mean()
            ws_mse = chunk_data.loc[list_of_tiles]['ws-mse'].mean()
            viewport_mse = viewport['mse'][0]
            viewport_ssim = viewport['ssim'][0]
            n_tiles_seen = len(list_of_tiles)
            decodable_path = {}
            for tile in list_of_tiles:
                decodable_path.update({tile: f'decodable/{name}/{projection}/{tiling}/tile{tile}/qp{quality}/chunk{chunk}.mp4'})
            decodable_path = json.dumps(decodable_path)
            data = (name, projection, tiling, quality, user, chunk,
                    bitrate, dectime_serial, dectime_parallel, ssim,
                    mse, s_mse, ws_mse, viewport_mse, viewport_ssim,
                    n_tiles_seen, decodable_path)
            session_data.append(data)

        print(f'\nSaving')
        df = pd.DataFrame(session_data, columns=['name', 'projection', 'tiling', 'quality', 'user', 'chunk',
                                                 'bitrate', 'dectime_serial', 'dectime_parallel', 'ssim', 'mse', 's_mse',
                                                 'ws_mse', 'viewport_mse', 'viewport_ssim', 'n_tiles_seen'])
        df.set_index(['name', 'projection', 'tiling', 'quality', 'user', 'chunk'], inplace=True)
        df.to_hdf(f'dataset/user_session_qp.hd5', key='df')

    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        # self.load_database()
        self.database = self.database.groupby(['tiling', 'quality', 'chunk']).mean()

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    serie = self.get_chunk_data(('tiling', 'quality'))
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

    def plots(self):
        self.make_plot_quality_tiling()
        self.make_plot_tiling_quality()
        # self.make_boxplot_quality_tiling()
        # self.make_boxplot_tiling_quality()
        # self.make_violinplot_quality_tiling()
        # self.make_violinplot_tiling_quality()


if __name__ == '__main__':
    os.chdir('../')

    SerieAnalysisTilingQualityChunk(Config())
