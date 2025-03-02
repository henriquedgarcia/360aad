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
        self.split_cat()

    def split_cat(self):

        self.metric = 'chunk_quality'
        if work := True:
            index_quality = pd.MultiIndex.from_tuples([], names=["name", "projection", "tiling", "tile", "quality", "chunk"])
            df = pd.DataFrame(index=index_quality, columns=["ssim", "mse", "smse", "wsmse"])

            for self.name in self.name_list:
                self.database = load_json(self.database_json)

                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            print(f'\r{self.name} {self.projection} {self.tiling}/{self.tile}', end='')

                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    data_ssim = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['ssim']
                                    data_mse = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['mse']
                                    data_smse = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['s-mse']
                                    data_wsmse = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['ws-mse']

                                    df.loc[(self.name, self.projection, self.tiling, int(self.tile), int(self.quality), int(self.chunk))] = [
                                        float(np.average(data_ssim)),
                                        float(np.average(data_mse)),
                                        float(np.average(data_smse)),
                                        float(np.average(data_wsmse))
                                    ]
            df["ssim"].to_pickle(f'dataset/ssim.pickle')
            df["mse"].to_pickle(f'dataset/mse.pickle')
            df["smse"].to_pickle(f'dataset/s_mse.pickle')
            df["wsmse"].to_pickle(f'dataset/ws_mse.pickle')

        self.metric = 'get_tiles'
        if work := True:
            # chunk_data = []
            # for self.name in self.name_list:
            #     self.database = load_json(self.database_json.with_stem(self.database_json.stem + '_fov110x90'))
            #
            #     for self.tiling in self.tiling_list:
            #         for i, self.user in enumerate(self.users_list):
            #             print(f'\r{self.name} {self.projection} {self.tiling} user{i}', end='')
            #
            #             for self.chunk in self.chunk_list:
            #                 chunk_tile_list = self.database[self.name][self.projection][self.tiling][self.user]['chunks'][self.chunk]
            #                 chunk_tile_serie = pd.Series(chunk_tile_list).astype(int)
            #                 register = (self.name, self.projection, self.tiling, int(self.user),
            #                             int(self.chunk), chunk_tile_serie)
            #                 chunk_data.append(register)
            #
            # columns = ["name", "projection", "tiling", "chunk", "user", "value"]
            # df = pd.DataFrame(chunk_data, columns=columns).set_index(columns[:-1])
            # df["value"].to_pickle(f'dataset/get_tiles_chunk.pickle')

            frame_data = []
            for self.name in self.name_list:
                self.database = load_json(self.database_json.with_stem(self.database_json.stem + '_fov110x90'))

                for self.tiling in self.tiling_list:
                    for i, self.user in enumerate(self.users_list):
                        print(f'\r{self.name} {self.projection} {self.tiling} user{i}', end='')

                        for self.frame in range(1800):
                            frame_tile_list = self.database[self.name][self.projection][self.tiling][self.user]['frames'][self.frame]
                            frame_tile_serie = pd.Series(frame_tile_list).astype(int)
                            register = (self.name, self.projection, self.tiling, int(self.user),
                                        self.frame, frame_tile_serie)
                            frame_data.append(register)

            columns = ["user", "name", "projection", "tiling", "frame", "value"]
            index = ["user", "name", "projection", "tiling", "frame"]
            df = pd.DataFrame(frame_data, columns=columns).set_index(index)
            df["value"].to_pickle(f'dataset/get_tiles_frame.pickle')

        self.metric = 'bitrate'
        if work := False:
            bitrate_data = []

            for self.name in self.name_list:
                self.database = load_json(self.database_json)

                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            print(f'\r{self.name} {self.projection} {self.tiling}/{self.tile}', end='')

                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    data = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['dash_m4s']
                                    bitrate_data.append((self.name, self.projection, self.tiling, int(self.tile), int(self.quality), int(self.chunk), int(data)))

            columns = ["name", "projection", "tiling", "tile", "quality", "chunk", "value"]
            df = pd.DataFrame(bitrate_data, columns=columns).set_index(columns[:-1])
            df["value"].to_pickle(f'dataset/bitrate.pickle')

        self.metric = 'time'
        if work := False:
            chunk_data = []

            for self.name in self.name_list:
                self.database = load_json(self.database_json)

                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            print(f'\r{self.name} {self.projection} {self.tiling}/{self.tile}', end='')
                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    data_dectime = self.database[self.name][self.projection][self.tiling][self.tile][self.quality][self.chunk]['dectime_avg']
                                    data_dectime = float(data_dectime)
                                    register = (self.name, self.projection, self.tiling, int(self.tile),
                                                int(self.quality), int(self.chunk), float(data_dectime))
                                    chunk_data.append(register)
            columns = ["name", "projection", "tiling", "tile", "quality", "chunk", "value"]
            df = pd.DataFrame(chunk_data, columns=columns).set_index(columns[:-1])
            df["value"].to_pickle(f'dataset/dectime.pickle')

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc: str):
        self.ui.update(desc)


if __name__ == '__main__':
    os.chdir('../')
    FixDatabase(Config())
