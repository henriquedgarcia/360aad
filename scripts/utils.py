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


class GetDatabaseKeys:
    def get_database_keys(self):
        ...


class Bucket:
    def __init__(self):
        self.bucket = AutoDict()

    def __getitem__(self, item):
        return self.bucket[item]

    def load_bucket(self, bucket_path: Path):
        self.bucket = load_json(bucket_path)

    def get_bucket_values(self, keys=None):
        if keys is None:
            return self.bucket

        if isinstance(keys, list):
            return get_nested_value(self.bucket, keys)

        return self.bucket[keys]

    def set_bucket_value(self, value, keys):
        try:
            get_nested_value(self.bucket, keys).append(value)
        except AttributeError:
            set_nested_value(self.bucket, keys, [value])

    def keys(self):
        deep_search_keys(self.bucket)
        return list(self.bucket.keys())

    def save_bucket(self, filename):
        save_json(self.bucket, filename)


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

    results = []
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


def collect_keys_by_level(tree, level=0, result=None):
    result = result or defaultdict(list)

    if isinstance(tree, dict):
        for key, value in tree.items():
            result[level].append(key)
            collect_keys_by_level(value, level + 1, result)

    if level == 0: return list(result.values())


def iterate_over_key_tree(tree, level=0, keys=None):
    keys = keys or []

    if isinstance(tree, dict):
        for key, value in tree.items():
            keys.append(key)
            collect_keys_by_level(value, level + 1, keys)
            keys.pop()
    else:
        value = tree
        yield keys, value

    if level == 0: return list(keys.values())


