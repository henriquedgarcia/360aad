import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict


class ChunkAnalysisTilingQualityGroupName(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        # del self.dataset_structure['dectime_std']

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    for self.group in self.groups_list:
                        for self.name in self.name_list:
                            if not self.name_list[self.name]["group"] == self.group:
                                continue
                            serie = self.get_chunk_data()
                            self.stats_defaultdict['Metric'].append(self.metric)
                            self.stats_defaultdict['Tiling'].append(self.tiling)
                            self.stats_defaultdict['Quality'].append(self.quality)
                            self.stats_defaultdict['Name'].append(self.name)
                            self.stats_defaultdict['n_arquivos'].append(len(serie))
                            self.stats_defaultdict['Média'].append(serie.mean())
                            self.stats_defaultdict['Desvio Padrão'].append(serie.std())
                            self.stats_defaultdict['Mínimo'].append(serie.quantile(0.00))
                            self.stats_defaultdict['1º Quartil'].append(serie.quantile(0.25))
                            self.stats_defaultdict['Mediana'].append(serie.quantile(0.50))
                            self.stats_defaultdict['3º Quartil'].append(serie.quantile(0.75))
                            self.stats_defaultdict['Máximo'].append(serie.quantile(1.00))

    def load_database(self):
        super(ChunkAnalysisTilingQualityGroupName, self).load_database()

    def get_chunk_data(self, by_chunk=False) -> pd.Series:
        database = self.database
        chunk_data: pd.Series = database.xs((self.tiling, self.quality, self.name), level=('tiling', 'quality', 'name'))['value']
        return chunk_data

    def plots(self):
        pass

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

            for n, self.quality in enumerate(self.quality_list, 1):
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
                plt.close()

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
                plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisTilingQualityGroupName(config)
