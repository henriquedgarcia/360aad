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

from scripts.bucket import Bucket
from scripts.config import Config, ConfigIf
from scripts.database import database_factory, Database
from scripts.make_bucket import MakeBuket
from scripts.progressbar import ProgressBar
from scripts.utils import load_json, splitx, get_nested_value


class BitrateAnalysis:
    def __init__(self):
        """
        metric = 'bitrate' | 'time' | 'chunk_quality' | 'get_tiles
        """
        config = Config()
        print('GeneralAnalysis')
        BitrateChunkGeneralAnalysis(config)
        TimeChunkGeneralAnalysis(config)
        QualityChunkGeneralAnalysis(config)
        GetTilesChunkGeneralAnalysis(config)
        # print('ByQuality')
        # ByQuality(config, 'bitrate')
        # print('ByTiling')
        # ByTiling(config, 'bitrate')
        # print('ByTilingByQuality')
        # ByTilingByQuality(config, 'bitrate')


class DectimeAnalysis:
    def __init__(self):
        """
        metric = 'bitrate' | 'time' | 'chunk_quality'
        """
        config = Config()
        print('GeneralAnalysis')
        BitrateChunkGeneralAnalysis(config)
        # print('ByQuality')
        # ByQuality(config, 'time')
        # print('ByTiling')
        # ByTiling(config, 'time')
        # print('ByTilingByQuality')
        # ByTilingByQuality(config, 'time')


class AnalysisPaths(ConfigIf):
    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def graphs_workfolder(self):
        folder = Path(f'graphs/{self.metric}/{self.class_name}/')
        return folder

    @property
    def boxplot_folder(self):
        folder = self.graphs_workfolder / 'boxplot'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def histogram_folder(self):
        folder = self.graphs_workfolder / 'histogram'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def plot_name_quality_folder(self):
        folder = self.graphs_workfolder / 'plot_name_quality'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def plot_name_quality_tiling_folder(self):
        folder = self.graphs_workfolder / 'plot_name_quality_tiling'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def heatmap_folder(self):
        folder = self.graphs_workfolder / 'heatmap'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def stats_workfolder(self):
        folder = Path(f'stats/{self.metric}/{self.class_name}/')
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def bucket_workfolder(self):
        folder = Path(f'bucket/')
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def boxplot_path(self):
        return self.boxplot_folder / 'boxplot.png'

    @property
    def hist_path(self):
        return self.histogram_folder / 'histogram.png'

    @property
    def stats_csv(self):
        return self.stats_workfolder / 'stats.csv'

    bucket: Bucket
    bucket_keys_name: list[str]
    categories: list[str]

    @property
    def bucket_json(self):
        cat = '-'.join(self.categories)
        keys = '_'.join(self.bucket_keys_name)
        return self.bucket_workfolder / f'{self.metric}_[{cat}]_{keys}.json'

    @property
    def database_json(self):
        database_path = Path(f'dataset/{self.metric}')
        return database_path / f'{self.metric}_{self.config.name}.json'


class AnalysisBase(AnalysisPaths):
    bucket: Bucket
    stats_df: pd.DataFrame
    ui: ProgressBar
    database: Database
    bucket_keys_name: list[str]

    def __init__(self, config):
        self.config = config
        self.main()

    def main(self):
        ...

    def fill_bucket(self):
        """
        metric, categories, keys_orders
        """
        if self.bucket_json.exists():
            self.bucket = Bucket()
            self.bucket.load_bucket(self.bucket_json)
            return

        self.make_bucket()
        self.bucket.save_bucket(self.bucket_json)

    def get_bucket_keys(self):
        bucket_keys = [getattr(self, keys_name) for keys_name in self.bucket_keys_name]
        return [self.category] + bucket_keys

    def make_bucket(self) -> Bucket:
        ...


