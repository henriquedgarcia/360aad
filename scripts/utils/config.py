from dataclasses import dataclass
from math import prod
from typing import Union

from scripts.utils.utils import splitx


@dataclass
class Config:
    duration = 60
    fps = 30
    gop = 30

    rate_control = "qp"
    decoding_num = 5

    bins = 30
    metric_list = ["time", "rate", "ssim", "mse", "s-mse", "ws-mse"]
    error_metric = "rmse"
    distributions = ["burr12", "fatiguelife", "gamma", "beta", "invgauss",
                     "rayleigh", "lognorm", "genpareto", "pareto", "halfnorm",
                     "expon"]

    fov = "110x90"

    chunk_list = list(range(1, 61))
    quality_list = [16, 22, 28, 34, 40]
    tiling_list = ["1x1", "3x2", "6x4", "9x6", "12x8"]
    projection_list = {'cmp': '3240x2160',
                       'erp': '4320x2160'}

    name_list = {
        "cable_cam": {
            "offset": "0:15",
            "group": "HS"
        },
        "closet_tour": {
            "offset": "0:07",
            "group": "FS"
        },
        "drop_tower": {
            "offset": "1:11",
            "group": "VM"
        },
        "glass_elevator": {
            "offset": "0:14",
            "group": "VN"
        },
        "pac_man": {
            "offset": "0",
            "group": "MM"
        },
        "penthouse": {
            "offset": "0:04",
            "group": "RS"
        },
        "sunset": {
            "offset": "0:40",
            "group": "FN"
        },
        "wingsuit_dubai": {
            "offset": "0:00",
            "group": "MS"
        }
    }

    name_list_original = {
        "angel_falls": {
            "offset": "5:30",
            "group": "MN"
        },
        "blue_angels": {
            "offset": "1:00",
            "group": "MM"
        },
        "cable_cam": {
            "offset": "0:15",
            "group": "HS"
        },
        "chariot_race": {
            "offset": "0:00",
            "group": "HM"
        },
        "closet_tour": {
            "offset": "0:07",
            "group": "FS"
        },
        "drone_chases_car": {
            "offset": "2:11",
            "group": "MS"
        },
        "drone_footage": {
            "offset": "0:01",
            "group": "HN"
        },
        "drone_video": {
            "offset": "0:15",
            "group": "VM"
        },
        "drop_tower": {
            "offset": "1:11",
            "group": "VM"
        },
        "dubstep_dance": {
            "offset": "0:05",
            "group": "FM"
        },
        "elevator_lift": {
            "offset": "0:00",
            "group": "VN"
        },
        "glass_elevator": {
            "offset": "0:14",
            "group": "VN"
        },
        "montana": {
            "offset": "0:00",
            "group": "FN"
        },
        "motorsports_park": {
            "offset": "0:15",
            "group": "HS"
        },
        "nyc_drive": {
            "offset": "0:12",
            "group": "HM"
        },
        "pac_man": {
            "offset": "0",
            "group": "MM"
        },
        "penthouse": {
            "offset": "0:04",
            "group": "RS"
        },
        "petite_anse": {
            "offset": "0:45",
            "group": "HN"
        },
        "rhinos": {
            "offset": "0:18",
            "group": "FM"
        },
        "sunset": {
            "offset": "0:40",
            "group": "FN"
        },
        "three_peaks": {
            "offset": "0:00",
            "group": "MN"
        },
        "video_04": {
            "offset": "0",
            "group": "FS"
        },
        "video_19": {
            "offset": "0",
            "group": "RN"
        },
        "video_20": {
            "offset": "0",
            "group": "RN"
        },
        "video_22": {
            "offset": "0",
            "group": "RS"
        },
        "video_23": {
            "offset": "0",
            "group": "RM"
        },
        "video_24": {
            "offset": "0",
            "group": "RM"
        },
        "wingsuit_dubai": {
            "offset": "0:00",
            "group": "MS"
        }
    }

    name = projection = tiling = tile = quality = chunk = user = metric = group = frame = category = None

    dataset_structure = {
        'siti': {'path': f'dataset/siti_qp.pickle',
                 'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'frame'],
                 'key_types': [str, str, str, int, int, int],
                 'columns': ['si', 'ti'],
                 'columns_types': [float, float],
                 'quantity': ''
                 },
        'head_movement': {'path': f'dataset/head_movement.pickle',
                          'keys': ['name', 'projection', 'user', 'frame'],
                          'key_types': [str, str, int, int],
                          'columns': ['yaw', 'pitch', 'roll'],
                          'columns_types': [float, float, float],
                          'quantity': 'Rads'
                          },
        'seen_tiles': {'path': f'dataset/seen_tiles_cmp_fov110x90.pickle',
                       'keys': ['name', 'projection', 'tiling', 'user', 'chunk'],
                       'key_types': [str, str, str, int, int],
                       'columns': ['seen_tiles'],
                       'columns_types': [list[int]],
                       'quantity': 'Tiles Seen'
                       },

        'bitrate': {'path': f'dataset/bitrate_qp.pickle',
                    'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                    'key_types': [str, str, str, int, int, int],
                    'columns': ['bitrate'],
                    'columns_types': [int],
                    'quantity': 'Bitrate (bps)'
                    },
        'dectime': {'path': f'dataset/dectime_cmp_qp.pickle',
                    'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                    'key_types': [str, str, str, int, int, int],
                    'columns': ['dectime'],
                    'columns_types': [float],
                    'quantity': 'Time (s)'
                    },
        'ssim': {'path': f'dataset/chunk_quality_ssim_cmp_qp.pickle',
                 'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                 'key_types': [str, str, str, int, int, int],
                 'columns': ['ssim'],
                 'columns_types': [float],
                 'quantity': ''
                 },
        'mse': {'path': f'dataset/chunk_quality_mse_cmp_qp.pickle',
                'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                'key_types': [str, str, str, int, int, int],
                'columns': ['mse'],
                'columns_types': [float],
                'quantity': ''
                },
        's-mse': {'path': f'dataset/chunk_quality_s-mse_cmp_qp.pickle',
                  'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                  'key_types': [str, str, str, int, int, int],
                  'columns': ['s-mse'],
                  'columns_types': [float],
                  'quantity': ''
                  },
        'ws-mse': {'path': f'dataset/chunk_quality_ws-mse_cmp_qp.pickle',
                   'keys': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                   'key_types': [str, str, str, int, int, int],
                   'columns': ['ws-mse'],
                   'columns_types': [float],
                   'quantity': ''
                   },

    }

    @property
    def groups_list(self):
        groups_set = {self.name_list[name]["group"]
                      for name in self.name_list}
        return list(groups_set)


