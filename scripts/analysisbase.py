from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Callable, Union

import matplotlib as mpl
import pandas as pd
from cycler import cycler
from matplotlib import pyplot as plt

from scripts.utils.config import ConfigIf
from scripts.utils.progressbar import ProgressBar
from scripts.utils.utils import load_pd_pickle, LazyProperty


class AnalysisProps(ConfigIf, ABC):
    # constants
    categories: tuple
    bucket_keys_name: tuple
    database_keys: dict

    # database-dependent
    metric: str
    category: str

    # containers
    stats_defaultdict: defaultdict
    database: Union[pd.DataFrame, pd.Series]

    # misc
    stats_df: pd.DataFrame
    ui: ProgressBar

    @property
    def class_name(self):
        return self.__class__.__name__


class AnalysisPaths(AnalysisProps):
    @property
    def siti_path(self):
        siti_pickle = self.dataset_structure['siti']['path']
        return siti_pickle

    @property
    def head_movement_path(self):
        head_movement_pickle = self.dataset_structure['head_movement']['path']
        return head_movement_pickle

    @LazyProperty
    def head_movement_db(self):
        return load_pd_pickle(self.head_movement_path)

    @property
    def users_by_name(self):
        users_by_name = {}
        for name in self.name_list:
            key = (name, self.projection)
            level = ['name', 'projection']
            coss_section = self.head_movement_db.xs(key=key, level=level)
            level_values = coss_section.index.get_level_values('user').unique()
            users = list(level_values)
            users_by_name[name] = users
        return users_by_name

    @LazyProperty
    def name_by_users(self):
        names_by_users = defaultdict(list)
        for name, users_list in self.users_by_name.items():
            for user in users_list:
                names_by_users[user].append(name)

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
        return self.stats_workfolder / f'{self.class_name}_{self.projection}_{self.rate_control}_stats.csv'

    @property
    def corr_csv(self):
        return self.stats_workfolder / f'{self.class_name}_corr.csv'


class AnalysisBase(AnalysisPaths, ABC):
    def __init__(self, config):
        print(f'{self.class_name} initializing...')
        # self.rc_config()
        self.config = config
        self.setup()

        self.make_stats()

        self.plots()

    @staticmethod
    def rc_config():
        rc_param = {"figure": {'figsize': (7.0, 1.2), 'dpi': 300, 'autolayout': True},
                    "axes": {'linewidth': 1, 'titlesize': 8, 'labelsize': 7,
                             'prop_cycle': cycler(color=[plt.get_cmap('tab20')(i) for i in range(20)])},
                    "xtick": {'labelsize': 6},
                    "ytick": {'labelsize': 6},
                    "legend": {'fontsize': 6},
                    "font": {'size': 6},
                    "patch": {'linewidth': 0.5, 'edgecolor': 'black', 'facecolor': '#3297c9'},
                    "lines": {'linewidth': 1, 'markersize': 2},
                    "errorbar": {'capsize': 4},
                    "boxplot": {'flierprops.marker': '+', 'flierprops.markersize': 1, 'flierprops.linewidth': 0.5,
                                'boxprops.linewidth': 0.0,
                                'capprops.linewidth': 1,
                                'medianprops.linewidth': 0.5,
                                'whiskerprops.linewidth': 0.5,
                                }
                    }

        for group in rc_param:
            mpl.rc(group, **rc_param[group])

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

    keys: list
    column: list

    def load_database(self, callback: Callable = None):
        filename = self.dataset_structure[self.metric]['path']
        self.database = load_pd_pickle(filename)
        self.keys = self.dataset_structure[self.metric]['keys']
        self.column = self.dataset_structure[self.metric]['columns'][0]

        if callback: callback(self)

    def get_chunk_data(self, level: tuple[str, ...]) -> pd.Series:
        key = tuple(getattr(self, lv) for lv in level)
        chunk_data: pd.Series = self.database.xs(key=key, level=level)[self.column]
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
