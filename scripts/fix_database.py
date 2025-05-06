import os
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.analysisbase import AnalysisPaths
from scripts.utils.config import Config
from scripts.utils.progressbar import ProgressBar
from scripts.utils.utils import load_json, load_pd_pickle


class FixDatabase(AnalysisPaths):
    @property
    def database_json(self):
        database_path = Path(f'dataset/{self.metric}')
        return database_path / f'{self.metric}_{self.name}.json'

    def __init__(self, config: Config):
        print(f'{self.__class__.__name__} initializing...')
        self.config = config
        self.projection = 'cmp'

        self.fix()

    def fix(self):
        # self.fix_siti()

        # self.fix_head_movement()

        # self.fix_seen_tiles()

        # self.fix_viewport_quality()

        self.fix_bitrate()
        # self.fix_dectime()
        # self.fix_chunk_quality()
        # self.join_metrics()

    def fix_bitrate(self):
        metric = 'bitrate'
        new_database = self.dataset_structure[metric]['path']

        bitrate_data = []
        mpd_data = []

        for self.name in self.name_list:
            database = load_json(Path(f'dataset/{metric}/{metric}_{self.name}.json'))
            for self.tiling in self.tiling_list:
                for self.tile in self.tile_list:
                    database[self.name][self.projection][self.tiling][str(self.tile)]['dash_mpd']
                    mpd_data.append()
                    for self.quality in self.quality_list:
                        print(f'\r({metric}_{self.name}_{self.projection}_{self.tiling}_tile{self.tile}_qp{self.quality})', end='')
                        for self.chunk in self.chunk_list:
                            data = database[self.name][self.projection][self.tiling][str(self.tile)][str(self.quality)][str(self.chunk+1)]['dash_m4s']
                            bitrate_data.append((self.name, self.projection, self.tiling, self.tile, self.quality, self.chunk, int(data)))
        print('\nSaving')
        columns = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']
        df = pd.DataFrame(bitrate_data, columns=columns + [metric])
        df = df.set_index(columns)
        serie = df[metric]
        serie.to_pickle(new_database)

    def fix_siti(self):
        metric = 'siti'
        self.name = 'wingsuit_dubai'  # um erro fez todos os valores ficarem no último arquivo

        data_full: pd.DataFrame = load_pd_pickle(Path(f'dataset/{metric}/{metric}_{self.name}.pickle'))
        index_names = list(data_full.index.names) + ['frame']
        df_list = []
        for index, series in data_full.iterrows():
            index: tuple
            index_list = [index + (i,) for i in range(1800)]
            multi_index = pd.MultiIndex.from_tuples(index_list, names=index_names)
            df = pd.DataFrame({'si': series[0], 'ti': series[1]}, index=multi_index)
            df_list.append(df)
        df_final = pd.concat(df_list)
        df_final.sort_index(inplace=True)

        print('\nSaving')
        new_database = self.dataset_structure['siti']['path']
        df_final.to_pickle(new_database)

    def fix_head_movement(self):
        new_database = self.dataset_structure['head_movement']['path']

        head_movement_by_frame = []
        for self.name in self.name_list:
            for self.user in self.users_by_name:
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

    def fix_viewport_quality(self):
        pass


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

    def join_metrics(self):
        final_name = lambda: Path(f'dataset/metrics.pickle')
        metric_name = lambda: Path(f'dataset/pickles/0_grouped_{self.metric}.pickle')
        pickle_name = lambda: Path(f'dataset/pickles/{self.metric}_{self.name}.pickle')
        seen_tiles_name = lambda: Path(f'dataset/seen_tiles/seen_tiles_{self.name}_fov110x90.pickle')
        final_seen_tiles_name = lambda: Path(f'dataset/seen_tiles.pickle')

        def main():
            group_data_by_metric()
            group_data_total()
            group_seen_tiles()

        def group_data_by_metric():
            metric_list = ['bitrate', 'dectime', 'ssim', 'mse', 's-mse', 'ws-mse']
            p = ProgressBar(total=len(self.name_list) * len(metric_list), desc='join_metrics')

            for self.metric in metric_list:
                if metric_name().exists(): continue
                merged = None
                for self.name in self.name_list:
                    p.update(f'{self.metric} {self.name}')
                    serie = pd.read_pickle(pickle_name())
                    merged = (serie if merged is None
                              else pd.concat([merged, serie], axis=0))
                merged = merged.apply(np.mean)
                merged.to_pickle(metric_name())

        def group_data_total():
            if final_name().exists(): return
            series_dict = {}
            for self.metric in ['bitrate', 'dectime', 'ssim', 'mse', 's-mse', 'ws-mse']:
                serie = pd.read_pickle(metric_name())
                series_dict[f'{self.metric}'] = serie

            df = pd.DataFrame.from_dict(series_dict)
            df.to_pickle(final_name())
            # df = pd.read_pickle(f'dataset/metrics.pickle')
            # pd.options.display.max_columns=pd.options.display.max_colwidth = 999

        def group_seen_tiles():
            p = ProgressBar(total=len(self.name_list), desc='join_metrics')
            merged = None
            if seen_tiles_name().exists(): return
            for self.name in self.name_list:
                p.update(f'{self.name}')
                serie = pd.read_pickle(seen_tiles_name())
                merged = (serie if merged is None
                          else pd.concat([merged, serie], axis=0))
            merged.to_pickle(final_seen_tiles_name())

        main()

    def start_ui(self, total, desc):
        self.ui = ProgressBar(total=total, desc=desc)

    def update_ui(self, desc: str):
        self.ui.update(desc)

    @property
    def dataset_structure(self):
        return self.config.dataset_structure


if __name__ == '__main__':
    os.chdir('../')
    FixDatabase(Config())
