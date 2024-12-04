from dataclasses import dataclass


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
    name = projection = tiling = tile = quality = chunk = user = None

    def get_tile_list(self, tiling):
        return self.tiling_list[tiling]
