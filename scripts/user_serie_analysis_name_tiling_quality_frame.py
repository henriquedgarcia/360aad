import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import AutoDict


class UserSerieAnalysisNameTilingQualityFrame(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        del self.dataset_structure['dectime_std']

    def make_stats(self):
        print(f'make_stats.')
        metric_list = list(self.dataset_structure)
        for self.metric in metric_list:
            self.load_database()
            for self.user in self.users_list:
                self.load_get_tiles()

                for self.name in self.name_list:
                    for self.tiling in self.tiling_list:
                        for self.quality in self.quality_list:
                                serie_data = self.get_chunk_serie(('name','tiling', 'quality', 'user'))
                                self.stats_defaultdict['Metric'].append(self.metric)
                                self.stats_defaultdict['Tiling'].append(self.tiling)
                                self.stats_defaultdict['Quality'].append(self.quality)
                                self.stats_defaultdict['n_arquivos'].append(len(serie_data))
                                self.stats_defaultdict['Média'].append(serie_data.mean())
                                self.stats_defaultdict['Desvio Padrão'].append(serie_data.std())
                                self.stats_defaultdict['Mínimo'].append(serie_data.quantile(0.00))
                                self.stats_defaultdict['1º Quartil'].append(serie_data.quantile(0.25))
                                self.stats_defaultdict['Mediana'].append(serie_data.quantile(0.50))
                                self.stats_defaultdict['3º Quartil'].append(serie_data.quantile(0.75))
                                self.stats_defaultdict['Máximo'].append(serie_data.quantile(1.00))

    def plots(self):
        self.corr()

        self.make_plot_quality_tiling_frame()
        self.make_plot_tiling_quality_frame()
        self.make_boxplot_quality_tiling_frame()
        self.make_boxplot_tiling_quality_frame()
        self.make_violinplot_quality_tiling_frame()
        self.make_violinplot_tiling_quality_frame()

    def corr(self):
        print(f'Make correlation')
        metric_list = list(self.dataset_structure)

        try:
            df = pd.read_csv(self.corr_csv)
        except FileNotFoundError:
            corr_default_dict = defaultdict(list)
            for metric1 in metric_list:
                database1 = self.get_database(metric1)
                for metric2 in metric_list:
                    database2 = self.get_database(metric2)
                    for self.tiling in self.tiling_list:
                        for self.quality in self.quality_list:
                            print(f'\r\t({metric1}x{metric2}) {self.tiling}_qp{self.quality}', end='')
                            serie_data_1 = database1.loc[(self.tiling, self.quality)]['value']
                            serie_data_2 = database2.loc[(self.tiling, self.quality)]['value']
                            pearson = serie_data_1.corr(serie_data_2, method='pearson')

                            corr_default_dict['metric1'].append(metric1)
                            corr_default_dict['metric2'].append(metric2)
                            corr_default_dict['tiling'].append(self.tiling)
                            corr_default_dict['quality'].append(self.quality)
                            corr_default_dict['pearson'].append(pearson)
            print('')
            df = pd.DataFrame(corr_default_dict)
            df.to_csv(self.corr_csv, index=False)

        df_multi = df.set_index(['metric1', 'metric2', 'tiling', 'quality', ])
        l: plt.Line2D
        quality_list = list(map(int, self.quality_list))

        for n, metric1 in enumerate(metric_list[:-1]):
            for metric2 in metric_list[n + 1:]:
                filename = self.graphs_workfolder / 'corr' / f'by_quality_{metric1}_x_{metric2}.pdf'
                if not filename.exists():
                    fig = plt.figure(figsize=(6.4, 4.8), layout='tight', dpi=300)
                    ax: plt.Axes = fig.add_subplot(1, 1, 1)
                    for self.tiling in self.tiling_list:
                        serie = df_multi.xs((metric1, metric2, self.tiling), level=['metric1', 'metric2', 'tiling'])['pearson']
                        l, = ax.plot(quality_list, serie.to_list(), label=f'{self.tiling}')
                        ax.plot(quality_list, serie.to_list(), 'o', color=l.get_color())
                    ax.set_xticks(quality_list)
                    ax.set_ylim(top=1)
                    if metric1 == 'ssim' or metric2 == 'ssim':
                        ax.set_ylim((-1, 0))
                    ax.set_title(f'Correlation {metric1} x {metric2}')
                    ax.legend()
                    for qlt in self.quality_list:
                        ax.axvline(x=int(qlt), color='gray', linestyle='--')
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    fig.savefig(filename)

                filename = self.graphs_workfolder / 'corr' / f'by_tiling_{metric1}_x_{metric2}.pdf'
                tiling_list = list(self.tiling_list)
                tiling_pos_list = list(range(len(self.tiling_list)))

                if not filename.exists():
                    fig = plt.figure(figsize=(6.4, 4.8), layout='tight', dpi=300)
                    ax: plt.Axes = fig.add_subplot(1, 1, 1)
                    for self.quality in self.quality_list:
                        serie = df_multi.xs((metric1, metric2, int(self.quality)), level=['metric1', 'metric2', 'quality'])['pearson']
                        l, = ax.plot(tiling_pos_list, serie.to_list(), label=f'{self.quality}')
                        ax.plot(tiling_pos_list, serie.to_list(), 'o', color=l.get_color())
                    ax.set_xticks(tiling_pos_list, tiling_list)
                    ax.set_ylim(top=1)
                    if metric1 == 'ssim' or metric2 == 'ssim':
                        ax.set_ylim((-1, 0))
                    ax.set_title(f'Correlation {metric1} x {metric2}')
                    ax.legend()
                    for tiling_pos in tiling_pos_list:
                        ax.axvline(x=tiling_pos, color='gray', linestyle='--')
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    fig.savefig(filename)

    def make_plot_quality_tiling_frame(self):
        print(f'make_boxplot_quality_tiling.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.series_plot_folder / f'plot_quality_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.tiling in self.tiling_list:
                    serie = self.get_chunk_serie(('tiling', 'quality'))
                    ax.plot(serie, label=f'{self.tiling}')

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Chunk')
                ax.legend(loc='upper right')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_plot_tiling_quality_frame(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.series_plot_folder / f'plot_tiling_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.quality in self.quality_list:
                    serie = self.get_chunk_serie(('tiling', 'quality'))
                    ax.plot(serie, label=f'qp{self.quality}')

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Chunk')
                ax.legend(loc='upper right')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_quality_tiling_frame(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_quality_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_serie(('tiling', 'quality')) for self.tiling in self.tiling_list]
                ax.boxplot(serie_list, tick_labels=list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_tiling_quality_frame(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_tiling_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality')) for self.quality in self.quality_list]
                ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_quality_tiling_frame(self):
        print(f'make_violinplot_quality_tiling_frame.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.violinplot_folder / f'violinplot_quality_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality')) for self.tiling in self.tiling_list]
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def make_violinplot_tiling_quality_frame(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files°
            boxplot_path = self.violinplot_folder / f'violinplot_tiling_{self.metric}.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            # Load Database
            self.load_database()

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')
                ax: plt.Axes = fig.add_subplot(3, 2, n)

                serie_list = [self.get_chunk_data(('tiling', 'quality')) for self.quality in self.quality_list]
                ax.violinplot(serie_list, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Quality')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path)
            fig.clf()
            plt.close()

    def get_database(self, metric):
        database = super(UserSerieAnalysisNameTilingQualityFrame, self).get_database(metric)
        database = database.groupby(['name', 'tiling', 'quality', 'tile', 'chunk'], sort=False).mean()

        return database

    get_tiles: pd.DataFrame
    def load_get_tiles(self):
        self.get_tiles = self.get_database('get_tiles')
        pass


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    UserSerieAnalysisNameTilingQualityFrame(config)
