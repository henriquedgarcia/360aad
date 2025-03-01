from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

import pandas as pd

from scripts.utils.config import ConfigIf
from scripts.utils.progressbar import ProgressBar
from scripts.utils.utils import load_pickle


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
    def barplot_folder(self):
        folder = self.graphs_workfolder / 'barplot'
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
    def corr_csv(self):
        return self.stats_workfolder / f'{self.__class__.__name__}_corr.csv'

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
        'get_tiles': {'path': f'dataset/df_ws-mse.pickle',
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
        self.database = self.get_database(self.metric)

    def get_database(self, metric):
        filename = self.dataset_structure[metric]['path']
        database = load_pickle(filename)
        level_of_chunk = 5
        index_int = database.index.levels[level_of_chunk].astype(int)
        database.index = database.index.set_levels(index_int, level=level_of_chunk)
        return database

    def get_chunk_data(self, levels: tuple[str, ...]) -> pd.Series:
        key = tuple(getattr(self, level) for level in levels)
        chunk_data: pd.Series = self.database.xs(key=key, level=levels)['value']
        return chunk_data

    def get_chunk_serie(self, keys):
        labels = tuple(getattr(self, a) for a in keys)
        chunk_data = self.database.loc[labels]['value']
        return chunk_data

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc):
        self.ui.update(desc)

    def close_ui(self):
        del self.ui

    filename: Path

    def check_filename(self):
        if self.filename.exists():
            print(f'\t{self.filename} exists.')
            return True
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        return False
