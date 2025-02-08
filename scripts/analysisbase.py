import pickle
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

import pandas as pd

from scripts.bucket import Bucket
from scripts.config import ConfigIf
from scripts.progressbar import ProgressBar
from scripts.utils import load_json, get_nested_value, set_nested_value, get_bucket_value, set_bucket_value


class AnalysisPaths(ConfigIf):
    # constants
    categories: tuple
    bucket_keys_name: tuple
    database_keys: dict

    # database-dependent
    metric: str
    category: str

    # containers
    bucket: dict
    stats_defaultdict: defaultdict
    database: dict

    # misc
    stats_df: pd.DataFrame
    ui: ProgressBar

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def results_folder(self):
        folder = Path('results') / f'{self.class_name}'
        return folder

    @property
    def graphs_workfolder(self):
        folder = self.results_folder / f'graphs/'
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
        folder = self.results_folder / f'stats/'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def bucket_workfolder(self):
        folder = self.results_folder / f'bucket/'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def stats_csv(self):
        return self.stats_workfolder / f'{self.__class__.__name__}_stats.csv'

    @property
    def bucket_pickle(self):
        cat = '-'.join(self.categories)
        keys = '_'.join(self.bucket_keys_name)
        return self.bucket_workfolder / f'{self.metric}_[{cat}]_{keys}.pickle'

    @property
    def database_json(self):
        database_path = Path(f'dataset/{self.metric}')
        database_json_path = database_path / f'{self.metric}_{self.config.name}.json'
        if self.metric == 'get_tiles':
            database_json_path_stem = database_json_path.stem + '_fov110x90'
            database_json_path = database_json_path.with_stem(database_json_path_stem)
        return database_json_path


class AnalysisBase(AnalysisPaths, ABC):
    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config

        self.setup()
        self._make_bucket()
        self._make_stats()
        self.plots()

    def _make_bucket(self):
        try:
            self.load_bucket()
        except FileNotFoundError:
            self.make_bucket()
            self.save_bucket()

    def _make_stats(self):
        if not self.stats_csv.exists():
            self.make_stats()
            self.save_stats()

    def save_stats(self):
        self.stats_df: pd.DataFrame = pd.DataFrame(self.stats_defaultdict)
        self.stats_df.to_csv(self.stats_csv, index=False)

    @abstractmethod
    def setup(self):
        ...

    @abstractmethod
    def make_bucket(self) -> Bucket:
        ...

    @abstractmethod
    def make_stats(self):
        ...

    @abstractmethod
    def plots(self):
        ...

    def load_database(self):
        print(f'\n{self.__class__.__name__} loading database...')
        self.database = load_json(self.database_json)

    def get_dataset_value(self, category):
        database_keys = [getattr(self, key) for key in self.database_keys[category]] + [category]
        value = get_nested_value(self.database, database_keys)
        return value

    def load_bucket(self):
        with open(self.bucket_pickle, 'rb') as f:
            print(f'\t{self.__class__.__name__} loading bucket...')
            self.bucket = pickle.load(f)

        # self.bucket = pickle.loads(self.bucket_pickle.read_bytes())

    # noinspection PyTypeChecker
    def save_bucket(self):
        with open(self.bucket_pickle, 'wb') as f:
            pickle.dump(self.bucket, f)
        # self.bucket_pickle.write_bytes(pickle.dumps(self.bucket))

    def get_bucket_keys(self, cat):
        bucket_keys = [cat] + [getattr(self, key) for key in self.bucket_keys_name]
        return bucket_keys

    def get_bucket_value(self, bucket_keys: list):
        return get_bucket_value(self.bucket, bucket_keys)

    def set_bucket_value(self, value, bucket_keys: list):
        set_bucket_value(self.bucket, bucket_keys, value)

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc):
        self.ui.update(desc)

    def close_ui(self):
        del self.ui
