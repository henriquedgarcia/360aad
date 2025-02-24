import os
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.analysisbase import AnalysisPaths
from scripts.utils.config import Config
from scripts.utils.progressbar import ProgressBar
from scripts.utils.utils import dict_to_tuples, AutoDict, save_pickle, load_json, load_pickle


class FixDatabase(AnalysisPaths):
    dataset_structure = {'bitrate': {'dash_mpd': ['name', 'projection', 'tiling', 'tile', 'category', 'value', None, None],
                                     'dash_init': ['name', 'projection', 'tiling', 'tile', 'quality', 'category', 'value', None],
                                     'dash_m4s': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'value']
                                     },
                         'time': {'dectime_avg': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'value'],
                                  'dectime_std': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'value'],
                                  },
                         'chunk_quality': {'ssim': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'frame', 'value'],
                                           'mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'frame', 'value'],
                                           's-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'frame', 'value'],
                                           'ws-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'category', 'frame', 'value'],
                                           }
                         }
    metrics = list(dataset_structure)
    databases: dict
    new_names = {'dash_mpd': 'dash_mpd',
                 'dash_init': 'dash_init',
                 'dash_m4s': 'bitrate',

                 'dectime_avg': 'dectime',
                 'dectime_std': 'dectime_std',

                 'ssim': 'ssim',
                 'mse': 'mse',
                 's-mse': 's-mse',
                 'ws-ms': 'ws-ms',
                 }
    categories = ''
    bucket_keys_name = ['']
    bucket = {}

    @property
    def database_json(self):
        database_path = Path(f'dataset/{self.metric}')
        return database_path / f'{self.metric}_{self.name}.json'

    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config
        self.split_cat()
        self.to_dataframe()

    def split_cat(self):
        self.metric = 'bitrate'
        if work := False:
            cat_db1 = AutoDict()
            cat_db2 = AutoDict()
            cat_db3 = AutoDict()
            total = (len(self.name_list) *
                     181 *
                     len(self.quality_list) *
                     len(self.chunk_list)
                     )
            self.start_ui(total, f'{self.metric}')
            for self.name in self.name_list:
                self.database = load_json(self.database_json)

                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            print(f'\r{self.name} {self.projection} {self.tiling}/{self.tile}', end='')
                            data = self.database[self.name][self.projection][self.tiling][self.tile]['dash_mpd']
                            cat_db1[self.name][self.projection][self.tiling][self.tile] = int(data)

                            for self.quality in self.quality_list:
                                data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality]['dash_init']
                                cat_db2[self.name][self.projection][self.tiling][self.tile][self.quality] = int(data)

                                for self.chunk in self.chunk_list:
                                    self.update_ui('')
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['dash_m4s']
                                    cat_db3[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = int(data)

            save_pickle(cat_db1, f'dataset/dash_mpd.pickle')
            save_pickle(cat_db2, f'dataset/dash_init.pickle')
            save_pickle(cat_db3, f'dataset/dash_m4s.pickle')

        self.metric = 'time'
        if work := False:
            cat_db1 = AutoDict()
            cat_db2 = AutoDict()

            for self.name in self.name_list:
                self.database = load_json(self.database_json)

                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            print(f'\r{self.name} {self.projection} {self.tiling}/{self.tile}', end='')
                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['dectime_avg']
                                    cat_db1[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = float(data)
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['dectime_std']
                                    cat_db2[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = float(data)

            save_pickle(cat_db1, f'dataset/dectime_avg.pickle')
            save_pickle(cat_db2, f'dataset/dectime_std.pickle')

        self.metric = 'chunk_quality'
        if work := False:
            cat_db1 = AutoDict()
            cat_db2 = AutoDict()
            cat_db3 = AutoDict()
            cat_db4 = AutoDict()

            total = (len(self.name_list) *
                     181 *
                     len(self.quality_list) *
                     len(self.chunk_list)
                     )
            self.start_ui(total, f'{self.metric}')
            for self.name in self.name_list:
                self.database = load_json(self.database_json)

                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    self.update_ui('')
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['ssim']
                                    cat_db1[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = float(np.average(data))
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['mse']
                                    cat_db2[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = float(np.average(data))
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['s-mse']
                                    cat_db3[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = float(np.average(data))
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['ws-mse']
                                    cat_db4[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk] = float(np.average(data))

            save_pickle(cat_db1, f'dataset/ssim.pickle')
            save_pickle(cat_db2, f'dataset/mse.pickle')
            save_pickle(cat_db3, f'dataset/s-mse.pickle')
            save_pickle(cat_db4, f'dataset/ws-mse.pickle')

    def to_hfs(self):
        global_dataset_path = Path(f'dataset/global_dataset.h5')

        for self.metric in self.metrics:
            self.categories = self.dataset_structure[self.metric]

            data_tuples = []

            for self.category in self.categories:
                # df_name = self.new_names[self.category]
                df_name = self.category
                try:
                    pd.read_hdf(global_dataset_path, key=df_name)
                    continue
                except (FileNotFoundError, KeyError):
                    pass

                if not data_tuples:
                    for self.name in self.name_list:
                        self.database = load_json(self.database_json)
                        data_tuples.extend(dict_to_tuples(self.database))

                labels = self.dataset_structure[self.metric][self.category]
                df = pd.DataFrame(data_tuples, columns=labels)
                filtered_df = df[df['category'] == self.category]
                del filtered_df['category']
                if None in filtered_df.columns: del filtered_df[None]
                new_index = [i for i in labels if i not in ['category', 'value', None]]
                new_df = filtered_df.set_index(new_index)

                print('Saving new database...')

                t = int if self.metric == 'bitrate' else float
                new_df['value'] = new_df['value'].astype(t)
                new_df.to_hdf(global_dataset_path, key=df_name, mode='a')

    def to_dataframe(self):
        """
        metric, categories, keys_orders
        """
        print(f'make_bucket')
        for self.metric in self.dataset_structure:
            print(f'make_{self.metric}_bucket')
            if self.bucket_pickle.exists():
                self.df = load_pickle(self.bucket_pickle)
                return

            filename = self.dataset_structure[self.metric]['path']
            self.database = load_pickle(filename)

            data_tuples = list(dict_to_tuples(self.database))
            labels = self.dataset_structure[self.metric]['keys'] + ['value']
            self.df = pd.DataFrame(data_tuples, columns=labels)

            new_index = [i for i in labels[:-1]]
            self.df.set_index(new_index, inplace=True)

            print('Saving new database...')
            t = int if self.metric == 'bitrate' else float
            self.df['value'] = self.df['value'].astype(t)
            save_pickle(self.df, self.bucket_pickle)

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc):
        self.ui.update(desc)


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    FixDatabase(config)
