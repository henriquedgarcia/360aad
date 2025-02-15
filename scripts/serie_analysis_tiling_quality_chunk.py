import os
from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict


class SerieAnalysisTilingQuality(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        del self.dataset_structure['dectime_std']

    def make_stats(self):
        return

    def get_data(self):
        data = []
        for self.chunk in self.chunk_list:
            chunk_data = list(self.database.xs((self.tiling, self.quality, self.chunk), level=('tiling', 'quality', 'chunk'))['value'])
            data.append(np.average(chunk_data))

        return data

    def plots(self):
        self.make_plot_quality_tiling()
        self.make_boxplot_tiling_quality()

    def make_plot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()

            boxplot_path_quality = self.boxplot_folder / f'boxplot_{self.metric}_quality.pdf'
            if boxplot_path_quality.exists():
                print(f'\t{boxplot_path_quality} exists.')
                continue

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                print(f'Plot qp{self.quality}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.tiling in self.tiling_list:
                    bucket = self.get_data()
                    ax.plot(bucket, label=f'{self.tiling}')

                ax.set_title(f'qp{self.quality}')
                ax.set_xlabel(f'Chunk')
                ax.legend()
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))
            fig.savefig(boxplot_path_quality)
            fig.clf()

    def make_boxplot_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()

            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_tiling.pdf'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                print(f'Plot {self.tiling}')

                ax: plt.Axes = fig.add_subplot(3, 2, n)
                for self.quality in self.quality_list:
                    bucket = self.get_data()
                    ax.plot(bucket, label=f'qp{self.quality}')

                ax.set_title(f'{self.tiling}')
                ax.set_xlabel(f'Chunk')
                ax.legend()
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                if self.metric == 'dash_m4s':
                    ax.ticklabel_format(axis='y', style='scientific',
                                        scilimits=(6, 6))

            fig.savefig(boxplot_path)
            fig.clf()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    SerieAnalysisTilingQuality(config)
