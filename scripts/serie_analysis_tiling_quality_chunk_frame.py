import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict, load_pickle


class SerieAnalysisTilingQualityChunkFrame(AnalysisBase):
    def __init__(self, config):
        super().__init__(config)

    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']

    def make_stats(self):
        print(f'make_stats.')
        metric_list = list(self.dataset_structure)
        for self.metric in metric_list:
            self.load_database()

            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    serie_data_1 = self.database.loc[(self.tiling, self.quality)]['value']
                    self.stats_defaultdict['Metric'].append(self.metric)
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['n_arquivos'].append(len(serie_data_1))
                    self.stats_defaultdict['Média'].append(serie_data_1.mean())
                    self.stats_defaultdict['Desvio Padrão'].append(serie_data_1.std())
                    self.stats_defaultdict['Mínimo'].append(serie_data_1.quantile(0.00))
                    self.stats_defaultdict['1º Quartil'].append(serie_data_1.quantile(0.25))
                    self.stats_defaultdict['Mediana'].append(serie_data_1.quantile(0.50))
                    self.stats_defaultdict['3º Quartil'].append(serie_data_1.quantile(0.75))
                    self.stats_defaultdict['Máximo'].append(serie_data_1.quantile(1.00))

    def get_chunk_data(self):
        chunk_data = self.database.loc[(self.tiling, self.quality)]['value']
        return chunk_data

    def load_database(self):
        super().load_database()
        self.database = self.database.groupby(['tiling', 'quality', 'tile', 'chunk']).mean()
        index_int = self.database.index.levels[3].astype(int)
        self.database.index = self.database.index.set_levels(index_int, level=3)
        self.database.sort_index(inplace=True)

        if self.metric in ['dash_m4s', 'dectime_avg']:
            self.database = self.database.groupby(['tiling', 'quality', 'chunk']).sum()
        else:
            self.database = self.database.groupby(['tiling', 'quality', 'chunk']).mean()

    def load_database2(self, metric):
        # print(f'\t{self.__class__.__name__} loading {metric} database...')
        filename = self.dataset_structure[metric]['path']
        database = load_pickle(filename)

        # group by XXX - tiling - chunk (chunk is the temporal serie. Tiling compose the frame.)
        database = database.groupby(['tiling', 'quality', 'tile', 'chunk']).mean()

        # fix index order changing chunk index from str to int.
        index_int = database.index.levels[3].astype(int)
        database.index = database.index.set_levels(index_int, level=3)
        database.sort_index(inplace=True)

        if metric in ['dash_m4s', 'dectime_avg']:
            database = database.groupby(['tiling', 'quality', 'chunk']).sum()
        else:
            database = database.groupby(['tiling', 'quality', 'chunk']).mean()
        return database

    def corr(self):
        corr_default_dict = defaultdict(list)
        metric_list = list(self.dataset_structure)
        for self.metric in metric_list:
            self.load_database()
            database1 = self.database
            for metric2 in metric_list:
                database2 = self.load_database2(metric2)

                for self.tiling in self.tiling_list:
                    for self.quality in self.quality_list:
                        print(f'\t{self.tiling}_qp{self.quality}')
                        serie_data_1 = database1.loc[(self.tiling, self.quality)]['value']
                        serie_data_2 = database2.loc[(self.tiling, self.quality)]['value']
                        corr = serie_data_1.corr(serie_data_2, method='pearson')

                        corr_default_dict['Metric1'].append(self.metric)
                        corr_default_dict['Metric2'].append(metric2)
                        corr_default_dict['Tiling'].append(self.tiling)
                        corr_default_dict['Quality'].append(self.quality)
                        corr_default_dict['corr'].append(corr)

        pd.DataFrame(corr_default_dict).to_csv(self.corr_csv)

    def plots(self):
        self.corr()


        self.make_plot_quality_tiling_frame()
        self.make_plot_tiling_quality_frame()
        self.make_boxplot_quality_tiling_frame()
        self.make_boxplot_tiling_quality_frame()
        self.make_violinplot_quality_tiling_frame()
        self.make_violinplot_tiling_quality_frame()

    def make_plot_quality_tiling_frame(self):
        print(f'make_boxplot_quality_tiling.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.series_plot_folder / f'plot_{self.metric}_quality.pdf'
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
                    serie = self.get_chunk_data()
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
            boxplot_path = self.series_plot_folder / f'plot_{self.metric}_tiling.pdf'
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
                    serie = self.get_chunk_data()
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
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Check files
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_quality.pdf'
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

                serie_list = [self.get_chunk_data() for self.tiling in self.tiling_list]
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
            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_tiling.pdf'
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

                serie_list = [self.get_chunk_data() for self.quality in self.quality_list]
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
            boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_quality.pdf'
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

                serie_list = [self.get_chunk_data() for self.tiling in self.tiling_list]
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
            # Check files
            boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_tiling.pdf'
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

                serie_list = [self.get_chunk_data() for self.quality in self.quality_list]
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


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    SerieAnalysisTilingQualityChunkFrame(config)