class BitrateChunkGeneralAnalysis(AnalysisBase):
    metric = 'bitrate'
    categories = ['dash_mpd', 'dash_init', 'dash_m4s']

    def main(self):
        self.bucket_keys_name = []

        self.fill_bucket()
        self.make_table()
        self.make_boxplot()
        self.make_hist()

    def make_time_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                for self.category in self.categories:
                                    self.bucket.set_bucket_value(self.database.get_value(),
                                                                 self.get_bucket_keys())
                        self.quality = self.chunk = None

    def make_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        self.category = 'dash_mpd'
                        self.bucket.set_bucket_value(self.database.get_value(),
                                                     self.get_bucket_keys())
                        for self.quality in self.quality_list:
                            self.category = 'dash_init'
                            self.bucket.set_bucket_value(self.database.get_value(),
                                                         self.get_bucket_keys())
                            for self.chunk in self.chunk_list:
                                self.category = 'dash_m4s'
                                self.bucket.set_bucket_value(self.database.get_value(),
                                                             self.get_bucket_keys())
                        self.quality = self.chunk = None

    def make_table(self):
        if self.stats_csv.exists(): return
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
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        if self.boxplot_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        ax1.boxplot(self.bucket['dash_mpd'], whis=(0, 100))
        ax1.title.set_text('Arquivo mpd')
        ax2.boxplot(self.bucket['dash_init'], whis=(0, 100))
        ax2.title.set_text('Arquivo init')
        ax3.boxplot(self.bucket['dash_m4s'], whis=(0, 100))
        ax3.title.set_text('Arquivo m4s')
        fig.tight_layout()
        fig: plt.Figure
        fig.savefig(self.boxplot_path)
        fig.clf()

    def make_hist(self):
        if self.hist_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        ax1.hist(self.bucket['dash_mpd'], bins=30)
        ax1.set_title('MPD')
        ax2.hist(self.bucket['dash_init'], bins=30)
        ax2.set_title('Init')
        ax3.hist(self.bucket['dash_m4s'], bins=30)
        ax3.set_title('chunk')
        fig.tight_layout()
        fig.savefig(self.hist_path)
        fig.clf()


