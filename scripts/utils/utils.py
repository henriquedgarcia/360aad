import json
import pickle
from collections import defaultdict
from collections.abc import Sequence
from functools import reduce
from pathlib import Path
from typing import Callable, Any, Union

import pandas as pd


def get_nested_value_(data, keys) -> Any:
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


def get_nested_value(data, keys) -> Any:
    results = data
    for key in keys:
        results = results[key]
    return results


def get_nested_value__(data, keys) -> Any:
    """
    Fetch value from nested dict using a list of keys.
    :param data:
    :type data: dict
    :param keys:
    :type keys: list
    :return: Any
    """

    if not keys:
        return data
    return get_nested_value(data.get(keys[0], {}), keys[1:])


def set_nested_value(data, keys, value):
    subtree = get_nested_value(data, keys[:-1])
    subtree[keys[-1]] = value


class AutoDict(dict):
    def __missing__(self, key):
        self[key] = type(self)()
        return self[key]


def save_json(data: Union[dict, list], filename: Union[str, Path], separators=(',', ':'), indent=None):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_json(filename: Union[str, Path], object_hook: type[dict] = None):
    filename = Path(filename)
    results = json.loads(filename.read_text(encoding='utf-8'), object_hook=object_hook)
    return results


def save_pickle(data: Any, filename: Union[str, Path]):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_pd_pickle(filename: Union[str, Path]):
    results = pd.read_pickle(filename)
    return results


def splitx(string: str) -> tuple[int, ...]:
    """
    Receive a string like "5x6x7" (no spaces) and return a tuple of ints, in
    this case, (5, 6, 7).
    :param string: A string of numbers separated with "x".
    :return: Return a list of int
    """
    return tuple(map(int, string.split('x')))


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


class LazyProperty:
    _setter: Callable = None
    _deleter: Callable = None
    name: str
    attr_name: str

    def __init__(self, getter):
        """
        Creates a property that waits for the first use to be initialized. After this, it always returns the same
        result.

        Usage:

        class Bar:
            @LazyProperty
            def foo(self):
                print('calculating... ', end='')
                value = 1+1
                return value

            @foo.setter
            def foo(self, value):
                print('Setting foo with value automatically.')

        test = Bar()
        print(test.foo)  # print 'calculating... 2'
        print(test.foo)  # print '2'
        test.foo = 4     # print 'Setting foo with value automatically.'
        print(test.foo)  # print '4'. No calculate anymore.

        The value is stored in Bar._foo only once.

        :param getter:
        :type getter: Callable
        """
        self.getter = getter
        self.name = self.getter.__name__
        self.attr_name = '_' + self.name

    def __get__(self, instance, owner):
        """
        Run getter after getattr

        :param instance:
        :param owner:
        :return:
        """
        try:
            value = getattr(instance, self.attr_name)
        except AttributeError:
            value = self.getter(instance)
            setattr(instance, self.attr_name, value)
        return value

    def __set__(self, instance, value):
        """
        Run setter after setattr

        :param instance:
        :param value:
        :return:
        """
        setattr(instance, self.attr_name, value)

        if self._setter is not None:
            self._setter(instance, value)

    def __delete__(self, instance):
        """
        Run deleter before delattr
        :param instance:
        :return:
        """
        if self._deleter is not None:
            self._deleter(instance)

        delattr(instance, '_' + self.name)

    def setter(self, value: Callable):
        self._setter = value

    def deleter(self, value: Callable):
        self._deleter = value


def set_bucket_value(bucket: dict,
                     bucket_keys: Sequence,
                     value: Any):
    try:
        get_nested_value(bucket, bucket_keys).append(value)
    except AttributeError:
        set_nested_value(bucket, bucket_keys, [value])


def get_bucket_value(bucket: dict,
                     bucket_keys: list) -> Any:
    return get_nested_value(bucket, bucket_keys)


def dict_to_tuples(d, parent_key=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from dict_to_tuples(v, parent_key + (k,))
    else:
        yield parent_key + (d,)
