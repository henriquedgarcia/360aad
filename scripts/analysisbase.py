import pickle
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

import pandas as pd

from scripts.config import ConfigIf
from scripts.progressbar import ProgressBar
from scripts.utils import get_nested_value, get_bucket_value, set_bucket_value, load_pickle


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
    database: pd.DataFrame

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
    def series_plot_folder(self):
        folder = self.graphs_workfolder / f'series_plot/'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def boxplot_folder(self):
        folder = self.graphs_workfolder / 'boxplot'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def violinplot_folder(self):
        folder = self.graphs_workfolder / 'violinplot'
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def histogram_folder(self):
        folder = self.graphs_workfolder / 'histogram'
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
        return self.bucket_workfolder / f'bucket_{self.metric}.pickle'


class AnalysisBase(AnalysisPaths, ABC):
    dataset_structure = {
        'dash_mpd': {'path': f'dataset/df_dash_mpd.pickle',
                     'keys': ['name', 'projection', 'tiling', 'tile'],
                     'quantity': 'Bitrate (bps)'
                     },
        'dash_init': {'path': f'dataset/df_dash_init.pickle',
                      'keys': ['name', 'projection', 'tiling', 'tile', 'quality'],
                      'quantity': 'Bitrate (bps)'
                      },
        'dash_m4s': {'path': f'dataset/df_dash_m4s.pickle',
                     'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     'quantity': 'Bitrate (bps)'
                     },
        'dectime_avg': {'path': f'dataset/df_dectime_avg.pickle',
                        'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                        'quantity': 'Time (s)'
                        },
        'dectime_std': {'path': f'dataset/df_dectime_std.pickle',
                        'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                        'quantity': 'Time (s)'
                        },
        'ssim': {'path': f'dataset/df_ssim.pickle',
                 'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                 'quantity': ''
                 },
        'mse': {'path': f'dataset/df_mse.pickle',
                'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                'quantity': ''
                },
        's-mse': {'path': f'dataset/df_s-mse.pickle',
                  'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                  'quantity': ''
                  },
        'ws-mse': {'path': f'dataset/df_ws-mse.pickle',
                   'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                   'quantity': ''
                   },
        }

    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config
        self.setup()

        if not self.stats_csv.exists():
            self.make_stats()
            self.save_stats()

        self.plots()

    def save_stats(self):
        self.stats_df: pd.DataFrame = pd.DataFrame(self.stats_defaultdict)
        self.stats_df.to_csv(self.stats_csv, index=False)

    @abstractmethod
    def setup(self):
        ...

    def make_stats(self):
        ...

    @abstractmethod
    def plots(self):
        ...

    def load_database(self):
        print(f'\t{self.__class__.__name__} loading {self.metric} database...')
        filename = self.dataset_structure[self.metric]['path']
        self.database = load_pickle(filename)

    def get_database_value(self):
        keys_name = self.dataset_structure[self.metric]['keys']
        database_keys = [getattr(self, key) for key in keys_name]
        value = get_nested_value(self.database, database_keys)
        return value

    def load_bucket(self):
        with open(self.bucket_pickle, 'rb') as f:
            print(f'\t{self.__class__.__name__} loading bucket...')
            self.bucket = pickle.load(f)

        # self.bucket = pickle.loads(self.bucket_pickle.read_bytes())

    def save_bucket(self):
        with open(self.bucket_pickle, 'wb') as f:
            # noinspection PyTypeChecker
            pickle.dump(self.bucket, f)

    def get_bucket_keys(self, cat):
        bucket_keys = [cat] + [getattr(self, key) for key in self.bucket_keys_name]
        return bucket_keys

    def get_bucket_value(self, bucket_keys: list):
        return get_bucket_value(self.bucket, bucket_keys)

    def set_bucket_value(self, bucket_keys: list, value):
        set_bucket_value(self.bucket, bucket_keys, value)

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc):
        self.ui.update(desc)

    def close_ui(self):
        del self.ui
