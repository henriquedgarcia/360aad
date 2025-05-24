from abc import ABC
from pathlib import Path
from typing import Union

import pandas as pd

from scripts.utils.config import ConfigIf


class Data(ABC):
    level: list
    config: ConfigIf
    data: pd.Dataframe

    def __init__(self, filename: Union[str, Path], config: ConfigIf):
        self.config = config
        self.filename = filename
        self.data: pd.DataFrame = pd.read_pickle(filename)

        self.level = list(self.data.index.names)
        self.columns = list(self.data.columns)

    def __getitem__(self, column) -> Union[int, float]:
        """
        if str, search colum, full index
        if tuple, search index using cross-section
        :param column:
        :return:
        """
        levels = self.level
        key = tuple(getattr(self.config, level) for level in levels)
        return self.data.xs(key=key, level=levels)[column]

    def xs(self, levels):
        key = tuple(getattr(self.config, level) for level in levels)
        return self.data.xs(key=key, level=levels)

    def group_by(self, level: list[str], operation) -> pd.DataFrame:
        grouped = self.data.groupby(level=level)
        return grouped.apply(operation)


class SitiData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/siti_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class TilesSeenData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/seen_tiles_fov110x90.pickle" if filename is not None else filename
        super().__init__(filename, config)


class DectimeData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/dectime_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class BitrateData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/bitrate_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class ChunkQualitySSIMData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/chunk_quality_ssim_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class ChunkQualityMSEData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/chunk_quality_mse_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class ChunkQualitySMSEData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/chunk_quality_s-mse_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class ChunkQualityWSMSEData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/chunk_quality_ws-mse_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class UserViewportData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/user_viewport_quality_qp.pickle" if filename is not None else filename
        super().__init__(filename, config)


class HeadMovementData(Data):
    def __init__(self, config: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/head_movement.pickle" if filename is not None else filename
        super().__init__(filename, config)
