import os
from abc import ABC
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Generator

from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import load_pd_pickle

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


class HmDatasetAnalysis(AnalysisBase):
    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_stats(self):
        for self.name in self.name_list:
            for self.user in self.users_by_name[self.name]:
                key = (self.name, self.projection, self.user)
                level = ['name', 'projection', 'user']
                database = self.head_movement_db.xs(key=key, level=level).reset_index()
                for _, frame, azimuth, elevation, _ in database.itertuples():
                    # vetor1 = ea2xyz()
                    # vetor2 = ea2xyz
                    # ângulo entre vetores (em radianos)
                    pass

    def plots(self):
        pass


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    HmDatasetAnalysis(config)
