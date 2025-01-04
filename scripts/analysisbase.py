from pathlib import Path

import pandas as pd

from scripts.bucket import Bucket
from scripts.config import ConfigIf
from scripts.database import Database
from scripts.progressbar import ProgressBar


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
    bucket: Bucket
    stats_df: pd.DataFrame
    ui: ProgressBar
    database: Database
    bucket_keys_name: list[str]

    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config
        self.projection = 'cmp'
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
