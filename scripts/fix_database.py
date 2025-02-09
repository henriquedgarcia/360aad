from pathlib import Path

import pandas as pd

from scripts.analysisbase import AnalysisBase
from scripts.bucket import Bucket
from scripts.utils import dict_to_tuples


class FixDatabase(AnalysisBase):
    """
    Database[name][projection][tiling][tile][quality][chunk]
    """

    def setup(self):
        pass

    def make_bucket(self) -> Bucket:
        pass

    def make_stats(self):
        pass

    def plots(self):
        pass


    dataset_structute = {'bitrate': {'dash_mpd': ['name', 'projection', 'tiling', 'tile', 'category', 'value', None, None],
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
    metrics = list(dataset_structute)
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


    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config

        global_dataset_path = Path(f'dataset/global_dataset.h5')

        for self.metric in self.metrics:
            self.categories = self.dataset_structute[self.metric]

            data_tuples=[]
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
                        self.load_database()
                        data_tuples.extend(dict_to_tuples(self.database))

                labels = self.dataset_structute[self.metric][self.category]
                df = pd.DataFrame(data_tuples, columns=labels)
                filtered_df = df[df['category'] == self.category]
                del filtered_df['category']
                if None in filtered_df.columns: del filtered_df[None]
                new_index = [i for i in labels if i not in ['category', 'value', None]]
                new_df = filtered_df.set_index(new_index)

                print('Saving new database...')

                t = int if self.metric=='bitrate' else float
                new_df['value'] = new_df['value'].astype(t)
                new_df.to_hdf(global_dataset_path, key=df_name, mode='a')
