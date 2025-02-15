from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils import AutoDict


class ChunkAnalysisTilingQualityName(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        del self.dataset_structure['dectime_std']

    def make_stats(self):
        print(f'Calculating stats.')
        self.stats_defaultdict = defaultdict(list)
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    bucket = list(self.database.xs((self.tiling, self.quality), level=('tiling', 'quality'))['value'])

                    self.stats_defaultdict['Metric'].append(self.metric)
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['n_arquivos'].append(len(bucket))
                    self.stats_defaultdict['Média'].append(np.average(bucket))
                    self.stats_defaultdict['Desvio Padrão'].append(np.std(bucket))
                    self.stats_defaultdict['Mínimo'].append(np.quantile(bucket, 0))
                    self.stats_defaultdict['1º Quartil'].append(np.quantile(bucket, 0.25))
                    self.stats_defaultdict['Mediana'].append(np.quantile(bucket, 0.5))
                    self.stats_defaultdict['3º Quartil'].append(np.quantile(bucket, 0.75))
                    self.stats_defaultdict['Máximo'].append(np.quantile(bucket, 1))

    def plots(self):
        self.make_boxplot_quality_tiling()
        self.make_boxplot_tiling_quality()

    def make_boxplot_quality_tiling(self):
        print(f'Boxplot 1.')
        n_subplots = len(self.tiling_list)
        for self.metric in self.dataset_structure:
            self.load_database()

            boxplot_path_quality = self.boxplot_folder / f'boxplot_quality.pdf'
            if boxplot_path_quality.exists():
                print(f'\t{boxplot_path_quality} exists.')
                continue

            fig = plt.figure(figsize=(6, 8.5), layout='tight')

            for n, self.quality in enumerate(self.quality_list):
                ax: plt.Axes = fig.add_subplot(n_subplots, 1, n)
                ax.set_title(f'qp{self.quality}')

                print(f'fill bucket')

                buckets = []
                for self.tiling in self.tiling_list:
                    bucket = list(self.database.xs(self.quality, level='quality')['value'])
                    buckets.append(bucket)

                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))
                fig.savefig(boxplot_path_quality)
                fig.clf()

    def make_boxplot_tiling_quality(self):
        print(f'Boxplot 2.')
        n_subplots = len(self.quality_list)
        for self.metric in self.dataset_structure:
            self.load_database()

            boxplot_path = self.boxplot_folder / f'boxplot.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            fig = plt.figure(figsize=(6, 8.5), layout='tight')

            for n, self.tiling in enumerate(self.tiling_list):
                ax: plt.Axes = fig.add_subplot(n_subplots, 1, n)
                ax.set_title(f'qp{self.tiling}')

                print(f'fill bucket')

                buckets = []
                for self.quality in self.quality_list:
                    bucket = list(self.database.xs(self.quality, level='quality')['value'])
                    buckets.append(bucket)

                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_xlabel(f'Quality (QP)')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))
                fig.savefig(boxplot_path)
                fig.clf()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisQuality(config)


