import os
from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict


class ChunkAnalysisTilingQualityName(AnalysisBase):
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
                    for self.name in self.name_list:
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

    def get_chunk_data(self) -> pd.Series:
        database = self.database
        chunk_data: pd.Series = database.xs((self.tiling, self.quality, self.name), level=('tiling', 'quality', 'name'))['value']
        return chunk_data

    def plots(self):
        self.make_violinplot_quality_tiling()
        self.make_violinplot_tiling_quality()

    def make_violinplot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling')
        for self.metric in self.dataset_structure:
            self.database = None
            for self.quality in self.quality_list:
                boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_quality.pdf'
                if boxplot_path.exists():
                    print(f'\t{boxplot_path} exists.')
                    continue

                if self.database is None:
                    self.load_database()

                fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
                ax: plt.Axes = fig.add_subplot(1, 1, 1)

                for self.tiling in self.tiling_list:
                    print(f'Plot {self.tiling}')
                    serie_list = [self.get_chunk_data() for self.name in self.name_list]
                    vp = ax.violinplot(serie_list, showmeans=False, showmedians=True)
                    vp['bodies'][0].set_label(self.tiling)

                ax.set_xticks(list(range(1, len(self.name_list) + 1)),
                              list(self.name_list), rotation=-90)
                ax.set_title(f'{self.metric}_qp{self.quality}')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

                ax.legend(loc='upper right')
                fig.savefig(boxplot_path)
                # fig.show()
                fig.clf()
                plt.close()

    def make_violinplot_tiling_quality(self):
        print(f'make_boxplot_quality_tiling')
        for self.metric in self.dataset_structure:
            self.database = None
            for n, self.tiling in enumerate(self.tiling_list):
                boxplot_path = self.violinplot_folder / f'violinplot_{self.metric}_tiling.pdf'
                if boxplot_path.exists():
                    print(f'\t{boxplot_path} exists.')
                    continue

                if self.database is None:
                    self.load_database()

                fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.tiling}')
                ax: plt.Axes = fig.add_subplot(1, 1, 1)

                for n, self.quality in enumerate(self.quality_list):
                    print(f'Plot qp{self.quality}')
                    serie_list = [self.get_chunk_data() for self.name in self.name_list]
                    vp = ax.violinplot(serie_list, showmeans=False, showmedians=True)
                    vp['bodies'][0].set_label(self.tiling)

                ax.set_xticks(list(range(1, len(self.name_list) + 1)),
                              list(self.name_list), rotation=-90)
                ax.set_title(f'{self.metric}_qp{self.tiling}')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

                ax.legend(loc='upper right')
                fig.savefig(boxplot_path)
                # fig.show()
                fig.clf()
                plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisTilingQualityName(config)
