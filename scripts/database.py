from scripts.utils import get_nested_value, load_json


class Database:
    database: dict = None

    def __init__(self, config):
        self.config = config

    def get_value(self):
        value = get_nested_value(self.database, self.get_keys())
        return value

    def get_aggregates_chunks(self):
        value = []
        for self.config.chunk in self.config.chunk_list:
            value = get_nested_value(self.database, self.get_keys())
        return value

    def load(self, filename):
        self.database = load_json(filename)

    def get_keys(self) -> list:
        ...


class TimeDatabase(Database):
    categories = ['dectime', 'dectime_avg', 'dectime_med', 'dectime_std']

    def get_keys(self):
        # assert self.config.category in self.categories
        return [self.config.name, self.config.projection, self.config.tiling,
                self.config.tile, self.config.quality, self.config.chunk,
                self.config.category]


class BitrateDatabase(Database):
    categories = ['dash_mpd', 'dash_init', 'dash_m4s']

    def get_keys(self):
        # assert self.config.category in self.categories
        keys = [self.config.name, self.config.projection, self.config.tiling, self.config.tile]
        if self.config.category == 'dash_mpd':
            keys.append(self.config.category)
            return keys

        keys.append(self.config.quality)
        if self.config.category == 'dash_init':
            keys.append(self.config.category)
            return keys

        keys.append(self.config.chunk)
        if self.config.category == 'dash_m4s':
            keys.append(self.config.category)
            return keys
        raise ValueError('metric not supported')


class QualityDatabase(Database):
    categories = ['ssim', 'mse', 's-mse', 'ws-mse']

    def get_keys(self):
        # assert self.config.category in self.categories
        return [self.config.name, self.config.projection, self.config.tiling,
                self.config.tile, self.config.quality, self.config.chunk,
                self.config.category]


class GetTilesDatabase(Database):
    categories = ['frame', 'chunk']

    def get_keys(self):
        # assert self.config.category in self.categories
        keys = [self.config.name, self.config.projection, self.config.tiling,
                self.config.user, self.config.category]

        if self.config.category == 'chunks':
            keys.append(self.config.chunk)
        return keys


def database_factory(metric, config):
    config.metric = metric
    if metric == 'time':
        return TimeDatabase(config)
    elif metric == 'bitrate':
        return BitrateDatabase(config)
    elif metric == 'chunk_quality':
        return QualityDatabase(config)
    elif metric == 'get_tiles':
        return GetTilesDatabase(config)
    else:
        return None
