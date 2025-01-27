from pathlib import Path

import pandas as pd

from scripts.bucket import Bucket
from scripts.config import ConfigIf
from scripts.database import Database
from scripts.progressbar import ProgressBar
from scripts.utils import save_json, load_json


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
        database_json_path = database_path / f'{self.metric}_{self.config.name}.json'
        if self.metric == 'get_tiles':
            database_json_path_stem = database_json_path.stem + '_fov110x90'
            database_json_path = database_json_path.with_stem(database_json_path_stem)
        return database_json_path


class AnalysisBase(AnalysisPaths):
    metric: str
    categories: tuple
    bucket_keys_name: tuple

    stats_df: pd.DataFrame
    ui: ProgressBar
    database: Database

    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config
        self.projection = 'cmp'
        self.bucket = Bucket()

        self.setup()
        self.main()
        self.end()

    def setup(self):
        ...

    def main(self):
        self.fill_bucket()
        self.make_stats()
        self.plots()

    def fill_bucket(self):
        """
        metric, categories, keys_orders
        """

        try:
            self.load_bucket()
        except FileNotFoundError:
            self.make_bucket()
            self.save_bucket()

    def make_stats(self):
        ...

    def plots(self):
        ...

    def end(self):
        ...

    def make_bucket(self) -> Bucket:
        ...

    def load_bucket(self):
        self.bucket.bucket = load_json(self.bucket_json)

    def save_bucket(self):
        save_json(self.bucket.bucket, self.bucket_json)

    def get_bucket_keys(self):
        bucket_keys = [getattr(self, keys_name) for keys_name in self.bucket_keys_name]
        return [self.category] + bucket_keys

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc):
        self.ui.update(desc)
