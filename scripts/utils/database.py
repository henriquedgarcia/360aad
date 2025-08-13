from abc import ABC
from pathlib import Path
from typing import Union

import pandas as pd

from scripts.utils.config import ConfigIf


class Data(ABC):
    level: list
    config: ConfigIf
    data: pd.DataFrame

    def __init__(self, filename: Union[str, Path], config_if: ConfigIf):
        self.config = config_if
        self.filename = filename
        self.data: Union[pd.DataFrame, object] = pd.read_hdf(filename)

        self.level = list(self.data.index.names)
        self.columns = list(self.data.columns)

    def __getitem__(self, column) -> Union[int, float]:
        """
        if str, search colum, full index
        if tuple, search index using cross-section
        :param column:
        :return:
        """
        return self.xs(levels=self.level)

    def xs(self, levels):
        key = tuple(getattr(self.config, level) for level in levels)
        return self.data.xs(key=key, level=levels)

    def group_by(self, level: list[str], operation) -> pd.DataFrame:
        grouped = self.data.groupby(level=level)
        return grouped.apply(operation)


class SitiData(Data):
    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/siti_qp_by_chunk_qp.hd5" if filename is None else filename
        super().__init__(filename, config_if)


class TilesSeenData(Data):
    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/tiles_seen_fov110x90.hd5" if filename is None else filename
        super().__init__(filename, config_if)


class DectimeData(Data):
    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/dectime_qp.hd5" if filename is None else filename
        super().__init__(filename, config_if)


class BitrateData(Data):
    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/bitrate_qp.hd5" if filename is None else filename
        super().__init__(filename, config_if)


class ChunkQualityData(Data):
    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/chunk_quality_qp.hd5" if filename is None else filename
        super().__init__(filename, config_if)


class ViewportQualityData(Data):
    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/user_viewport_quality_qp.hd5" if filename is None else filename
        super().__init__(filename, config_if)


class HeadMovementData(Data):
    """
    df.index.names ['name', 'projection', 'user', 'frame']
    df.columns ['yaw', 'pitch', 'roll']
    """

    def __init__(self, config_if: ConfigIf, filename: Union[str, Path] = None):
        filename = "dataset/head_movement.hd5" if filename is None else filename
        super().__init__(filename=filename, config_if=config_if)
