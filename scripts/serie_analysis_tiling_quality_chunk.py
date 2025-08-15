import json
import os
from abc import ABC
from collections import defaultdict
from pathlib import Path
from typing import Union

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.database import BitrateData, DectimeData, ChunkQualityData, ViewportQualityData, TilesSeenData, SessionData


class Methods(AnalysisBase, ABC):

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


# noinspection PyTypeChecker
class SerieAnalysisTilingQualityChunk(Methods):
    def __init__(self, config):
        print(f'{self.class_name} initializing...')
        self.config = config
        self.setup()
        self.plots()
        # self.make_stats()
        # self.make_corr()

    def create_session_dataset(self):
        # Carrega os dataset
        bitrate_data_df: Union[object, pd.DataFrame] = pd.read_hdf('dataset/bitrate_qp.hd5')
        dectime_data_df: Union[object, pd.DataFrame] = pd.read_hdf('dataset/dectime_qp.hd5')
        chunk_quality_data_df: Union[object, pd.DataFrame] = pd.read_hdf('dataset/chunk_quality_qp.hd5')
        viewport_quality_df: Union[object, pd.DataFrame] = pd.read_hdf('dataset/user_viewport_quality_qp.hd5')
        tiles_seen_df: Union[object, pd.DataFrame] = pd.read_hdf('dataset/tiles_seen_fov110x90.hd5')

        self.start_ui(total=8 * 2 * 5 * 5 * 30 * 60, desc='create_session_dataset')
        session_data = []
        for name, projection, tiling, quality, user, chunk in viewport_quality_df.index:
            self.update_ui(f'{name=}, {projection=}, {tiling=}, {quality=}, {user=}, {chunk=}')

            viewport = viewport_quality_df.xs(key=(name, projection, tiling, quality, user, chunk),
                                              level=('name', 'projection', 'tiling', 'quality', 'user', 'chunk'))
            tiles_seen = tiles_seen_df.xs(key=(name, projection, tiling, user, chunk),
                                          level=('name', 'projection', 'tiling', 'user', 'chunk'))
            bitrate = bitrate_data_df.xs(key=(name, projection, tiling, quality, chunk),
                                         level=('name', 'projection', 'tiling', 'quality', 'chunk'))
            dectime = dectime_data_df.xs(key=(name, projection, tiling, quality, chunk),
                                         level=('name', 'projection', 'tiling', 'quality', 'chunk'))
            chunk_quality = chunk_quality_data_df.xs(key=(name, projection, tiling, quality, chunk),
                                                     level=('name', 'projection', 'tiling', 'quality', 'chunk'))
            list_of_tiles = list(tiles_seen['tiles_seen'][0])

            bitrate = bitrate.loc[list_of_tiles]['bitrate'].sum()
            dectime_serial = dectime.loc[list_of_tiles]['dectime'].sum()
            dectime_parallel = dectime.loc[list_of_tiles]['dectime'].max()
            ssim = chunk_quality.loc[list_of_tiles]['ssim'].mean()
            mse = chunk_quality.loc[list_of_tiles]['mse'].mean()
            s_mse = chunk_quality.loc[list_of_tiles]['s-mse'].mean()
            ws_mse = chunk_quality.loc[list_of_tiles]['ws-mse'].mean()
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
                                                 'ws_mse', 'viewport_mse', 'viewport_ssim', 'n_tiles_seen', 'decodable_path'])
        df.set_index(['name', 'projection', 'tiling', 'quality', 'user', 'chunk'], inplace=True)
        df.to_hdf(f'dataset/user_session_qp.hd5', key='df')

    bitrate_data: BitrateData
    dectime_data: DectimeData
    chunk_quality_data: ChunkQualityData
    viewport_quality_data: ViewportQualityData
    tiles_seen_data: TilesSeenData

    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.bitrate_data = BitrateData(self)
        self.dectime_data = DectimeData(self)
        self.chunk_quality_data = ChunkQualityData(self)
        self.viewport_quality_data = ViewportQualityData(self)
        self.tiles_seen_data = TilesSeenData(self)

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
        self.make_session_data()

        # self.make_plot_tiling_quality()
        # self.make_boxplot_quality_tiling()
        # self.make_boxplot_tiling_quality()
        # self.make_violinplot_quality_tiling()
        # self.make_violinplot_tiling_quality()

    user_list: list
    session_data: SessionData
    tiles_seen: Union[list, tuple]

    def make_session_data(self):
        try:
            self.session_data = SessionData(self)
            return
        except FileNotFoundError:
            pass

        def make_session_by_user():
            for self.name in self.name_list:
                self.user_list = list(self.tiles_seen_data.xs(('name',)).index.unique('user'))
                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.quality in self.quality_list:
                            for self.user in self.user_list:
                                filename = Path(f'dataset/user_session/{self.name}/{self.projection}/{self.tiling}/{self.rate_control}{self.quality}//user{self.user}_qp.hd5')
                                if filename.exists():
                                    print(f'\t{filename} exists.')
                                    continue
                                filename.parent.mkdir(parents=True, exist_ok=True)
                                self.start_ui(60, 'make_session')

                                data = []
                                for self.chunk in self.chunk_list:
                                    self.update_ui(f'{self}')

                                    bitrate_data = self.bitrate_data.xs(['name', 'projection', 'tiling', 'quality', 'chunk', ])
                                    dectime_data = self.dectime_data.xs(['name', 'projection', 'tiling', 'quality', 'chunk', ])
                                    chunk_quality_data = self.chunk_quality_data.xs(['name', 'projection', 'tiling', 'quality', 'chunk'])
                                    viewport_quality_data = self.viewport_quality_data.xs(['name', 'projection', 'tiling', 'quality', 'name', 'chunk', 'user', ])
                                    self.tiles_seen = list(self.tiles_seen_data.xs(('name', 'projection', 'tiling', 'user', 'chunk')).iloc[0, 0])

                                    bitrate_data_sum = bitrate_data.loc[pd.IndexSlice[self.tiles_seen]].sum()['bitrate']
                                    dectime_data_sum = dectime_data.loc[pd.IndexSlice[self.tiles_seen]].sum()['dectime']
                                    dectime_data_max = dectime_data.loc[pd.IndexSlice[self.tiles_seen]].max()['dectime']
                                    chunk_quality_mean = chunk_quality_data.loc[pd.IndexSlice[self.tiles_seen]].mean()
                                    ssim_mean = chunk_quality_mean['ssim']
                                    mse_mean = chunk_quality_mean['mse']
                                    smse_mean = chunk_quality_mean['s-mse']
                                    wsmse_mean = chunk_quality_mean['ws-mse']
                                    viewport_ssim = viewport_quality_data['ssim'][0]
                                    viewport_mse = viewport_quality_data['mse'][0]
                                    ntiles = len(self.tiles_seen)
                                    decodable_path = {}
                                    for tile in self.tiles_seen:
                                        decodable_path.update({tile: f'decodable/{self.name}/{self.projection}/{self.tiling}/tile{self.tile}/qp{self.quality}/chunk{self.chunk}.mp4'})
                                    # decodable_path = json.dumps(decodable_path)

                                    data.append((self.name, self.projection, self.tiling, self.quality, self.user, self.chunk,
                                                 bitrate_data_sum, dectime_data_sum, dectime_data_max,
                                                 ssim_mean, mse_mean, smse_mean, wsmse_mean,
                                                 viewport_ssim, viewport_mse,
                                                 ntiles, decodable_path))
                                df = pd.DataFrame(data, columns=['user', 'projection', 'tiling', 'name', 'quality', 'chunk',
                                                                 'bitrate_sum', 'dectime_sum', 'dectime_max',
                                                                 'ssim_mean', 'mse_mean', 'smse_mean', 'wsmse_mean',
                                                                 'viewport_ssim', 'viewport_mse',
                                                                 'ntiles', 'decodable_path'])
                                col_index: Union[list, tuple] = ['user', 'projection', 'tiling', 'name', 'quality', 'chunk']
                                df.set_index(col_index, inplace=True)
                                df.to_hdf(filename, key='user_session_qp', complevel=9)

        def merge_session_by_user():
            filename = Path(f'dataset/user_session_qp.hd5')
            if filename.exists():
                print(f'user_session_qp exists.')
                return
            session_data = pd.DataFrame()
            self.start_ui(8 * 2 * 5 * 5 * 30, 'make_session')
            for self.name in self.name_list:
                self.user_list = list(self.tiles_seen_data.xs(('name',)).index.unique('user'))
                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.quality in self.quality_list:
                            for self.user in self.user_list:
                                self.update_ui(f'{self}')
                                filename = Path(f'dataset/user_session/{self.name}/{self.projection}/{self.tiling}/{self.rate_control}{self.quality}//user{self.user}_qp.hd5')
                                df = pd.read_hdf(filename)
                                session_data = pd.concat([session_data, df])
            session_data.to_hdf(f'dataset/user_session_qp.hd5', key='df', complevel=9)

        make_session_by_user()
        merge_session_by_user()
        self.session_data = SessionData(self)

    def make_plot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        self.session_data.data = self.session_data.group_by(['projection', 'tiling', 'quality', 'chunk'], 'mean')

        for self.quality in self.quality_list:
            boxplot_path = self.series_plot_folder / 'quality_tiling' / f'plot_{self.rate_control}{self.quality}.pdf'
            boxplot_path.parent.mkdir(parents=True, exist_ok=True)
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                return

            print(f'Plot qp{self.quality}')
            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.rate_control}{self.quality}')
            for idx_proj, self.projection in enumerate(self.projection_list):
                for self.tiling in self.tiling_list:
                    sessions = {'bitrate_sum': fig.add_subplot(2, 8, 1 + 8 * idx_proj),
                                'dectime_sum': fig.add_subplot(2, 8, 2 + 8 * idx_proj),
                                'dectime_max': fig.add_subplot(2, 8, 3 + 8 * idx_proj),
                                'ssim_mean': fig.add_subplot(2, 8, 4 + 8 * idx_proj),
                                'mse_mean': fig.add_subplot(2, 8, 5 + 8 * idx_proj),
                                'smse_mean': fig.add_subplot(2, 8, 6 + 8 * idx_proj),
                                'wsmse_mean': fig.add_subplot(2, 8, 7 + 8 * idx_proj),
                                'tiles_seen': fig.add_subplot(2, 8, 8 + 8 * idx_proj)}
                    for metric, ax in sessions.items():
                        pass

    # bitrate
    # ax: plt.Axes = fig.add_subplot(3, 2, n)
    #
    # serie = self.get_chunk_data(('tiling', 'quality'))
    # ax.plot(serie, label=f'{self.tiling}')
    #
    # ax.set_title(f'qp{self.quality}')
    # ax.set_xlabel(f'Chunk')
    # ax.set_yscale('log')
    # ax.legend(loc='upper right')
    # ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

    # if self.metric == 'bitrate':
    #     ax.ticklabel_format(axis='y', style='scientific',
    #                         scilimits=(6, 6))


# fig.savefig(boxplot_path)
# fig.clf()
# plt.close()


if __name__ == '__main__':
    os.chdir('../')

    SerieAnalysisTilingQualityChunk(Config())
