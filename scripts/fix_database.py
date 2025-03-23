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
        self.join_metrics()
        # self.fix_head_movement()
        # self.fix_bitrate()
        # self.fix_dectime()
        # self.fix_seen_tiles()
        # self.fix_chunk_quality()

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
        columns = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']
        df = pd.DataFrame(bitrate_data, columns=columns + [metric])
        df = df.set_index(columns)
        serie = df[metric]
        serie.to_pickle(new_database)

    def fix_dectime(self):
        new_database = Path(f'dataset/dectime.pickle')
        if new_database.exists(): return

        metric = 'dectime'
        dectime_data = []

        for name in self.name_list:
            database = load_json(Path(f'dataset/time/time_{name}.json'))

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
        columns = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']
        df = pd.DataFrame(dectime_data, columns=columns + [metric])
        df = df.set_index(columns)
        serie = df[metric]
        serie.to_pickle(new_database)

    def fix_chunk_quality(self):
        self.metric = 'chunk_quality'
        index = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']

        for metric in ['ssim', 'mse', 's_mse', 'ws_mse']:
            filename = Path(f'dataset/{metric}.pickle')
            if filename.exists(): continue

            data_list = []

            for self.name in self.name_list:
                self.database = load_json(self.database_json)
                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            for self.quality in self.quality_list:
                                print(f'\r{metric} - {self.name}_{self.projection}_{self.tiling}_tile{self.tile}_qp{self.quality}', end='')
                                for self.chunk in self.chunk_list:
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk][metric.replace('_', '-')]
                                    register = (self.name, self.projection, self.tiling, int(self.tile), int(self.quality), int(self.chunk))
                                    data_list.append(register + (float(np.average(data)),))

            df = pd.DataFrame(data_list, columns=index + [metric])
            df = df.set_index(index)
            serie = df[f'{metric}']
            serie.to_pickle(filename)

    def fix_seen_tiles(self):
        new_database = Path(f'dataset/seen_tiles.pickle')
        if new_database.exists(): return

        def users_list(video_name):
            users_str = self.config.hmd_dataset[video_name + '_nas'].keys()
            sorted_users_int = sorted(map(int, users_str))
            sorted_users_str = list(map(str, sorted_users_int))
            return sorted_users_str

        projection = 'cmp'
        chunk_data = []
        for name in self.name_list:
            database = load_json(Path(f'dataset/get_tiles/get_tiles_{name}_fov110x90.json'))

            for tiling in self.tiling_list:
                for i, user in enumerate(users_list(name)):
                    print(f'\r{name} {projection} {tiling} user{i}', end='')

                    for chunk in self.chunk_list:
                        chunk_tile_list = database[name][projection][tiling][user]['chunks'][chunk]
                        chunk_tile_list = [int(i) for i in chunk_tile_list]
                        register = (name, projection, int(user), tiling,
                                    int(chunk), chunk_tile_list)
                        chunk_data.append(register)

        index = ['name', 'projection', 'user', 'tiling', 'chunk']
        df = pd.DataFrame(chunk_data, columns=index + ['seen_tiles'])
        df = df.set_index(index)
        serie = df['seen_tiles']
        serie.to_pickle(new_database)

    def fix_head_movement(self):
        new_database = Path(f'dataset/head_movement.pickle')
        # if new_database.exists(): return

        head_movement_by_frame = []
        for self.name in self.name_list:
            for self.user in self.users_list:
                print(f'\r{self.name} {self.projection} user{self.user}', end='')

                head_movement = self.config.hmd_dataset[self.name + '_nas'][self.user]
                for self.frame, (yaw, pitch, roll) in enumerate(head_movement):
                    register = (self.name, self.projection, int(self.user), self.frame,
                                yaw, pitch, roll)
                    head_movement_by_frame.append(register)

        index = ['name', 'projection', 'user', 'frame']
        df = pd.DataFrame(head_movement_by_frame, columns=index + ['yaw', 'pitch', 'roll'])
        df = df.set_index(index)
        df.to_pickle(new_database)

    def join_metrics(self):
        series_dict = {}
        for self.metric in ['bitrate', 'dectime', 'ssim', 'mse', 's-mse', 'ws-mse']:
            merged = pd.DataFrame([], columns=[self.metric])
            for self.name in self.name_list:
                serie = pd.read_pickle(f'dataset/pickles/{self.metric}_{self.metric}.pickle')
                flat_serie = serie.reset_index()
                merged = pd.merge(merged, flat_serie, on=[self.metric], how='outer')

            series_dict[f'{self.metric}'] = merged
        df = pd.DataFrame.from_dict(series_dict)
        df.to_pickle(f'dataset/metrics.pickle')
        # df = pd.read_pickle(f'dataset/metrics.pickle')
        # pd.options.display.max_columns=pd.options.display.max_colwidth = 999

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc: str):
        self.ui.update(desc)


if __name__ == '__main__':
    os.chdir('../')
    FixDatabase(Config())