class TimeChunkGeneralAnalysis(BitrateChunkGeneralAnalysis):
    metric = 'time'
    categories = ['dectime', 'dectime_avg', 'dectime_med', 'dectime_std']

    def make_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                for self.category in self.categories:
                                    self.bucket.set_bucket_value(self.database.get_value(),
                                                                 self.get_bucket_keys())
                        self.quality = self.chunk = self.category = None

    def make_table(self):
        if self.stats_csv.exists(): return

        stats_defaultdict = defaultdict(list)
        for cat in self.categories:
            stats_defaultdict['Nome'].append(cat)
            stats_defaultdict['n_arquivos'].append(len(self.bucket[cat]))
            stats_defaultdict['Média'].append(np.average(self.bucket[cat]))
            stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket[cat]))
            stats_defaultdict['Mínimo'].append(np.quantile(self.bucket[cat], 0))
            stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket[cat], 0.25))
            stats_defaultdict['Mediana'].append(np.quantile(self.bucket[cat], 0.5))
            stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket[cat], 0.75))
            stats_defaultdict['Máximo'].append(np.quantile(self.bucket[cat], 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        if self.boxplot_path.exists(): return
        fig = plt.Figure((10, 3))
        for n, cat in enumerate(self.categories):
            ax = fig.add_subplot(1, len(self.categories), n+1)
            ax.boxplot(self.bucket[cat], whis=(0, 100))
            ax.title.set_text(f'{cat}')
        fig.tight_layout()
        fig.savefig(self.boxplot_path)
        fig.clf()

    def make_hist(self):
        if self.hist_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        ax1.hist(self.bucket['dash_mpd'], bins=30)
        ax1.set_title('MPD')
        ax2.hist(self.bucket['dash_init'], bins=30)
        ax2.set_title('Init')
        ax3.hist(self.bucket['dash_m4s'], bins=30)
        ax3.set_title('chunk')
        fig.tight_layout()
        fig.savefig(self.hist_path)
        fig.clf()


class QualityChunkGeneralAnalysis(BitrateChunkGeneralAnalysis):
    metric = 'chunk_quality'
    categories = ['ssim', 'mse', 's-mse', 'ws-mse']

    def main(self):
        self.bucket_keys_name = []

        self.fill_bucket()
        self.make_table()
        self.make_boxplot()
        self.make_hist()

    def make_time_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                for self.category in self.categories:
                                    self.bucket.set_bucket_value(self.database.get_value(),
                                                                 self.get_bucket_keys())
                        self.quality = self.chunk = None

    def make_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        self.category = 'dash_mpd'
                        self.bucket.set_bucket_value(self.database.get_value(),
                                                     self.get_bucket_keys())
                        for self.quality in self.quality_list:
                            self.category = 'dash_init'
                            self.bucket.set_bucket_value(self.database.get_value(),
                                                         self.get_bucket_keys())
                            for self.chunk in self.chunk_list:
                                self.category = 'dash_m4s'
                                self.bucket.set_bucket_value(self.database.get_value(),
                                                             self.get_bucket_keys())
                        self.quality = self.chunk = None

    def make_table(self):
        if self.stats_csv.exists(): return
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
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        if self.boxplot_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        ax1.boxplot(self.bucket['dash_mpd'], whis=(0, 100))
        ax1.title.set_text('Arquivo mpd')
        ax2.boxplot(self.bucket['dash_init'], whis=(0, 100))
        ax2.title.set_text('Arquivo init')
        ax3.boxplot(self.bucket['dash_m4s'], whis=(0, 100))
        ax3.title.set_text('Arquivo m4s')
        fig.tight_layout()
        fig: plt.Figure
        fig.savefig(self.boxplot_path)
        fig.clf()

    def make_hist(self):
        if self.hist_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        ax1.hist(self.bucket['dash_mpd'], bins=30)
        ax1.set_title('MPD')
        ax2.hist(self.bucket['dash_init'], bins=30)
        ax2.set_title('Init')
        ax3.hist(self.bucket['dash_m4s'], bins=30)
        ax3.set_title('chunk')
        fig.tight_layout()
        fig.savefig(self.hist_path)
        fig.clf()


class GetTilesChunkGeneralAnalysis(BitrateChunkGeneralAnalysis):
    metric = 'get_tiles'
    categories = ['frame', 'chunk']

    def main(self):
        self.bucket_keys_name = []

        self.fill_bucket()
        self.make_table()
        self.make_boxplot()
        self.make_hist()

    def make_time_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                for self.category in self.categories:
                                    self.bucket.set_bucket_value(self.database.get_value(),
                                                                 self.get_bucket_keys())
                        self.quality = self.chunk = None

    def make_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
        for self.name in self.name_list:
            self.database.load(self.database_json)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        self.category = 'dash_mpd'
                        self.bucket.set_bucket_value(self.database.get_value(),
                                                     self.get_bucket_keys())
                        for self.quality in self.quality_list:
                            self.category = 'dash_init'
                            self.bucket.set_bucket_value(self.database.get_value(),
                                                         self.get_bucket_keys())
                            for self.chunk in self.chunk_list:
                                self.category = 'dash_m4s'
                                self.bucket.set_bucket_value(self.database.get_value(),
                                                             self.get_bucket_keys())
                        self.quality = self.chunk = None

    def make_table(self):
        if self.stats_csv.exists(): return
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
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        if self.boxplot_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        ax1.boxplot(self.bucket['dash_mpd'], whis=(0, 100))
        ax1.title.set_text('Arquivo mpd')
        ax2.boxplot(self.bucket['dash_init'], whis=(0, 100))
        ax2.title.set_text('Arquivo init')
        ax3.boxplot(self.bucket['dash_m4s'], whis=(0, 100))
        ax3.title.set_text('Arquivo m4s')
        fig.tight_layout()
        fig: plt.Figure
        fig.savefig(self.boxplot_path)
        fig.clf()

    def make_hist(self):
        if self.hist_path.exists(): return
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        ax1.hist(self.bucket['dash_mpd'], bins=30)
        ax1.set_title('MPD')
        ax2.hist(self.bucket['dash_init'], bins=30)
        ax2.set_title('Init')
        ax3.hist(self.bucket['dash_m4s'], bins=30)
        ax3.set_title('chunk')
        fig.tight_layout()
        fig.savefig(self.hist_path)
        fig.clf()


class ByQuality(BitrateChunkGeneralAnalysis):
    def fill_bucket(self):
        if self.bucket_json.exists():
            self.bucket = Bucket()
            self.bucket.load_bucket(self.bucket_json)
            return

        make_bucket = MakeBuket(self.config, self.metric,
                                bucket_keys_name=['quality'],
                                categories=['dash_m4s'])
        self.bucket = make_bucket.make_bucket()
        self.bucket.save_bucket(self.bucket_json)

    def make_table(self):
        if self.stats_csv.exists():
            return

        stats_defaultdict = defaultdict(list)
        for self.config.quality in self.config.quality_list:
            metrics = ['dash_init', 'dash_m4s']
            for metric in metrics:
                samples = self.bucket.get_bucket_values([metric, self.config.quality])
                stats_defaultdict['Nome'].append(metric)
                stats_defaultdict['Quality'].append(self.config.quality)
                stats_defaultdict['n_arquivos'].append(len(samples))
                stats_defaultdict['Média'].append(np.average(samples))
                stats_defaultdict['Desvio Padrão'].append(np.std(samples))
                stats_defaultdict['Mínimo'].append(np.quantile(samples, 0))
                stats_defaultdict['1º Quartil'].append(np.quantile(samples, 0.25))
                stats_defaultdict['Mediana'].append(np.quantile(samples, 0.5))
                stats_defaultdict['3º Quartil'].append(np.quantile(samples, 0.75))
                stats_defaultdict['Máximo'].append(np.quantile(samples, 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        if not self.boxplot_path.exists():
            fig, ax = plt.subplots(1, 2, figsize=(10, 5))
            fig: plt.Figure
            ax: list[plt.Axes]
            legends = []
            for n, quality in enumerate(self.config.quality_list):
                ax[0].boxplot(self.bucket['dash_init'][quality], whis=(0, 100), positions=[n])
                ax[1].boxplot(self.bucket['dash_m4s'][quality], whis=(0, 100), positions=[n])
            ax[0].title.set_text('Arquivo ini')
            ax[1].title.set_text('Arquivo m4s')
            ax[1].legend(legends)
            ax[0].set_xticklabels(self.config.quality_list)
            ax[1].set_xticklabels(self.config.quality_list)
            ax[0].ticklabel_format(axis='y', style='scientific')
            ax[1].ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
            ax[0].set_xlabel('QP')
            ax[1].set_xlabel('QP')
            ax[0].set_ylabel('Bitrate (bps)')
            ax[1].set_ylabel('Bitrate (Mbps)')
            fig.tight_layout()
            fig.savefig(self.boxplot_path)
            fig.clf()

        if not self.bitrate_boxplot_path1.exists():
            fig1 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, quality in enumerate(self.config.quality_list):
                ax1 = fig1.add_subplot(1, 6, n + 1)
                ax1.boxplot(self.bucket['dash_init'][quality], whis=(0, 100), positions=[n])
                ax1.title.set_text('Arquivo ini')
                ax1.set_xticklabels([quality])
                ax1.ticklabel_format(axis='y', style='scientific')
                ax1.set_xlabel('QP')
                ax1.set_ylabel('Bitrate (bps)')

            fig1.savefig(self.bitrate_boxplot_path1)

        if not self.bitrate_boxplot_path2.exists():
            fig2 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, quality in enumerate(self.config.quality_list):
                ax2 = fig2.add_subplot(1, 6, n + 1)
                ax2.boxplot(self.bucket['dash_m4s'][quality], whis=(0, 100), positions=[n])
                ax2.title.set_text('Arquivo m4s')
                ax2.set_xticklabels([quality])
                ax2.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax2.set_xlabel('QP')
                ax2.set_ylabel('Bitrate (bps)')

            fig2.savefig(self.bitrate_boxplot_path2)

    def make_hist(self):
        fig: plt.Figure
        ax: plt.Axes
        for n, self.config.quality in enumerate(self.config.quality_list):
            if self.hist_path.exists():
                continue
            fig = plt.figure(dpi=600, linewidth=0.5, tight_layout=True)
            ax = fig.add_subplot(1, 1, 1)

            ax.hist(self.bucket['dash_m4s'][self.config.quality], bins=30)

            ax.set_xlabel('Bitrate (Mbps)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'QP{self.config.quality}')
            ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            fig.suptitle('dash_m4s')
            fig.savefig(self.hist_path)
            fig.clf()

    @property
    def boxplot_path(self):
        return self.boxplot_folder / 'boxplot.pdf'

    @property
    def bitrate_boxplot_path1(self):
        return self.boxplot_folder / 'boxplot_ini.pdf'

    @property
    def bitrate_boxplot_path2(self):
        return self.boxplot_folder / 'boxplot_m4s.pdf'

    @property
    def hist_path(self):
        return self.histogram_folder / f'histogram_qp{self.config.quality}.pdf'


class ByTiling(BitrateChunkGeneralAnalysis):
    def fill_bucket(self):
        if self.bucket_json.exists():
            self.bucket = Bucket()
            self.bucket.load_bucket(self.bucket_json)
            return

        make_bucket = MakeBuket(self.config, self.metric,
                                bucket_keys_name=['tiling'],
                                categories=['dash_m4s'])

        self.bucket = make_bucket.make_bucket()
        self.bucket.save_bucket(self.bucket_json)

    def make_table(self):
        if self.stats_csv.exists():
            return
        stats_defaultdict = defaultdict(list)

        for self.config.tiling in self.config.tiling_list:
            metrics = ['dash_init', 'dash_m4s']
            for metric in metrics:
                samples = self.bucket.get_bucket_values([metric, self.config.tiling])
                stats_defaultdict['Nome'].append(metric)
                stats_defaultdict['Tiling'].append(self.config.tiling)
                stats_defaultdict['n_arquivos'].append(len(samples))
                stats_defaultdict['Média'].append(np.average(samples))
                stats_defaultdict['Desvio Padrão'].append(np.std(samples))
                stats_defaultdict['Mínimo'].append(np.quantile(samples, 0))
                stats_defaultdict['1º Quartil'].append(np.quantile(samples, 0.25))
                stats_defaultdict['Mediana'].append(np.quantile(samples, 0.5))
                stats_defaultdict['3º Quartil'].append(np.quantile(samples, 0.75))
                stats_defaultdict['Máximo'].append(np.quantile(samples, 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        if not self.boxplot_path.exists():
            fig, ax = plt.subplots(1, 2, figsize=(10, 5))
            fig: plt.Figure
            ax: list[plt.Axes]
            legends = []
            for n, tiling in enumerate(self.config.tiling_list):
                ax[0].boxplot(self.bucket['dash_init'][tiling], whis=(0, 100), positions=[n])
                ax[1].boxplot(self.bucket['dash_m4s'][tiling], whis=(0, 100), positions=[n])
            ax[0].title.set_text('Arquivo ini')
            ax[1].title.set_text('Arquivo m4s')
            ax[1].legend(legends)
            ax[0].set_xticklabels(self.config.tiling_list)
            ax[1].set_xticklabels(self.config.tiling_list)
            ax[0].ticklabel_format(axis='y', style='scientific')
            ax[1].ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
            ax[0].set_xlabel('QP')
            ax[1].set_xlabel('QP')
            ax[0].set_ylabel('Bitrate (bps)')
            ax[1].set_ylabel('Bitrate (Mbps)')
            fig.tight_layout()
            fig.savefig(self.boxplot_path)
            fig.clf()

        if not self.bitrate_boxplot_path1.exists():
            fig1 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, tiling in enumerate(self.config.tiling_list):
                ax1 = fig1.add_subplot(1, 6, n + 1)
                ax1.boxplot(self.bucket['dash_init'][tiling], whis=(0, 100), positions=[n])
                ax1.title.set_text('Arquivo ini')
                ax1.set_xticklabels([tiling])
                ax1.ticklabel_format(axis='y', style='scientific')
                ax1.set_xlabel('QP')
                ax1.set_ylabel('Bitrate (bps)')

            fig1.savefig(self.bitrate_boxplot_path1)

        if not self.bitrate_boxplot_path2.exists():
            fig2 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, tiling in enumerate(self.config.tiling_list):
                ax2 = fig2.add_subplot(1, 6, n + 1)
                ax2.boxplot(self.bucket['dash_m4s'][tiling], whis=(0, 100), positions=[n])
                ax2.title.set_text('Arquivo m4s')
                ax2.set_xticklabels([tiling])
                ax2.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax2.set_xlabel('QP')
                ax2.set_ylabel('Bitrate (bps)')

            fig2.savefig(self.bitrate_boxplot_path2)

    def make_hist(self):
        if self.hist_path.exists():
            return
        fig: plt.Figure
        ax: plt.Axes
        for n, tiling in enumerate(self.config.tiling_list):
            fig = plt.figure(dpi=600, linewidth=0.5, tight_layout=True)
            ax = fig.add_subplot(1, 1, 1)

            ax.hist(self.bucket['dash_m4s'][tiling], bins=30)

            ax.set_xlabel('Bitrate (Mbps)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'{tiling}')
            ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            fig.suptitle('dash_m4s')
            fig.savefig(self.hist_path)
            fig.clf()

    @property
    def boxplot_path(self):
        return self.boxplot_folder / 'boxplot.pdf'

    @property
    def bitrate_boxplot_path1(self):
        return self.boxplot_folder / 'boxplot_ini.pdf'

    @property
    def bitrate_boxplot_path2(self):
        return self.boxplot_folder / 'boxplot_m4s.pdf'

    @property
    def hist_path(self):
        return self.histogram_folder / f'histogram_qp{self.config.tiling}.pdf'


class ByTilingByQuality(BitrateChunkGeneralAnalysis):
    database: dict

    def make_plots(self):
        # self.make_boxplot()
        # self.make_hist()
        # self.make_plot()
        # self.make_plot2()
        # self.make_plot3()
        self.make_heatmap1()

    def fill_bucket(self):
        if self.bucket_json.exists():
            self.bucket = Bucket()
            self.bucket.load_bucket(self.bucket_json)
            return

        make_bucket = MakeBuket(self.config, self.metric,
                                bucket_keys_name=['tiling', 'quality'],
                                categories=['dash_m4s'])

        self.bucket = make_bucket.make_bucket()
        self.bucket.save_bucket(self.bucket_json)

    def make_table(self):
        if self.stats_csv.exists():
            return

        metrics = ['dash_init', 'dash_m4s']
        stats_defaultdict = defaultdict(list)

        for metric in metrics:
            for self.config.tiling in self.config.tiling_list:
                for self.config.quality in self.config.quality_list:
                    samples = self.bucket[metric][self.config.tiling][self.config.quality]
                    stats_defaultdict['Nome'].append(metric)
                    stats_defaultdict['Tiling'].append(self.config.tiling)
                    stats_defaultdict['Quality'].append(self.config.quality)
                    stats_defaultdict['n_arquivos'].append(len(samples))
                    stats_defaultdict['Média'].append(np.average(samples))
                    stats_defaultdict['Desvio Padrão'].append(np.std(samples))
                    stats_defaultdict['Mínimo'].append(np.quantile(samples, 0))
                    stats_defaultdict['1º Quartil'].append(np.quantile(samples, 0.25))
                    stats_defaultdict['Mediana'].append(np.quantile(samples, 0.5))
                    stats_defaultdict['3º Quartil'].append(np.quantile(samples, 0.75))
                    stats_defaultdict['Máximo'].append(np.quantile(samples, 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.stats_csv, index=False)

    def make_boxplot(self):
        for self.config.tiling in self.config.tiling_list:
            if not self.bitrate_boxplot_path1.exists():
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, self.config.quality in enumerate(self.config.quality_list):
                    ax.boxplot(self.bucket['dash_init'][self.config.tiling][self.config.quality], whis=(0, 100), positions=[n])

                ax.title.set_text('Arquivo ini')
                ax.set_xticklabels(self.config.quality_list)
                ax.ticklabel_format(axis='y', style='scientific')
                ax.set_xlabel('QP')
                ax.set_ylabel('Bitrate (bps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path1)
                fig.clf()

        for self.config.tiling in self.config.tiling_list:
            if not self.bitrate_boxplot_path2.exists():
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, self.config.quality in enumerate(self.config.quality_list):
                    ax.boxplot(self.bucket['dash_m4s'][self.config.tiling][self.config.quality], whis=(0, 100), positions=[n])
                ax.title.set_text('Arquivo m4s')
                ax.set_xticklabels(self.config.quality_list)
                ax.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax.set_xlabel('QP')
                ax.set_ylabel('Bitrate (Mbps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path2)
                fig.clf()

        for self.config.quality in self.config.quality_list:
            if not self.bitrate_boxplot_path3.exists():
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, self.config.tiling in enumerate(self.config.tiling_list):
                    ax.boxplot(self.bucket['dash_init'][self.config.tiling][self.config.quality], whis=(0, 100), positions=[n])
                ax.title.set_text('Arquivo ini')
                ax.set_xticklabels(self.config.tiling_list)
                ax.ticklabel_format(axis='y', style='scientific')
                ax.set_xlabel('Tiling')
                ax.set_ylabel('Bitrate (bps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path3)
                fig.clf()

        for self.config.quality in self.config.quality_list:
            if not self.bitrate_boxplot_path4.exists():
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, self.config.tiling in enumerate(self.config.tiling_list):
                    ax.boxplot(self.bucket['dash_m4s'][self.config.tiling][self.config.quality], whis=(0, 100), positions=[n])
                ax.title.set_text('Arquivo m4s')
                ax.set_xticklabels(self.config.tiling_list)
                ax.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax.set_xlabel('Tiling')
                ax.set_ylabel('Bitrate (Mbps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path4)
                fig.clf()

    def make_hist(self):
        for self.config.tiling in self.config.tiling_list:
            if not self.hist_path.exists():
                fig: plt.Figure
                ax: plt.Axes
                fig = plt.figure(figsize=(3, 10), dpi=600, linewidth=0.5, tight_layout=True)
                for n, self.config.quality in enumerate(self.config.quality_list):
                    ax = fig.add_subplot(1, len(self.config.quality_list), n + 1)

                    ax.hist(self.bucket['dash_m4s'][self.config.tiling][self.config.quality], bins=30)

                    ax.set_xlabel('Bitrate (Mbps)')
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'QP{self.config.quality}')
                    ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

                fig.suptitle('dash_m4s')
                fig.savefig(self.hist_path)
                fig.clf()

    def make_plot(self):
        for self.config.name in self.config.name_list:
            if self.plot_by_name_by_quality_path.exists(): continue
            self.database = load_json(self.database_json)
            fig = plt.figure(figsize=(8, 8), dpi=600, tight_layout=True)
            for self.config.projection in self.config.projection_list:
                for n, self.config.tiling in enumerate(self.config.tiling_list):
                    ax = fig.add_subplot(3, 2, n + 1)
                    for self.config.quality in self.config.quality_list:
                        chunk_list = []
                        for self.config.chunk in self.config.chunk_list:
                            value = 0
                            for self.config.tile in self.config.tile_list:
                                value += self.database[self.config.name][self.config.projection][self.config.tiling][self.config.tile][self.config.quality][self.config.chunk][
                                    'dash_m4s']
                            chunk_list.append(value)
                        ax.plot(chunk_list, label=f'QP {self.config.quality}')
                        ax.set_xlabel('Chunk')
                        ax.set_ylabel('Bitrate (bps)')
                        ax.set_title(f'{self.config.tiling}')
                    ax.legend()
            fig.savefig(self.plot_by_name_by_quality_path)
            fig.clf()

    def make_plot2(self):
        for self.config.name in self.config.name_list:
            if self.plot_by_name_by_tiling_path.exists(): continue
            self.database = load_json(self.database_json)
            fig = plt.figure(figsize=(8, 8), dpi=600, tight_layout=True)
            for self.config.projection in self.config.projection_list:
                for n, self.config.quality in enumerate(self.config.quality_list):
                    ax = fig.add_subplot(3, 2, n + 1)
                    for self.config.tiling in self.config.tiling_list:
                        chunk_list = []
                        for self.config.chunk in self.config.chunk_list:
                            value = 0
                            for self.config.tile in self.config.tile_list:
                                value += self.database[self.config.name][self.config.projection][self.config.tiling][self.config.tile][self.config.quality][self.config.chunk][
                                    'dash_m4s']
                            chunk_list.append(value)

                        ax.plot(chunk_list, label=f'QP {self.config.tiling}')
                        ax.set_xlabel('Chunk')
                        ax.set_ylabel('Bitrate (bps)')
                        ax.set_title(f'{self.config.quality}')
                    ax.legend()
            fig.savefig(self.plot_by_name_by_tiling_path)
            fig.clf()
            plt.close()

    def make_plot3(self):
        """
        Um arquivo por vídeo e qualidade.
        Cada axis é um tiling. Cada plot é um tile de chunk x bitrate
        :return:
        """
        self.config.projection = 'cmp'
        for self.config.name in self.config.name_list:
            self.database = load_json(self.database_json)
            for self.config.quality in self.config.quality_list:
                if self.plot_name_quality_tiling_path.exists(): continue
                fig = plt.figure(figsize=(8, 8), dpi=600, tight_layout=True)
                for n, self.config.tiling in enumerate(self.config.tiling_list):
                    ax = fig.add_subplot(3, 2, n + 1)
                    for self.config.tile in self.config.tile_list:
                        chunk_list = []
                        for self.config.chunk in self.config.chunk_list:
                            value = self.database[self.config.name][self.config.projection][self.config.tiling][self.config.tile][self.config.quality][self.config.chunk][
                                'dash_m4s']
                            chunk_list.append(value)

                        ax.plot(chunk_list)
                        ax.set_xlabel('Chunk')
                        ax.set_ylabel('Bitrate (bps)')
                        ax.set_title(f'QP {self.config.quality} - {self.config.tiling}')
                fig.savefig(self.plot_name_quality_tiling_path)
                fig.clf()
                plt.close()

    def make_heatmap1(self):
        """
        Um arquivo por vídeo
        um axis por qualidade.
        Cada axis é um tiling. Cada plot é um tile de chunk x bitrate
        :return:
        """
        self.config.projection = 'cmp'
        for self.config.name in self.config.name_list:
            self.database = load_json(self.database_json)
            for self.config.quality in self.config.quality_list:
                def main():
                    if self.bitrate_heatmap_path1.exists(): return
                    heatmap_dict = build_list_of_array()
                    fig = make_plot(heatmap_dict)
                    show(fig)

                def build_list_of_array():
                    """sorted by tiling"""
                    heatmap_lst = {}
                    for n, self.config.tiling in enumerate(self.config.tiling_list):
                        w, h = splitx(self.config.tiling)
                        heatmap_lst[self.config.tiling] = np.zeros((h * w,))

                        for self.config.tile in self.config.tile_list:
                            chunk_list = []  # values by chunk
                            for self.config.chunk in self.config.chunk_list:
                                keys = [self.config.name, self.config.projection, self.config.tiling,
                                        self.config.tile, self.config.quality, self.config.chunk,
                                        'dash_m4s']
                                value = get_nested_value(self.database, keys)
                                chunk_list.append(value)
                            heatmap_lst[self.config.tiling][int(self.config.tile)] = np.average(chunk_list)

                    # reshaping
                    heatmap_dict = {}
                    for self.config.tiling in self.config.tiling_list:
                        tiling_x, tiling_y = splitx(self.config.tiling)
                        reshaped = heatmap_lst[self.config.tiling].reshape(tiling_y, tiling_x)
                        heatmap_dict[self.config.tiling] = reshaped
                    return heatmap_dict

                def make_plot(heatmap_lst):
                    fig = plt.figure(figsize=(8, 8), dpi=600, tight_layout=True)
                    # maximo = np.max([np.max(array_of_tiles)
                    #                  for array_of_tiles in heatmap_lst.values()])
                    # minimum = np.min([np.min(array_of_tiles)
                    #                   for array_of_tiles in heatmap_lst.values()])
                    # norm = mpl.colors.Normalize(vmin=minimum, vmax=maximo)

                    for n, self.config.tiling in enumerate(self.config.tiling_list):
                        ax = fig.add_subplot(3, 2, n + 1)
                        im = ax.imshow(heatmap_lst[self.config.tiling], cmap='jet')
                        ax.set_title(f'QP {self.config.quality} - {self.config.tiling}')
                        fig.colorbar(im, ax=ax, orientation='vertical')

                        tiling_x, tiling_y = splitx(self.config.tiling)
                        ax.text(tiling_x / 2 - 0.5, tiling_y / 2 - 0.5,
                                f'{tiling_x * tiling_y * np.round(np.average(heatmap_lst[self.config.tiling]))} ',
                                ha="center", va="center", color="w")
                    return fig

                def show(fig):
                    # fig.show()
                    fig.savefig(self.bitrate_heatmap_path1.with_suffix('.png'))
                    plt.close()

                main()

    @property
    def bitrate_boxplot_path1(self):
        return self.boxplot_folder / f'boxplot_ini_{self.config.tiling}.pdf'

    @property
    def bitrate_boxplot_path2(self):
        return self.boxplot_folder / f'boxplot_m4s_{self.config.tiling}.pdf'

    @property
    def bitrate_boxplot_path3(self):
        return self.boxplot_folder / f'boxplot_ini_{self.config.quality}.pdf'

    @property
    def bitrate_boxplot_path4(self):
        return self.boxplot_folder / f'boxplot_m4s_{self.config.quality}.pdf'

    @property
    def hist_path(self):
        return self.histogram_folder / f'histogram_qp{self.config.tiling}.pdf'

    @property
    def plot_by_name_by_quality_path(self):
        return self.plot_name_quality_folder / f'plot_{self.config.name}_quality.pdf'

    @property
    def plot_by_name_by_tiling_path(self):
        return self.plot_name_quality_folder / f'plot_{self.config.name}_tiling.pdf'

    @property
    def plot_name_quality_tiling_path(self):
        return self.plot_name_quality_tiling_folder / f'plot_{self.config.name}_QP{self.config.quality}.pdf'

    @property
    def bitrate_heatmap_path1(self):
        return self.heatmap_folder / f'heatmap_{self.config.name}_QP{self.config.quality}.pdf'
