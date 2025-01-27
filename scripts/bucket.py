from scripts.utils import AutoDict, get_nested_value, set_nested_value


class Bucket:
    def __init__(self):
        self.bucket = AutoDict()

    def __getitem__(self, item):
        return self.bucket[item]

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

    def categories(self):
        # deep_search_keys(self.bucket)
        return list(self.bucket.keys())
