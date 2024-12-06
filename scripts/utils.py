import json
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

    def func(d, key): return d[key]

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
    def __init__(self, config):
        self.config = config
        self.bucket = AutoDict()
        self.metric = None
        self.database = None

    def set_database(self, database_path: Path):
        self.database = load_json(database_path)

    def set_bucket(self, bucket_path: Path):
        self.bucket = load_json(bucket_path)

    def get_bucket(self, keys=None):
        if keys is None:
            return self.bucket
        if isinstance(keys, list):
            return get_nested_value(self.bucket, keys)
        else:
            return self.bucket[keys]

    def set_value(self, /, **kwargs):
        self.metric = kwargs['metric']
        value = self.get_video_dict_value()
        values = list(kwargs.values())
        keys = list(values)

        try:
            get_nested_value(self.bucket, keys).append(value)
        except AttributeError:
            set_nested_value(self.bucket, keys, [value])

    def get_video_dict_value(self):
        keys = self.get_bitrate_keys()
        value = get_nested_value(self.database, keys)
        return value

    def get_bitrate_keys(self):
        keys = [self.config.name, self.config.projection, self.config.tiling, self.config.tile]
        if self.metric == 'dash_mpd':
            keys.append('dash_mpd')
            return keys

        keys.append(self.config.quality)
        if self.metric == 'dash_init':
            keys.append('dash_init')
            return keys

        keys.append(self.config.chunk)
        if self.metric == 'dash_m4s':
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
