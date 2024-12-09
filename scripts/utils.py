import json
from collections import defaultdict
from functools import reduce
from pathlib import Path
from typing import Any, Union

from tqdm import tqdm


def get_nested_value(data, keys) -> Any:
    """
    Fetch value from nested dict using a list of keys.
    :param data:
    :type data: dict
    :param keys:
    :type keys: list
    :return: Any
    """

    def func(d, key):
        return d[key]

    try:
        return reduce(func, keys, data)
    except KeyError as e:
        raise KeyError(f"Key not found: {e}")
    except TypeError as e:
        raise TypeError(f"Invalid structure: {e}")


def set_nested_value(data, keys, value):
    subtree = get_nested_value(data, keys[:-1])
    subtree[keys[-1]] = value


class AutoDict(dict):
    def __missing__(self, key):
        self[key] = type(self)()
        return self[key]


class Bucket:
    database: dict[str, dict]

    def __init__(self, config):
        self.config = config
        self.bucket = AutoDict()
        self.category = None
        self.metric = self.config.metric

    def set_database(self, database_path: Path):
        self.database = load_json(database_path)

    def load_bucket(self, bucket_path: Path):
        self.bucket = load_json(bucket_path)

    def get_bucket(self, keys=None):
        if keys is None:
            return self.bucket
        if isinstance(keys, list):
            return get_nested_value(self.bucket, keys)
        else:
            return self.bucket[keys]

    def set_value(self, /, **kwargs):
        self.category = kwargs['category']
        value = self.get_video_dict_value()
        values = list(kwargs.values())
        keys = list(values)

        try:
            get_nested_value(self.bucket, keys).append(value)
        except AttributeError:
            set_nested_value(self.bucket, keys, [value])

    def get_video_dict_value(self):
        keys = self.get_keys()
        value = get_nested_value(self.database, keys)
        return value

    def get_keys(self):
        if self.config.metric == 'bitrate':
            return self.get_bitrate_keys()
        elif self.config.metric == 'time':
            return self.get_time_keys()

    def get_time_keys(self):
        if self.category not in ['dectime', 'dectime_avg', 'dectime_med', 'dectime_std']:
            return

        keys = [self.config.name, self.config.projection, self.config.tiling,
                self.config.tile, self.config.quality, self.config.chunk, self.category]
        return keys

    def get_bitrate_keys(self):
        keys = [self.config.name, self.config.projection, self.config.tiling, self.config.tile]
        if self.category == 'dash_mpd':
            keys.append('dash_mpd')
            return keys

        keys.append(self.config.quality)
        if self.category == 'dash_init':
            keys.append('dash_init')
            return keys

        keys.append(self.config.chunk)
        if self.category == 'dash_m4s':
            keys.append('dash_m4s')
            return keys
        raise ValueError('metric not supported')

    def keys(self):
        return list(self.bucket.keys())

    def __getitem__(self, item):
        return self.bucket[item]


def save_json(data: Union[dict, list], filename: Union[str, Path], separators=(',', ':'), indent=None):
    filename = Path(filename)
    try:
        filename.write_text(json.dumps(data, separators=separators, indent=indent), encoding='utf-8')
    except (FileNotFoundError, OSError):
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(json.dumps(data, separators=separators, indent=indent), encoding='utf-8')


def splitx(string: str) -> tuple[int, ...]:
    """
    Receive a string like "5x6x7" (no spaces) and return a tuple of ints, in
    this case, (5, 6, 7).
    :param string: A string of numbers separated with "x".
    :return: Return a list of int
    """
    return tuple(map(int, string.split('x')))


def load_json(filename: Union[str, Path], object_hook: type[dict] = None):
    filename = Path(filename)
    results = json.loads(filename.read_text(encoding='utf-8'), object_hook=object_hook)
    return results


class ProgressBar:
    t: tqdm

    def __init__(self, total, desc):
        self.t = tqdm(total=total, desc=desc)

    def new(self, total, desc):
        self.t = tqdm(total=total, desc=desc)

    def update(self, postfix_str):
        self.set_postfix_str(postfix_str)
        self.t.update()

    def set_postfix_str(self, postfix_str):
        self.t.set_postfix_str(postfix_str)

    def __del__(self):
        self.t.close()


def id2xy(idx: Union[int, str], shape: tuple):
    """

    :param idx: index
    :param shape: (height, width)
    :return: tuple
    """
    idx = int(idx)
    tile_x = idx % shape[1]
    tile_y = idx // shape[1]
    return tile_x, tile_y


def xy2idx(tile_x, tile_y, shape: tuple):
    idx = tile_x + tile_y * shape[0]
    return idx


def deep_search_keys(dictionary: dict) -> dict:
    if not isinstance(dictionary, dict):  # Se a árvore não é um dicionário, não há níveis a percorrer
        return {}

    results = defaultdict(set)
    stack = [(dictionary, 0)]
    while stack:
        current, level = stack.pop()

        # Adiciona as chaves do nível atual
        for key, value in current.items():
            results[level].update([key])

            # Adiciona os filhos se forem dicionários
            if isinstance(value, dict):
                stack.append((value, level + 1))

    return dict(results)
