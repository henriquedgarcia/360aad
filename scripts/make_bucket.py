from pathlib import Path
from typing import Optional

from scripts.config import ConfigIf, Config
from scripts.database import database_factory, Database
from scripts.utils import Bucket, get_nested_value, save_json


class MakeBuket(ConfigIf):
    bucket: Bucket
    metric_list = ['time', 'bitrate', 'chunk_quality', 'get_tiles']
    metric: str
    database: Optional[Database]

    def __init__(self, config: Config, metric: str, bucket_keys_name: list, categories: list):
        """

        :param metric:
        :param bucket_keys_name:
        """
        self.database = None
        assert metric in self.metric_list

        self.config = config
        self.config.metric = metric
        self.bucket_keys_name = bucket_keys_name
        self.categories = categories
        if metric in ['time', 'bitrate', 'chunk_quality']:
            self.iterator = self.iterator1
        elif metric == 'get_tiles':
            self.iterator = self.iterator2

    def make_bucket(self):
        self.bucket = Bucket()
        self.database = database_factory(self.config.metric, self.config)

        for self.category in self.categories:
            for _ in self.iterator():
                self.set_bucket()
        return self.bucket

    def iterator1(self):
        """
        bitrate, chunk_quality, time iterator
        :return:
        """
        for self.name in self.name_list:
            for self.config.v in self.categories:
                for self.projection in self.projection_list:
                    for self.tiling in self.tiling_list:
                        for self.tile in self.tile_list:
                            for self.quality in self.quality_list:
                                for self.chunk in self.chunk_list:
                                    yield

    def iterator2(self):
        """
        GetTiles iterator
        :return:
        """
        for self.name in self.name_list:
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.user in self.users_list:
                        yield

    @property
    def name(self):
        return self.config.name

    @name.setter
    def name(self, value):
        self.config.name = value
        self.database.load(self.database_json_path)

    def iterator3(self):
        """
        viewport iterator
        :return:
        """
        for self.category in self.categories:
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.user in self.users_list:
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                yield

    def set_bucket(self):
        self.bucket.set_bucket_value(self.database.get_value(),
                                     self.get_bucket_keys())

    def get_database_value(self, keys):
        value = get_nested_value(self.database.database, keys)
        return value

    def get_bucket_keys(self):
        bucket_keys = [getattr(self.config, keys_name) for keys_name in self.bucket_keys_name]
        return [self.category] + bucket_keys

    @property
    def database_json_path(self):
        database_path = Path(f'dataset/{self.config.metric}')
        return database_path / f'{self.config.metric}_{self.name}.json'

    def save_bucket(self, bucket_json):
        bucket = self.bucket.get_bucket_values()
        save_json(bucket, bucket_json)
