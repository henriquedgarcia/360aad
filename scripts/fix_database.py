import os
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.analysisbase import AnalysisPaths
from scripts.utils.config import Config
from scripts.utils.progressbar import ProgressBar
from scripts.utils.utils import load_json


class FixDatabase(AnalysisPaths):
    dataset_structure = {
        'get_tiles': {'get_tiles_chunk': ['name', 'projection', 'tiling', 'tile', 'category', 'value', None, None],
                      'get_tiles_frame': ['name', 'projection', 'tiling', 'tile', 'category', 'value', None, None],
                      },
        'bitrate': {'dash_mpd': ['name', 'projection', 'tiling', 'tile', 'category', 'value', None, None],
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

    @property
    def database_json(self):
        database_path = Path(f'dataset/{self.metric}')
        return database_path / f'{self.metric}_{self.name}.json'

    def __init__(self, config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config
        self.projection = 'cmp'
        self.fix()

    def fix(self):
        # self.fix_bitrate()
        # self.fix_dectime()
        # self.fix_seen_tiles()
        self.fix_chunk_quality()
        # self.join_metrics()

    def fix_bitrate(self):
        new_database = Path(f'dataset/bitrate.pickle')
        if new_database.exists():
            return

        metric = 'bitrate'
        bitrate_data = []

        for name in self.name_list:
            database = load_json(Path(f'dataset/{metric}/{metric}_{name}.json'))

            for projection in self.projection_list:
                for tiling in self.tiling_list:
                    for tile in self.tiling_list[tiling]:
                        for quality in self.quality_list:
                            print(f'\r({metric}_{name}_{projection}_{tiling}_tile{tile}_qp{quality})', end='')
                            for chunk in self.chunk_list:
                                data = database[name][projection][tiling][tile][quality][chunk]['dash_m4s']
                                bitrate_data.append((name, projection, tiling, int(tile), int(quality), int(chunk), int(data)))
        print('\nSaving')
        columns = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'value']
        df = pd.DataFrame(bitrate_data, columns=columns).set_index(columns[:-1])
        df['value'].to_pickle(new_database)

    def fix_dectime(self):
        new_database = Path(f'dataset/dectime.pickle')
        if new_database.exists():
            return

        metric = 'time'
        dectime_data = []

        for name in self.name_list:
            database = load_json(Path(f'dataset/{metric}/{metric}_{name}.json'))

            for projection in self.projection_list:
                for tiling in self.tiling_list:
                    for tile in self.tiling_list[tiling]:
                        for quality in self.quality_list:
                            print(f'\r({metric}_{name}_{projection}_{tiling}_tile{tile}_qp{quality})', end='')
                            for chunk in self.chunk_list:
                                data_dectime = database[name][projection][tiling][tile][quality][chunk]['dectime_avg']
                                data_dectime = float(data_dectime)
                                register = (name, projection, tiling, int(tile),
                                            int(quality), int(chunk), float(data_dectime))
                                dectime_data.append(register)
        print('\nSaving')
        columns = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'value']
        df = pd.DataFrame(dectime_data, columns=columns).set_index(columns[:-1])
        df['value'].to_pickle(f'dataset/dectime.pickle')

    def fix_seen_tiles(self):
        new_database = Path(f'dataset/seen_tiles.pickle')
        if new_database.exists():
            return

        def users_list(video_name):
            users_str = self.config.hmd_dataset[video_name + '_nas'].keys()
            sorted_users_int = sorted(map(int, users_str))
            sorted_users_str = list(map(str, sorted_users_int))
            return sorted_users_str

        metric = 'get_tiles'
        projection = 'cmp'
        chunk_data = []
        for name in self.name_list:
            database = load_json(Path(f'dataset/{metric}/{metric}_{name}_fov110x90.json'))

            for tiling in self.tiling_list:
                for i, user in enumerate(users_list(name)):
                    print(f'\r{name} {projection} {tiling} user{i}', end='')

                    for chunk in self.chunk_list:
                        chunk_tile_list = database[name][projection][tiling][user]['chunks'][chunk]
                        chunk_tile_list = [int(i) for i in chunk_tile_list]
                        register = (name, projection, int(user), tiling,
                                    int(chunk), chunk_tile_list)
                        chunk_data.append(register)

        columns = ['name', 'projection', 'user', 'tiling', 'chunk', 'seen_tiles']
        df = pd.DataFrame(chunk_data, columns=columns).set_index(columns[:-1])
        df.to_pickle(new_database)

    def fix_chunk_quality(self):
        self.metric = 'chunk_quality'
        data_list = []
        index = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']

        for metric in ['ssim', 'mse', 's_mse', 'ws_mse']:
            filename = Path(f'dataset/{metric}.pickle')
            if filename.exists(): continue

            for self.name in self.name_list:
                self.database = load_json(self.database_json)
                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            print(f'\r{metric} {self.name} {self.projection} {self.tiling}/{self.tile}', end='')
                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk][metric.replace('_', '-')]
                                    register = (self.name, self.projection, self.tiling, int(self.tile), int(self.quality), int(self.chunk))
                                    data_list.append(register + (float(np.average(data)),))
            pd.DataFrame(data_list, columns=index + [metric]).set_index(index)[f'{metric}'].to_pickle(filename)

    def join_metrics(self):
        series_dict = {}
        for self.metric in ['bitrate', 'dectime', 'ssim', 'mse', 's_mse', 'ws_mse']:
            serie = pd.read_pickle(f'dataset/{self.metric}.pickle')
            series_dict[f'{self.metric}'] = serie
        df = pd.DataFrame.from_dict(series_dict)
        df.to_pickle(f'dataset/metrics.pickle')
        # df = pd.read_pickle(f'dataset/metrics.pickle')

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc: str):
        self.ui.update(desc)


if __name__ == '__main__':
    os.chdir('../')
    FixDatabase(Config())