class ChunkAnalysisTilingQualityTime(AnalysisBase):
    def setup(self):
        print(f'Setup.')
        self.metric = 'time'
        self.bucket_keys_name = ('tiling', 'quality')
        self.database_keys = {'dectime_avg': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']}
        self.categories = tuple(self.database_keys)
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_bucket(self):
        print(f'Collecting Data.')
        total = 181 * len(self.quality_list) * len(self.chunk_list)
        for self.name in self.name_list:
            self.load_database()
            self.start_ui(total, '\t' + self.name)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.update_ui(f'{self.tiling}/{self.tile}_qp{self.quality}')
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                for cat in self.categories:
                                    value = self.get_database_value(cat)
                                    self.set_bucket_value(self.get_bucket_keys(cat), value, )
            self.close_ui()

    def make_stats(self):
        print(f'Calculating stats.')
        for self.tiling in self.tiling_list:
            for self.quality in self.quality_list:
                for cat in self.categories:
                    bucket_value = self.bucket[cat][self.tiling][self.quality]
                    self.stats_defaultdict['Metric'].append(cat)
                    self.stats_defaultdict['tiling'].append(self.tiling)
                    self.stats_defaultdict['quality'].append(self.quality)
                    self.stats_defaultdict['n_chunks'].append(len(bucket_value))
                    self.stats_defaultdict['Média'].append(np.average(bucket_value))
                    self.stats_defaultdict['Desvio Padrão'].append(np.std(bucket_value))
                    self.stats_defaultdict['Mínimo'].append(np.quantile(bucket_value, 0))
                    self.stats_defaultdict['1º Quartil'].append(np.quantile(bucket_value, 0.25))
                    self.stats_defaultdict['Mediana'].append(np.quantile(bucket_value, 0.5))
                    self.stats_defaultdict['3º Quartil'].append(np.quantile(bucket_value, 0.75))
                    self.stats_defaultdict['Máximo'].append(np.quantile(bucket_value, 1))

    def plots(self):
        self.make_boxplot1()
        self.make_boxplot2()

    def make_boxplot1(self):
        print(f'Boxplot 1.')
        n_subplots = len(self.categories)
        for self.quality in self.quality_list:
            boxplot_path_quality = self.boxplot_folder / f'boxplot_qp{self.quality}.pdf'
            if boxplot_path_quality.exists():
                print(f'\t{boxplot_path_quality} exists.')
                continue

            fig = plt.figure(figsize=(6, 2.4), layout='tight')
            fig.suptitle(f'QP {self.quality}')

            for n, self.category in enumerate(self.categories, 1):
                ax: plt.Axes = fig.add_subplot(n_subplots, 1, n)
                ax.set_title(self.category)

                buckets = []
                for self.tiling in self.tiling_list:
                    bucket_keys = self.get_bucket_keys(self.category)
                    bucket_value = self.get_bucket_value(bucket_keys)
                    buckets.append(bucket_value)
                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_ylabel(f'Time (s)')
                ax.set_xlabel(f'Tiling')
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))
            fig.savefig(boxplot_path_quality)
            fig.clf()

    def make_boxplot2(self):
        print(f'Boxplot 2.')
        n_subplots = len(self.categories)
        for self.tiling in self.tiling_list:
            boxplot_path_tiling = self.boxplot_folder / f'boxplot_{self.tiling}.pdf'
            if boxplot_path_tiling.exists():
                print(f'\t{boxplot_path_tiling} exists.')
                continue

            fig = plt.figure(figsize=(6, 2.4), layout='tight')
            fig.suptitle(f'{self.tiling}')

            for n, self.category in enumerate(self.categories, 1):
                ax: plt.Axes = fig.add_subplot(n_subplots, 1, n)
                ax.set_title(self.category)

                buckets = []
                for self.quality in self.quality_list:
                    bucket_keys = self.get_bucket_keys(self.category)
                    bucket_value = self.get_bucket_value(bucket_keys)
                    buckets.append(bucket_value)
                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))
                ax.set_xlabel(f'Quality (QP)')
                ax.set_ylabel(f'Time (s)')
                ax.set_title(self.category)
            fig.tight_layout()
            fig.savefig(boxplot_path_tiling)
            fig.clf()