class Factors:
    config: Config

    @property
    def name(self):
        return self.config.name

    @name.setter
    def name(self, value):
        self.config.name = value

    @property
    def projection(self):
        return self.config.projection

    @projection.setter
    def projection(self, value):
        self.config.projection = value

    @property
    def quality(self) -> int:
        return self.config.quality

    @quality.setter
    def quality(self, value: int):
        self.config.quality = value

    @property
    def tiling(self) -> str:
        return self.config.tiling

    @tiling.setter
    def tiling(self, value: str):
        self.config.tiling = value

    @property
    def tile(self) -> int:
        return self.config.tile

    @tile.setter
    def tile(self, value: int):
        self.config.tile = value

    @property
    def chunk(self) -> 30:
        return self.config.chunk

    @chunk.setter
    def chunk(self, value: int):
        self.config.chunk = value

    @property
    def metric(self):
        return self.config.metric

    @metric.setter
    def metric(self, value):
        self.config.metric = value

    @property
    def user(self):
        return self.config.user

    @user.setter
    def user(self, value):
        self.config.user = value

    @property
    def frame(self):
        return self.config.frame

    @frame.setter
    def frame(self, value):
        self.config.frame = value


class Lists:
    config: Config

    @property
    def name_list(self) -> dict[str, Union[dict[str, str], dict[str, str], dict[str, str], dict[str, str], dict[str, str], dict[str, str], dict[str, str], dict[str, str]]]:
        return self.config.name_list

    @property
    def projection_list(self):
        return self.config.projection_list

    @property
    def quality_list(self):
        return self.config.quality_list

    _tiling_list = None

    @property
    def tiling_list(self):
        if self._tiling_list is None:
            self._tiling_list = self.config.tiling_list
        return self._tiling_list

    @tiling_list.setter
    def tiling_list(self, value):
        self._tiling_list = value

    @property
    def chunk_list(self):
        return self.config.chunk_list

    @property
    def groups_list(self):
        return self.config.groups_list

    @property
    def metric_list(self):
        return list(self.config.dataset_structure)


class ConfigIf(Factors, Lists):
    config = Config()
    _dataset_structure: dict = None

    @property
    def dataset_structure(self):
        if self._dataset_structure is None:
            self._dataset_structure = self.config.dataset_structure
        return self._dataset_structure

    @dataset_structure.setter
    def dataset_structure(self, value):
        self._dataset_structure = value

    @property
    def video_shape(self):
        return splitx(self.scale)[::-1]

    @property
    def scale(self):
        return self.config.projection[self.projection]

    @property
    def fov(self):
        return self.config.fov

    @property
    def n_tiles(self):
        return prod(splitx(self.tiling))

    @property
    def tile_list(self):
        return list(range(self.n_tiles))

    @property
    def n_frames(self):
        return 1800

    @property
    def fps(self):
        return self.config.fps

    @property
    def gop(self):
        return self.config.gop

    @property
    def rate_control(self):
        return self.config.rate_control

    @property
    def decoding_num(self):
        return self.config.decoding_num

    @property
    def group(self):
        if self.config.group is None and self.name is not None:
            self.config.group = self.name_list[self.name]["group"]
        return self.config.group

    @group.setter
    def group(self, value):
        self.config.group = value

    @property
    def video_list_by_group(self) -> dict:
        """

        :return: a dict like {group: video_list}
        """
        b = {group: [name for name in self.name_list
                     if self.config.name_list[name]['group'] == group]
             for group in self.groups_list}
        return b

    def __str__(self):
        factors_list = ['name', 'projection', 'tiling', 'tile', 'user', 'quality', 'chunk',
                        'frame', 'metric', 'group']

        txt = []
        for factor in factors_list:
            value = getattr(self, factor)
            if value is None:
                continue

            if factor in ['name', 'projection', 'tiling']:
                value = value
            elif factor == 'quality':
                value = f'{self.config.rate_control}{value}'
            elif factor == 'tile':
                value = f'tile{int(value):02d}'
            elif factor == 'chunk':
                value = f'chunk{int(value):02d}'
            elif factor == 'frame':
                value = f'frame{int(value):03d}'
            elif factor == 'user':
                value = f'user{int(value):02d}'
            elif factor == 'attempt':
                value = f'attempt{value}'
            else:
                continue
            txt.append(f'[{value}]')

        return ''.join(txt)
