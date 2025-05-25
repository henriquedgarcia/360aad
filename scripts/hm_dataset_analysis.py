import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from py360tools.transform import ea2xyz

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.database import HeadMovementData
from scripts.utils.utils import load_pd_pickle

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
os.chdir('../')


def cinematic_calc(ea):
    xyz = ea2xyz(ea=ea)
    xyz /= np.linalg.norm(xyz, axis=0)  # Normalizando para garantir vetores unitários
    v1 = xyz[:, :-1]  # Todos os vetores, exceto o último
    v2 = xyz[:, 1:]  # Todos os vetores, exceto o primeiro
    dot_product = np.sum(v1 * v2, axis=0)  # Soma dos produtos dos componentes
    dot_product = np.clip(dot_product, -1.0, 1.0)
    shifts_by_frame = np.arccos(dot_product)
    shifts_by_frame = np.insert(shifts_by_frame, 0, 0)
    vel_by_shift = shifts_by_frame * 30  # rad/s. Velocidade instantânea

    vel_avg = np.mean(vel_by_shift)
    vel_std = np.std(vel_by_shift)
    return vel_avg, vel_std, shifts_by_frame


class HmDatasetAnalysis(AnalysisBase):
    data: HeadMovementData
    shifts_by_frame_pickle: Path
    users_by_name: dict
    names_by_user: dict

    def setup(self):
        self.projection = 'cmp'

        self.data = HeadMovementData(self)

        self.users_by_name = defaultdict(list)
        for self.name in self.name_list:
            coss_section = self.data.xs(['name'])
            users = list(coss_section.index.unique('user'))
            self.users_by_name[self.name].extend(users)

        self.names_by_user = defaultdict(list)
        for self.name in self.name_list:
            coss_section = self.data.xs(['name'])
            for self.user in coss_section.index.unique('user'):
                self.names_by_user[self.user].append(self.name)

    @property
    def users_list(self):
        return self.users_by_name[self.name]

    def make_stats(self):
        try:
            self.stats_df = load_pd_pickle(self.stats_pickle)
        except FileNotFoundError:
            self.make_stats_df()

        self.group_stats()

    def make_stats_df(self):
        shift_by_frame = []
        stats = []
        for self.name in self.name_list:
            for self.user in self.users_list:
                database = self.data.xs(levels=['name', 'user'])
                ea = database[['pitch', 'yaw']].to_numpy().T
                vel_avg, vel_std, shifts_by_frame = cinematic_calc(ea)

                stats.append((self.name, self.user, vel_avg, vel_avg))

                for frame, shift in enumerate(shifts_by_frame):
                    shift_by_frame.append((self.name, self.user, frame, shift))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats, columns=['name', 'user', 'vel_avg', 'vel_std'])
        self.stats_df.to_csv(self.stats_csv, index=False)
        self.stats_df.set_index(['name', 'user'], inplace=True)
        self.stats_df.to_pickle(self.stats_pickle)

        shift_by_frame_df = pd.DataFrame(shift_by_frame, columns=['name', 'user', 'frame', 'rads'])
        shift_by_frame_df.set_index(['name', 'user', 'frame'], inplace=True)
        shift_by_frame_serie = shift_by_frame_df['rads']
        shift_by_frame_serie.name = 'shift'  # in rads / frame
        shift_by_frame_serie.to_pickle(self.stats_workfolder / f'{self.class_name}_shifts_by_frame.pickle')

    def group_stats(self):
        df_user_mean = self.stats_df['vel_avg'].groupby('user').mean()
        df_user_std = self.stats_df['vel_avg'].groupby('user').std().fillna(0, inplace=True)

        df_user: pd.DataFrame = pd.DataFrame({'vel_avg': df_user_mean, 'vel_std': df_user_std})
        df_user.sort_values('vel_avg')
        df_user.to_pickle(self.stats_workfolder / f'{self.class_name}_df_user.csv')

        df_name_mean = self.stats_df.groupby('name').mean()
        df_name_mean.columns = ['vel_avg']
        df_name_std = self.stats_df.groupby('name').std()
        df_name_std.columns = ['vel_std']
        df_name = df_name_mean.join(df_name_std)
        df_name.sort_values('vel_avg')
        df_name.to_csv(self.stats_workfolder / f'{self.class_name}_df_name.csv')

    def plots(self):
        pass


if __name__ == '__main__':
    config = Config()
    HmDatasetAnalysis(config)
