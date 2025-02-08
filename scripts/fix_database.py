from pathlib import Path

import pandas as pd

from scripts.analysisbase import AnalysisBase
from scripts.bucket import Bucket


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

    metrics = {'bitrate': ['dash_m4s'],
               'time': ['dectime_avg'],
               'chunk_quality': ['ssim', 'mse', 's-mse', 'ws-mse']}
    dataset_structute = {'bitrate': {'dash_mpd': ['name', 'projection', 'tiling', 'tile'],
                                     'dash_init': ['name', 'projection', 'tiling', 'tile', 'quality'],
                                     'dash_m4s': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']},
                         'time': {'dectime': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                  'dectime_avg': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                  'dectime_med': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                  'dectime_std': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                  },
                         'chunk_quality': {'ssim': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                           'mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                           's-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                           'ws-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                                           }
                         }
    database_keys = {'dash_m4s': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     'dectime_avg': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     'ssim': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     'mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     's-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     'ws-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                     }

    databases: dict
    new_names = {'dash_m4s': 'bitrate',
                 'dectime_avg': 'dectime',
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

        new_name = Path(f'dataset/global_dataset.h5')

        if new_name.exists():
            return

        for self.metric in self.metrics:
            for self.category in self.metrics[self.metric]:
                df_name = self.new_names[self.category]
                try:
                    pd.read_hdf(new_name, key=df_name)
                    continue
                except (FileNotFoundError, KeyError):
                    pass

                index = pd.MultiIndex.from_tuples([], names=['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'])
                df = pd.DataFrame(columns=['value'], index=index)

                for self.name in self.name_list:
                    self.load_database()
                    total = (181
                             * len(self.quality_list)
                             # * len(self.chunk_list)
                             # * len(self.metrics[self.metric])
                             )
                    self.start_ui(total, f'\t{self.category}_{self.name}')

                    for self.projection in self.projection_list:
                        for self.tiling in self.tiling_list:
                            for self.tile in self.tile_list:
                                for self.quality in self.quality_list:
                                    self.update_ui(f'{self.tiling}/{self.tile}_qp{self.quality}')
                                    for self.chunk in self.chunk_list:
                                        value = self.get_dataset_value(self.category)

                                        df.loc[(self.name,
                                                self.projection,
                                                self.tiling,
                                                self.tile,
                                                self.quality,
                                                self.chunk,
                                                )] = value
                print('Saving new database...')
                mode = 'a' if new_name.exists() else 'w'
                df.to_hdf(new_name, key=df_name, mode=mode)