class ChunkAnalysisTilingQualityQuality(AnalysisBase):
    def setup(self):
        print(f'Setup.')
        self.metric = 'chunk_quality'
        self.bucket_keys_name = ('tiling', 'quality')
        self.database_keys = {'ssim': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              'mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              's-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              'ws-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']}
        self.categories = tuple(self.database_keys)
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_bucket(self):
        print(f'Collecting Data.')
        total = 181 * len(self.quality_list)
        for self.name in self.name_list:
            self.load_database()
            self.start_ui(total, '\t' + self.name)
            for self.tiling in self.tiling_list:
                for self.tile in self.tile_list:
                    for self.quality in self.quality_list:
                        self.update_ui(f'{self.tiling}/{self.tile}_qp{self.quality}')
                        for self.chunk in self.chunk_list:
                            for cat in self.categories:
                                value = np.average(self.get_database_value(cat))
                                self.set_bucket_value(self.get_bucket_keys(cat), value, )
            self.close_ui()

    def make_stats(self):
        print(f'Calculating stats.')
        for self.tiling in self.tiling_list:
            for self.quality in self.quality_list:
                for cat in self.categories:
                    bucket_value = self.bucket[cat][self.tiling][self.quality]

                    self.stats_defaultdict['Metric'].append(cat)
                    self.stats_defaultdict['tiling'].append(self.tiling)
                    self.stats_defaultdict['quality'].append(self.quality)
                    self.stats_defaultdict['n_chunks'].append(len(bucket_value))
                    self.stats_defaultdict['Média'].append(np.average(bucket_value))
                    self.stats_defaultdict['Desvio Padrão'].append(np.std(bucket_value))
                    self.stats_defaultdict['Mínimo'].append(np.quantile(bucket_value, 0))
                    self.stats_defaultdict['1º Quartil'].append(np.quantile(bucket_value, 0.25))
                    self.stats_defaultdict['Mediana'].append(np.quantile(bucket_value, 0.5))
                    self.stats_defaultdict['3º Quartil'].append(np.quantile(bucket_value, 0.75))
                    self.stats_defaultdict['Máximo'].append(np.quantile(bucket_value, 1))

    def plots(self):
        self.make_boxplot1()
        self.make_boxplot2()

    def make_boxplot1(self):
        print(f'Boxplot 1.')
        n_subplots = len(self.categories)
        for self.quality in self.quality_list:
            boxplot_path_quality = self.boxplot_folder / f'boxplot_qp{self.quality}.pdf'
            if boxplot_path_quality.exists():
                print(f'\t{boxplot_path_quality} exists.')
                continue

            fig = plt.figure(figsize=(6, 8.5), layout='tight')
            fig.suptitle(f'QP {self.quality}')

            for n, self.category in enumerate(self.categories, 1):
                ax: plt.Axes = fig.add_subplot(n_subplots, 1, n)
                ax.set_title(self.category)

                buckets = []
                for self.tiling in self.tiling_list:
                    bucket_keys = self.get_bucket_keys(self.category)
                    bucket_value = self.get_bucket_value(bucket_keys)
                    buckets.append(bucket_value)
                ax.violinplot(buckets, showmeans=False, showmedians=True)
                # ax.boxplot(buckets, whis=(0, 100), tick_labels=list(self.tiling_list))
                ax.set_xlabel(f'Tiling')
                ax.set_title(self.category)
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))
            fig.savefig(boxplot_path_quality)
            fig.clf()

    def make_boxplot2(self):
        print(f'Boxplot 2.')
        n_subplots = len(self.categories)
        for self.tiling in self.tiling_list:
            boxplot_path_tiling = self.boxplot_folder / f'boxplot_{self.tiling}.pdf'
            if boxplot_path_tiling.exists():
                print(f'\t{boxplot_path_tiling} exists.')
                continue

            fig = plt.figure(figsize=(6, 8.5), layout='tight')
            fig.suptitle(f'{self.tiling}')

            for n, self.category in enumerate(self.categories, 1):
                ax: plt.Axes = fig.add_subplot(n_subplots, 1, n)
                ax.set_title(self.category)

                buckets = []
                for self.quality in self.quality_list:
                    bucket_keys = self.get_bucket_keys(self.category)
                    bucket_value = self.get_bucket_value(bucket_keys)
                    buckets.append(bucket_value)
                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))
                ax.set_xlabel(f'Quality (QP)')
                ax.set_title(self.category)
            fig.savefig(boxplot_path_tiling)
            fig.clf()
