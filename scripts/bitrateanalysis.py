"""
# Bitrate Structure

`bitrate[name][projection][tiling][tile][quality][chunk]['dash_m4s']: int`

or

`bitrate[name][projection][tiling][tile][quality]['dash_init']: int`

or

`bitrate[name][projection][tiling][tile]['dash_mpd']: int`
"""
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.config import Config
from scripts.utils import Bucket, load_json, save_json, ProgressBar

# Config
config = Config()
database_path = Path('dataset/bitrate')


class BitrateAnalysis:
    def __init__(self):
        # GeneralAnalysis()
        ByQuality()


class GeneralAnalysis:
    bucket: Bucket
    stats_df: pd.DataFrame

    def __init__(self):
        self.fill_bucket()
        self.make_table()
        self.make_plots()

    ui: ProgressBar

    def fill_bucket(self):
        self.bucket = Bucket(config)

        if self.bitrate_bucket_json.exists():
            self.bucket.bucket = load_json(self.bitrate_bucket_json)
            return

        self.ui = ProgressBar(28 * 181 * 6, self.class_name)
        for config.name in config.name_list:
            video_dict = load_json(self.video_json)

            for config.projection in config.projection_list:
                for config.tiling in config.tiling_list:
                    for config.tile in config.get_tile_list(config.tiling):
                        self.bucket.set_bucket(video_dict, metric='dash_mpd')
                        for config.quality in config.quality_list:
                            self.bucket.set_bucket(video_dict, metric='dash_init')
                            self.ui.update(f'{self}')
                            for config.chunk in config.chunk_list:
                                self.bucket.set_bucket(video_dict, metric='dash_m4s')

        save_json(self.bucket.bucket, self.bitrate_bucket_json)

    def __str__(self):
        return f'{config.name} - {config.tiling} - tile{config.tile} - QP{config.quality}'

    def make_table(self):
        stats_defaultdict = defaultdict(list)

        stats_defaultdict['Nome'].append('MPD')
        stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_mpd']))
        stats_defaultdict['Média'].append(np.average(self.bucket['dash_mpd']))
        stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_mpd']))
        stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_mpd'], 0))
        stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_mpd'], 0.25))
        stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_mpd'], 0.5))
        stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_mpd'], 0.75))
        stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_mpd'], 1))

        stats_defaultdict['Nome'].append('Init')
        stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_init']))
        stats_defaultdict['Média'].append(np.average(self.bucket['dash_init']))
        stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_init']))
        stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_init'], 0))
        stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_init'], 0.25))
        stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_init'], 0.5))
        stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_init'], 0.75))
        stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_init'], 1))

        stats_defaultdict['Nome'].append('m4s')
        stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_m4s']))
        stats_defaultdict['Média'].append(np.average(self.bucket['dash_m4s']))
        stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_m4s']))
        stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_m4s'], 0))
        stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_m4s'], 0.25))
        stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_m4s'], 0.5))
        stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_m4s'], 0.75))
        stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_m4s'], 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.bitrate_stats_csv, index=False)

    def make_plots(self):
        self.make_boxplot()
        self.make_hist()

    def make_boxplot(self):
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        ax1.boxplot(self.bucket['dash_mpd'], whis=(0, 100))
        ax1.title.set_text('Arquivo mpd')
        ax2.boxplot(self.bucket['dash_init'], whis=(0, 100))
        ax2.title.set_text('Arquivo init')
        ax3.boxplot(self.bucket['dash_m4s'], whis=(0, 100))
        ax3.title.set_text('Arquivo m4s')
        fig.tight_layout()
        fig: plt.Figure
        fig.savefig(self.bitrate_boxplot)
        fig.show()

    def make_hist(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        ax1.hist(self.bucket['dash_mpd'], bins=30)
        ax1.set_title('MPD')
        ax2.hist(self.bucket['dash_init'], bins=30)
        ax2.set_title('Init')
        ax3.hist(self.bucket['dash_m4s'], bins=30)
        ax3.set_title('chunk')
        fig.tight_layout()
        fig.savefig(self.bitrate_hist)
        fig.show()

    @property
    def graphs_workfolder(self):
        folder = Path(f'graphs/bitrate/{self.class_name}/')
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def stats_workfolder(self):
        folder = Path(f'stats/bitrate/{self.class_name}/')
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def bucket_workfolder(self):
        return self.stats_workfolder

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def bitrate_boxplot(self):
        return self.graphs_workfolder / 'boxplot.png'

    @property
    def bitrate_hist(self):
        return self.graphs_workfolder / 'histogram.png'

    @property
    def bitrate_stats_csv(self):
        return self.stats_workfolder / 'stats.csv'

    @property
    def bitrate_bucket_json(self):
        return self.bucket_workfolder / 'bucket.json'

    @property
    def video_json(self):
        return database_path / f'bitrate_{config.name}.json'


class ByQuality(GeneralAnalysis):
    def fill_bucket(self):
        self.bucket = Bucket(config)

        if self.bitrate_bucket_json.exists():
            self.bucket.bucket = load_json(self.bitrate_bucket_json)
            return

        self.ui = ProgressBar(28 * 181 * 6, self.class_name)
        for config.name in config.name_list:
            video_dict = load_json(self.video_json)

            for config.projection in config.projection_list:
                for config.tiling in config.tiling_list:
                    for config.tile in config.get_tile_list(config.tiling):
                        for config.quality in config.quality_list:
                            self.bucket.set_bucket(video_dict, metric='dash_init', quality=config.quality)
                            self.ui.update(f'{self}')
                            for config.chunk in config.chunk_list:
                                self.bucket.set_bucket(video_dict, metric='dash_m4s', quality=config.quality)

        save_json(self.bucket.bucket, self.bitrate_bucket_json)

    def make_table(self):
        for config.quality in config.quality_list:
            stats_defaultdict = defaultdict(list)

            stats_defaultdict['Nome'].append('Init')
            stats_defaultdict['Quality'].append(config.quality)
            stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_init'][config.quality]))
            stats_defaultdict['Média'].append(np.average(self.bucket['dash_init'][config.quality]))
            stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_init'][config.quality]))
            stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_init'][config.quality], 0))
            stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_init'][config.quality], 0.25))
            stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_init'][config.quality], 0.5))
            stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_init'][config.quality], 0.75))
            stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_init'][config.quality], 1))

            stats_defaultdict['Nome'].append('m4s')
            stats_defaultdict['Quality'].append(config.quality)
            stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_m4s'][config.quality]))
            stats_defaultdict['Média'].append(np.average(self.bucket['dash_m4s'][config.quality]))
            stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_m4s'][config.quality]))
            stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0))
            stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0.25))
            stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0.5))
            stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0.75))
            stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 1))

            self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
            self.stats_df.to_csv(self.bitrate_stats_csv, index=False)

    def make_boxplot(self):
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        fig: plt.Figure
        ax: list[plt.Axes]
        legends = []
        for n, quality in enumerate(config.quality_list):
            ax[0].boxplot(self.bucket['dash_init'][quality], whis=(0, 100), positions=[n])
            ax[1].boxplot(self.bucket['dash_m4s'][quality], whis=(0, 100), positions=[n])
            legends.append(f'QP {quality}')
        ax[0].title.set_text('Arquivo ini')
        ax[1].title.set_text('Arquivo m4s')
        ax[1].legend(legends)
        ax[0].set_xticklabels(config.quality_list)
        ax[1].set_xticklabels(config.quality_list)
        ax[0].set_xlabel('QP')
        ax[1].set_xlabel('QP')
        ax[0].set_ylabel('Bitrate (bps)')
        ax[1].set_ylabel('Bitrate (bps)')
        fig.tight_layout()
        fig.savefig(self.bitrate_boxplot)

    def make_hist(self):
        fig, ax = plt.subplots(5, 1, figsize=(8, 8))
        for n, quality in enumerate(config.quality_list):
            ax[n].hist(self.bucket['dash_init'][quality], bins=30)
            ax[n].set_title('Init')
            ax[n].hist(self.bucket['dash_m4s'][quality], bins=30)
            ax[n].set_title('chunk')

        fig.tight_layout()

    @property
    def bitrate_boxplot(self):
        return self.graphs_workfolder / 'boxplot.png'

    @property
    def bitrate_hist(self):
        return self.graphs_workfolder / 'histogram.png'


