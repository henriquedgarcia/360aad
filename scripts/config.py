from dataclasses import dataclass
from math import prod

from scripts.utils import load_json, splitx


@dataclass
class Config:
    dataset_file = "dataset/nasrabadi.json"

    duration = 60,
    fps = 30,
    gop = 30,
    scale = "3240x2160"

    rate_control = "qp",
    decoding_num = 5,

    bins = 30,
    metric_list = ["time", "rate", "ssim", "mse", "s-mse", "ws-mse"],
    error_metric = "rmse",
    distributions = ["burr12", "fatiguelife", "gamma", "beta", "invgauss",
                     "rayleigh", "lognorm", "genpareto", "pareto", "halfnorm",
                     "expon"],

    fov = "110x90",

    chunk_list = list(map(str, range(1, 61)))
    quality_list = ["22", "28", "34", "40", "46", "50"]
    tiling_list = {"1x1": list(map(str, range(1))),
                   "3x2": list(map(str, range(6))),
                   "6x4": list(map(str, range(24))),
                   "9x6": list(map(str, range(54))),
                   "12x8": list(map(str, range(96)))}
    projection_list = ['cmp']
    name_list = {
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

    def get_tile_list(self, tiling):
        return self.tiling_list[tiling]

    @property
    def tile_list(self):
        return self.tiling_list[self.tiling]

    _hmd_dataset = None

    @property
    def hmd_dataset(self):
        if self._hmd_dataset is None:
            self._hmd_dataset = load_json(self.dataset_file)
        return self._hmd_dataset

    @property
    def users_list(self):
        users_str = self.hmd_dataset[self.name + '_nas'].keys()
        sorted_users_int = sorted(map(int, users_str))
        sorted_users_str = list(map(str, sorted_users_int))
        return sorted_users_str

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
    def quality(self):
        return self.config.quality

    @quality.setter
    def quality(self, value):
        self.config.quality = value

    @property
    def tiling(self) -> str:
        return self.config.tiling

    @tiling.setter
    def tiling(self, value: str):
        self.config.tiling = value

    @property
    def tile(self) -> str:
        return self.config.tile

    @tile.setter
    def tile(self, value: str):
        self.config.tile = value

    @property
    def chunk(self):
        return self.config.chunk

    @chunk.setter
    def chunk(self, value):
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
    def group(self):
        return self.config.group

    @group.setter
    def group(self, value):
        self.config.group = value

    @property
    def frame(self):
        return self.config.frame

    @frame.setter
    def frame(self, value):
        self.config.frame = value


class Lists:
    config: Config

    @property
    def name_list(self):
        return self.config.name_list

    @property
    def projection_list(self):
        return self.config.projection_list

    @property
    def quality_list(self):
        return self.config.quality_list

    @property
    def tiling_list(self):
        return self.config.tiling_list

    @property
    def tile_list(self):
        return self.config.tile_list

    @property
    def chunk_list(self):
        return self.config.chunk_list

    @property
    def users_list(self):
        return self.config.users_list

    @property
    def groups_list(self):
        return self.config.groups_list


class ConfigIf(Factors, Lists):
    config = Config()

    @property
    def video_shape(self):
        return splitx(self.scale)[::-1]

    @property
    def scale(self):
        return self.config.scale

    @property
    def fov(self):
        return self.config.fov

    @property
    def n_tiles(self):
        return prod(splitx(self.tiling))

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
    def dataset_name(self):
        return self.config.dataset_file

    @property
    def video_list_by_group(self):
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
