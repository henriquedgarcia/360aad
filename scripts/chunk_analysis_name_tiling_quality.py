import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict


class ChunkAnalysisNameTilingQuality(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                for self.tiling in self.tiling_list:
                    for self.quality in self.quality_list:
                        chunk_data = self.get_chunk_data()
                        self.stats_defaultdict['Metric'].append(self.metric)
                        self.stats_defaultdict['Name'].append(self.name)
                        self.stats_defaultdict['Tiling'].append(self.tiling)
                        self.stats_defaultdict['Quality'].append(self.quality)
                        self.stats_defaultdict['n_arquivos'].append(len(chunk_data))
                        self.stats_defaultdict['Média'].append(chunk_data.mean())
                        self.stats_defaultdict['Desvio Padrão'].append(chunk_data.std())
                        self.stats_defaultdict['Mínimo'].append(chunk_data.quantile(0.00))
                        self.stats_defaultdict['1º Quartil'].append(chunk_data.quantile(0.25))
                        self.stats_defaultdict['Mediana'].append(chunk_data.quantile(0.50))
                        self.stats_defaultdict['3º Quartil'].append(chunk_data.quantile(0.75))
                        self.stats_defaultdict['Máximo'].append(chunk_data.quantile(1.00))

    def get_chunk_data(self) -> pd.Series:
        database = self.database
        chunk_data: pd.Series = database.xs(key=(self.name, self.tiling, self.quality),
                                            level=('name', 'tiling', 'quality'))['value']
        return chunk_data

    def plots(self):
        # self.make_boxplot_name_quality_tiling()
        # self.make_boxplot_name_tiling_quality()
        self.make_boxplot_quality_tiling_name()
        # self.make_boxplot_quality_name_tiling()
        # self.make_boxplot_tiling_name_quality()
        # self.make_boxplot_tiling_quality_name()
        # self.make_violinplot_name_quality_tiling()
        # self.make_violinplot_name_tiling_quality()

    def make_boxplot_name_quality_tiling(self):
        print(f'make_boxplot_name_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.boxplot_folder / f'metric_name_tiling_quality' / f'boxplot_quality_tiling_{self.metric}_{self.name}.pdf'
                try:
                    boxplot_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

                for n, self.quality in enumerate(self.quality_list, 1):
                    print(f'\r\tPlot {self.metric} {self.name}_{self.quality}', end='')
                    ax: plt.Axes = fig.add_subplot(3, 2, n)

                    serie_list = [self.get_chunk_data()
                                  for self.tiling in self.tiling_list]
                    ax.boxplot(serie_list, tick_labels=list(self.tiling_list))

                    ax.set_title(f'qp{self.quality}')
                    ax.set_xlabel(f'Tiling')
                    ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                    if self.metric == 'dash_m4s':
                        ax.ticklabel_format(axis='y', style='scientific',
                                            scilimits=(6, 6))
                print(f'\n\tSaving.')
                fig.savefig(boxplot_path)
                fig.clf()
                plt.close()

    def make_boxplot_name_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            # Load Database
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.boxplot_folder / f'metric_name_tiling_quality' / f'boxplot_tiling_quality_{self.metric}_{self.name}.pdf'
                try:
                    boxplot_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

                for n, self.tiling in enumerate(self.tiling_list, 1):
                    print(f'\r\tPlot {self.metric} {self.name}_{self.tiling}', end='')
                    ax: plt.Axes = fig.add_subplot(3, 2, n)

                    serie_list = [self.get_chunk_data()
                                  for self.quality in self.quality_list]
                    ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                    ax.set_title(f'{self.tiling}')
                    ax.set_xlabel(f'Quality')
                    ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                    if self.metric == 'dash_m4s':
                        ax.ticklabel_format(axis='y', style='scientific',
                                            scilimits=(6, 6))
                print(f'\n\tSaving.')
                fig.savefig(boxplot_path)
                fig.clf()
                plt.close()

    def make_boxplot_quality_tiling_name(self):
        print(f'make_boxplot_quality_tiling_name.')
        ticks_position = list(range(1, len(self.name_list) + 1))
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.quality in self.quality_list:
                # Check files
                boxplot_path = self.boxplot_folder / f'metric_quality_tiling_name' / f'boxplot_tiling_name_{self.metric}_{self.quality}.pdf'
                try:
                    boxplot_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(10, 12), dpi=300,
                                 # constrained_layout=True,
                                 # tight_layout=True,
                                 )

                for n, self.tiling in enumerate(self.tiling_list, 1):
                    print(f'\r\tPlot qp{self.tiling}', end='')
                    ax: plt.Axes = fig.add_subplot(6, 1, n)

                    serie_list = [self.get_chunk_data().mean()
                                  for self.name in self.name_list]
                    # ax.boxplot(serie_list)
                    ax.bar(ticks_position, serie_list)
                    ax.set_xticks([])
                    if self.tiling == '12x8':
                        ax.set_xticks(ticks_position,
                                      list(self.name_list), rotation=-90, ha='center')
                    ax.set_title(f'{self.tiling}')
                    ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                    if self.metric == 'dash_m4s':
                        ax.ticklabel_format(axis='y', style='scientific',
                                            scilimits=(6, 6))

                print(f'\n\tSaving.')
                fig.suptitle(f'{self.metric}_{self.quality}')
                plt.subplots_adjust(left=0.07, right=0.99, bottom=0.00, top=0.94)
                # fig.show()
                fig.savefig(boxplot_path)
                fig.clf()
                plt.close()

    def make_boxplot_quality_tiling_name2(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            # Load Database
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.boxplot_folder / f'metric_name_tiling_quality' / f'boxplot_tiling_quality_{self.metric}_{self.name}.pdf'
                try:
                    boxplot_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

                for n, self.tiling in enumerate(self.tiling_list, 1):
                    print(f'\r\tPlot {self.tiling}', end='')
                    ax: plt.Axes = fig.add_subplot(3, 2, n)

                    serie_list = [self.get_chunk_data()
                                  for self.quality in self.quality_list]
                    ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                    ax.set_title(f'{self.tiling}')
                    ax.set_xlabel(f'Quality')
                    ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                    if self.metric == 'dash_m4s':
                        ax.ticklabel_format(axis='y', style='scientific',
                                            scilimits=(6, 6))
                print(f'\n\tSaving.')
                fig.savefig(boxplot_path)
                fig.clf()
                plt.close()

    def make_boxplot_tiling_name_quality(self):
        print(f'make_boxplot_name_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.boxplot_folder / f'metric_name_tiling_quality' / f'boxplot_quality_tiling_{self.metric}_{self.name}.pdf'
                try:
                    boxplot_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

                for n, self.quality in enumerate(self.quality_list, 1):
                    print(f'\r\tPlot qp{self.quality}', end='')
                    ax: plt.Axes = fig.add_subplot(3, 2, n)

                    serie_list = [self.get_chunk_data()
                                  for self.tiling in self.tiling_list]
                    ax.boxplot(serie_list, tick_labels=list(self.tiling_list))

                    ax.set_title(f'qp{self.quality}')
                    ax.set_xlabel(f'Tiling')
                    ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                    if self.metric == 'dash_m4s':
                        ax.ticklabel_format(axis='y', style='scientific',
                                            scilimits=(6, 6))
                print(f'\n\tSaving.')
                fig.savefig(boxplot_path)
                fig.clf()
                plt.close()

    def make_boxplot_tiling_quality_name(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            # Load Database
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.boxplot_folder / f'metric_name_tiling_quality' / f'boxplot_tiling_quality_{self.metric}_{self.name}.pdf'
                try:
                    boxplot_path.parent.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

                for n, self.tiling in enumerate(self.tiling_list, 1):
                    print(f'\r\tPlot {self.tiling}', end='')
                    ax: plt.Axes = fig.add_subplot(3, 2, n)

                    serie_list = [self.get_chunk_data()
                                  for self.quality in self.quality_list]
                    ax.boxplot(serie_list, tick_labels=list(self.quality_list))

                    ax.set_title(f'{self.tiling}')
                    ax.set_xlabel(f'Quality')
                    ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])

                    if self.metric == 'dash_m4s':
                        ax.ticklabel_format(axis='y', style='scientific',
                                            scilimits=(6, 6))
                print(f'\n\tSaving.')
                fig.savefig(boxplot_path)
                fig.clf()
                plt.close()

    def make_violinplot_name_quality_tiling(self):
        print(f'make_violinplot_quality_tiling_frame.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Load Database
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_{self.name}_quality.pdf'
                if boxplot_path.exists():
                    print(f'\t{boxplot_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

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

    def make_violinplot_name_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        # By metric ['dash_m4s', 'dectime_avg', 'ssim','mse', 's-mse', 'ws-mse']
        for self.metric in self.dataset_structure:
            # Load Database
            self.load_database()
            for self.name in self.name_list:
                # Check files
                boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_{self.name}_tiling.pdf'
                if boxplot_path.exists():
                    print(f'\t{boxplot_path} exists.')
                    continue
                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.name}')

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
    ChunkAnalysisNameTilingQuality(config)
