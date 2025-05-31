import os
import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from fitter import Fitter
from matplotlib import pyplot as plt
from py360tools.transform import ea2xyz

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.database import HeadMovementData
from scripts.utils.utils import load_pd_pickle

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
os.chdir('../')


def calc_shift_by_frame(ea):
    xyz = ea2xyz(ea=ea)
    xyz /= np.linalg.norm(xyz, axis=0)  # Normalizando para garantir vetores unitários
    v1 = xyz[:, :-1]  # Todos os vetores, exceto o último
    v2 = xyz[:, 1:]  # Todos os vetores, exceto o primeiro
    dot_product = np.sum(v1 * v2, axis=0)  # Soma dos produtos dos componentes
    dot_product = np.clip(dot_product, -1.0, 1.0)
    shifts_by_frame = np.arccos(dot_product)
    shifts_by_frame = np.insert(shifts_by_frame, 0, 0)
    return shifts_by_frame


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
                shifts_by_frame = calc_shift_by_frame(ea)

                vel_by_shift = shifts_by_frame * 30  # Rad/s. Velocidade instantânea
                vel_avg = np.mean(vel_by_shift)
                vel_std = np.std(vel_by_shift)

                stats.append((self.name, self.user, vel_avg, vel_std))

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
        csv_by_user = self.stats_workfolder / f'{self.class_name}_df_user.csv'
        csv_by_name = self.stats_workfolder / f'{self.class_name}_df_name.csv'
        if csv_by_user.exists():
            print(f'The file {csv_by_user} exists. skipping')
            return

        df_user_mean = self.stats_df['vel_avg'].groupby('user').mean()
        df_user_std = self.stats_df['vel_avg'].groupby('user').std().fillna(0)

        df_user: pd.DataFrame = pd.DataFrame({'vel_avg': df_user_mean, 'vel_std': df_user_std})
        df_user.sort_values('vel_avg')
        df_user.to_csv(self.stats_workfolder / f'{self.class_name}_df_user.csv')

        ###################

        df_name_mean = self.stats_df['vel_avg'].groupby('name').mean()
        df_name_std = self.stats_df['vel_avg'].groupby('name').std()

        df_name: pd.DataFrame = pd.DataFrame({'vel_avg': df_name_mean, 'vel_std': df_name_std})
        df_name.sort_values('vel_avg')
        df_name.to_csv(self.stats_workfolder / f'{self.class_name}_df_name.csv')

    def plots(self):
        self.plot_dist()

    def plot_dist(self):
        ax: plt.Axes

        dists = ['lognorm', 'weibull_min', 'gamma', 'erlang', 'chi2',
                 'chi', 'maxwell', 'rayleigh']
        fig, axes = plt.subplots(2, 4,
                                 # sharex=True, sharey=True,
                                 layout='constrained',
                                 figsize=(8, 5), dpi=300)
        axes = axes.flat
        dists = []
        stats = defaultdict(list)
        for ax, self.name in zip(axes, self.name_list):
            fitter_filename = self.histogram_folder / f'fitter_{self.name}.pickle'

            try:
                # load fitter
                f = pickle.loads(fitter_filename.read_bytes())
            except FileNotFoundError:
                # get data
                data = self.stats_df.xs(self.name, level='name')['vel_avg']

                # make fit
                f = Fitter(data, distributions=dists, bins=6)
                f.fit()
                fitter_filename.write_bytes(pickle.dumps(f))

            # plot bar
            width = np.min(np.diff(f.x))
            ax.bar(f.x, f.y, width=width, color=('blue', 0.2), edgecolor='black')

            # plot dists
            dists = list(f.df_errors.index)
            for dist in dists:
                ax.plot(f.x, f.fitted_pdf[dist], label=dist)

                stats['name'].append(self.name)
                stats['distribution'].append(dist)
                stats['fitted_param'].append(f.fitted_param[dist])
                stats['sumsquare_error'].append(f.df_errors['sumsquare_error'][dist])
                stats['aic'].append(f.df_errors['aic'][dist])
                stats['bic'].append(f.df_errors['bic'][dist])
                stats['kl_div'].append(f.df_errors['bic'][dist])
                stats['ks_statistic'].append(f.df_errors['bic'][dist])
                stats['ks_pvalue'].append(f.df_errors['bic'][dist])

            # Config axes
            ax.set_title(f'{self.name}')
            if list(self.name_list).index(self.name) > 3:
                ax.set_xlabel('rads/s')

        fig.legend(dists, loc='outside lower center', ncols=4, fontsize='large')
        fig.suptitle('Average Velocity (rad/s)')
        fig.show()
        fig.savefig(self.histogram_folder / f'{self.class_name}_auto_bins.pdf')
        pd.DataFrame(stats).to_csv(self.stats_workfolder / f'Distributions.csv', index=False)

    def bar_user(self):
        """
        distribuições contínuas positivas
        para velocidade média em um vídeo






        """
        df_user_mean = self.stats_df['vel_avg'].groupby('user').mean()
        df_user_mean.sort_values(inplace=True)
        plt.bar(range(len(df_user_mean)), df_user_mean)
        plt.hist(df_user_mean)
        plt.show()


if __name__ == '__main__':
    config = Config()
    HmDatasetAnalysis(config)
