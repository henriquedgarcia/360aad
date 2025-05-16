import os
from collections import defaultdict
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from py360tools.transform import ea2xyz

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import load_pd_pickle

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
os.chdir('../')


def main():
    class HmDatasetAnalysis(AnalysisBase):
        data: HMData
        shifts_by_frame_pickle: Path

        def setup(self):
            self.projection = 'cmp'
            self.stats_defaultdict = defaultdict(list)
            self.shifts_by_frame_pickle = self.stats_csv.with_name(f'{self.class_name}_shifts_by_frame.pickle')

            self.data = HMData(self)
            # level_values = self.data.data.index.get_level_values('name')
            # isin = level_values.isin(list(self.name_list))
            # self.data.data = self.data.data.loc[isin]
            # self.data.data.to_pickle(self.head_movement_path)

        def make_stats(self):
            try:
                self.stats_df = load_pd_pickle(self.stats_csv.with_suffix('.pickle'))
            except FileNotFoundError:
                self.make_stats_df()

            df_user_mean = self.stats_df.groupby('user').mean()
            df_user_mean.columns=['vel_avg', 'dist_avg']
            df_user_std = self.stats_df.groupby('user').std()
            df_user_std.columns=['vel_std', 'dist_std']
            df_user: pd.DataFrame = df_user_mean.join(df_user_std)
            df_user.sort_values('vel_avg')

            df_name_mean = self.stats_df.groupby('name').mean()
            df_name_mean.columns=['vel_avg', 'dist_avg']
            df_name_std = self.stats_df.groupby('name').std()
            df_name_std.columns=['vel_std', 'dist_std']
            df_name = df_name_mean.join(df_name_std)
            df_name.sort_values('vel_avg')

        def make_stats_df(self):
            users_by_name = {}
            for name in self.config.name_list_original:
                key = (name, self.projection)
                level = ['name', 'projection']
                coss_section = self.head_movement_db.xs(key=key, level=level)
                level_values = coss_section.index.get_level_values('user').unique()
                users = list(level_values)
                users_by_name[name] = users

            data = []
            for self.name in self.config.name_list_original:
                for self.user in users_by_name[self.name]:
                    levels = ['name', 'projection', 'user']
                    database = self.data.xs(levels=levels)
                    ea = database[['pitch', 'yaw']].to_numpy().T
                    xyz = ea2xyz(ea=ea)
                    xyz /= np.linalg.norm(xyz, axis=0)  # Normalizando para garantir vetores unitários
                    v1 = xyz[:, :-1]  # Todos os vetores, exceto o último
                    v2 = xyz[:, 1:]  # Todos os vetores, exceto o primeiro
                    dot_product = np.sum(v1 * v2, axis=0)  # Soma dos produtos dos componentes
                    dot_product = np.clip(dot_product, -1.0, 1.0)
                    shifts_by_frame = np.arccos(dot_product)
                    shifts_by_frame = np.insert(shifts_by_frame, 0, 0)
                    vel_by_shift = shifts_by_frame * 30  # rad/s
                    vel_avg = np.mean(vel_by_shift)
                    dist = np.sum(shifts_by_frame)

                    for frame, shift in enumerate(shifts_by_frame):
                        data.append((self.name, self.projection, self.user, frame, shift))

                    self.stats_defaultdict['name'].append(self.name)
                    self.stats_defaultdict['projection'].append(self.projection)
                    self.stats_defaultdict['user'].append(self.user)
                    self.stats_defaultdict['vel_avg'].append(vel_avg)
                    self.stats_defaultdict['dist'].append(dist)

            self.stats_df: pd.DataFrame = pd.DataFrame(self.stats_defaultdict)
            self.stats_df.to_csv(self.stats_csv, index=False)
            self.stats_df.set_index(['name', 'projection', 'user'], inplace=True)
            self.stats_df.to_pickle(self.stats_csv.with_suffix('.pickle'))

            df = pd.DataFrame(data, columns=['name', 'projection', 'user', 'frame', 'rads'])
            df.set_index(['name', 'projection', 'user', 'frame'], inplace=True)
            df.to_pickle(self.shifts_by_frame_pickle)

        def plots(self):
            pass

    config = Config()
    HmDatasetAnalysis(config)


class HMData:
    def __init__(self, context: AnalysisBase, database='head_movement'):
        self.level = context.dataset_structure[database]['keys']
        self.columns = context.dataset_structure[database]['columns']
        self.context = context
        filename = context.head_movement_path
        self.data: pd.DataFrame = load_pd_pickle(Path(filename))

    def __getitem__(self, column) -> Union[int, float]:
        return self.xs(self.level)[column]

    def xs(self, levels) -> pd.DataFrame:
        key = tuple(getattr(self.context, level) for level in levels)
        return self.data.xs(key=key, level=levels)

    def group_by(self, level: list[str], operation) -> pd.DataFrame:
        grouped = self.data.groupby(level=level)
        return grouped.apply(operation)


if __name__ == '__main__':
    main()
