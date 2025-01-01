from pathlib import Path

from scripts.analysisbase import AnalysisBase
from scripts.database import database_factory
from scripts.progressbar import ProgressBar
from scripts.utils import AutoDict, set_nested_value, save_json


class FixDatabase(AnalysisBase):
    """
    Database[name][projection][tiling][tile][quality][chunk]
    """
    metric = 'bitrate'
    categories = {'bitrate': ['dash_mpd', 'dash_init', 'dash_m4s'],
                  'time': ['dectime', 'dectime_avg', 'dectime_med', 'dectime_std'],
                  'chunk_quality': ['ssim', 'mse', 's-mse', 'ws-mse']}
    databases: dict

    def main(self):
        self.fix()

    def fix(self):
        self.databases = {}
        for self.metric in self.categories:
            self.databases[self.metric] = database_factory(self.metric, self.config)

        print(f'Fix {self.metric}.')
        self.ui = ProgressBar(28 * 181, f'Fix {self.metric}.')
        for self.name in self.name_list:
            new_name = Path(f'dataset/bitrate_time_quality/dataset_{self.name}.json')
            if new_name.exists():
                continue

            dataset = AutoDict()
            for self.metric in self.categories:
                self.databases[self.metric].load(self.database_json)

            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.ui.update(f'{self}')
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                self.category = 'dash_m4s'
                                dash_m4s = self.databases['bitrate'].get_value()
                                self.category = 'dectime_avg'
                                dectime_avg = self.databases['time'].get_value()
                                self.category = 'ssim'
                                ssim = self.databases['chunk_quality'].get_value()
                                self.category = 'mse'
                                mse = self.databases['chunk_quality'].get_value()
                                self.category = 's-mse'
                                s_mse = self.databases['chunk_quality'].get_value()
                                self.category = 'ws-mse'
                                ws_mse = self.databases['chunk_quality'].get_value()
                                value = {'bitrate': dash_m4s,
                                         'dectime': dectime_avg,
                                         'ssim': ssim,
                                         'mse': mse,
                                         's_mse': s_mse,
                                         'ws_mse': ws_mse}

                                keys = [self.name, self.projection,
                                        self.tiling, self.tile, self.quality, self.chunk]
                                set_nested_value(dataset, keys, value)
                        self.quality = self.chunk = None

            save_json(dataset, new_name)