# class ByTiling(GeneralAnalisys):
#     def fill_bucket(self):
#         self.bucket = Bucket(config)
#
#         if self.bitrate_bucket_json.exists():
#             self.bucket.bucket = load_json(self.bitrate_bucket_json)
#             return
#
#         for config.name in config.name_list:
#             video_dict = load_json(self.video_json)
#
#             for config.projection in config.projection_list:
#                 for config.tiling in config.tiling_list:
#                     for config.tile in config.get_tile_list(config.tiling):
#                         for config.quality in config.quality_list:
#                             self.bucket.set_bucket(video_dict, metric='dash_init', quality=config.quality)
#                             for config.chunk in config.chunk_list:
#                                 self.bucket.set_bucket(video_dict, metric='dash_m4s', quality=config.quality)
#
#         save_json(self.bucket.bucket, self.bitrate_bucket_json)
#
#     def make_table(self):
#         for config.quality in config.quality_list:
#             stats_defaultdict = defaultdict(list)
#
#             stats_defaultdict['Nome'].append('Init')
#             stats_defaultdict['Quality'].append(config.quality)
#             stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_init'][config.quality]))
#             stats_defaultdict['Média'].append(np.average(self.bucket['dash_init'][config.quality]))
#             stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_init'][config.quality]))
#             stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_init'][config.quality], 0))
#             stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_init'][config.quality], 0.25))
#             stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_init'][config.quality], 0.5))
#             stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_init'][config.quality], 0.75))
#             stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_init'][config.quality], 1))
#
#             stats_defaultdict['Nome'].append('m4s')
#             stats_defaultdict['Quality'].append(config.quality)
#             stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_m4s'][config.quality]))
#             stats_defaultdict['Média'].append(np.average(self.bucket['dash_m4s'][config.quality]))
#             stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_m4s'][config.quality]))
#             stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0))
#             stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0.25))
#             stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0.5))
#             stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 0.75))
#             stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_m4s'][config.quality], 1))
#
#             self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
#             self.stats_df.to_csv(self.bitrate_stats_csv, index=False)
#
#     def make_plots(self):
#         self.make_boxplot()
#         self.make_hist()
#
#     def make_boxplot(self):
#         fig, ax = plt.subplots(1, 2, figsize=(10, 5))
#         fig: plt.Figure
#         ax: list[plt.Axes]
#         legends = []
#         for n, quality in enumerate(config.quality_list):
#             ax[0].boxplot(self.bucket['dash_init'][quality], whis=(0, 100), positions=[n])
#             ax[1].boxplot(self.bucket['dash_m4s'][quality], whis=(0, 100), positions=[n])
#             legends.append(f'QP {quality}')
#         ax[0].title.set_text('Arquivo ini')
#         ax[1].title.set_text('Arquivo m4s')
#         ax[1].legend(legends)
#         ax[0].set_xticklabels(config.quality_list)
#         ax[1].set_xticklabels(config.quality_list)
#         ax[0].set_xlabel('QP')
#         ax[1].set_xlabel('QP')
#         ax[0].set_ylabel('Bitrate (bps)')
#         ax[1].set_ylabel('Bitrate (bps)')
#         fig.tight_layout()
#         fig.savefig(self.bitrate_boxplot)
#
#     def make_hist(self):
#         fig, ax = plt.subplots(5, 1, figsize=(8, 8))
#         for n, quality in enumerate(config.quality_list):
#             ax[n].hist(self.bucket['dash_init'], bins=30)
#             ax[n].set_title('Init')
#             ax[n].hist(self.bucket['dash_m4s'], bins=30)
#             ax[n].set_title('chunk')
#
#         fig.tight_layout()
#
#     @property
#     def class_name(self):
#         return self.__class__.__name__
#
#     @property
#     def bitrate_boxplot(self):
#         return f'stats/bitrate/{self.class_name}/boxplot.png'
#
#     @property
#     def bitrate_hist(self):
#         return f'stats/bitrate/{self.class_name}/histogram.png'
#
#     @property
#     def bitrate_stats_csv(self):
#         return Path(f'stats/bitrate/{self.class_name}/bitrate_stats.csv')
#
#     @property
#     def bitrate_bucket_json(self):
#         return Path(f'stats/bitrate/{self.class_name}/bitrate_bucket.json')
#
#     @property
#     def video_json(self):
#         return database_path / f'bitrate_{config.name}.json'
