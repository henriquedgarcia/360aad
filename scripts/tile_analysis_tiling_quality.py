import os
from collections import defaultdict

import numpy as np
from PIL import Image
from PIL.Image import Resampling
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict, splitx


class TileAnalysisTilingQuality(AnalysisBase):
    def setup(self):
        print(f'Setup.')
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
            new_db = self.database.groupby(['name', 'projection', 'tiling', 'tile', 'quality']).mean()
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    bucket = self.get_bucket(new_db)

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

    def get_bucket(self, db):
        level = ('tiling', 'quality')
        keys = (self.tiling, self.quality,)
        values = db.xs(keys, level=level)
        series = values['value']
        bucket = series.to_list()
        return bucket

    def plots(self):
        # self.make_boxplot_tiling_quality()
        # self.make_boxplot_quality_tiling()
        self.make_heatmap_tiling_quality()
        self.make_heatmap_quality_tiling()

    def make_boxplot_tiling_quality(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()
            new_db = self.database.groupby(['name', 'projection', 'tiling', 'tile', 'quality']).mean()

            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_tiling.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.tiling in enumerate(self.tiling_list, 1):
                ax: plt.Axes = fig.add_subplot(3, 2, n)
                ax.set_title(f'qp{self.tiling}')

                print(f'fill bucket {self.tiling}')
                buckets = []
                for self.quality in self.quality_list:
                    bucket = self.get_bucket(new_db)
                    buckets.append(bucket)

                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_xlabel(f'Quality (QP)')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                              list(self.quality_list))
            fig.savefig(boxplot_path)
            fig.clf()

    def make_boxplot_quality_tiling(self):
        print(f'make_boxplot_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()
            new_db = self.database.groupby(['name', 'projection', 'tiling', 'tile', 'quality']).mean()

            boxplot_path = self.boxplot_folder / f'boxplot_{self.metric}_quality.png'
            if boxplot_path.exists():
                print(f'\t{boxplot_path} exists.')
                continue

            fig = plt.figure(figsize=(6, 7.5), layout='tight')
            fig.suptitle(f'{self.metric}')

            for n, self.quality in enumerate(self.quality_list, 1):
                ax: plt.Axes = fig.add_subplot(3, 2, n)
                ax.set_title(f'qp{self.quality}')

                print(f'fill buckets {self.quality}')
                buckets = []
                for self.tiling in self.tiling_list:
                    bucket = self.get_bucket(new_db)
                    buckets.append(bucket)

                ax.violinplot(buckets, showmeans=False, showmedians=True)
                ax.set_xlabel(f'Tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(list(range(1, len(self.tiling_list) + 1)),
                              list(self.tiling_list))
            fig.savefig(boxplot_path)
            fig.clf()

    def make_heatmap_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()

            for self.tiling in self.tiling_list:
                heatmap_path = self.heatmap_folder / f'heatmap_{self.metric}_{self.tiling}.png'
                if heatmap_path.exists():
                    print(f'\t{heatmap_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}_{self.tiling}')
                m, n = splitx(self.tiling)

                for i, self.quality in enumerate(self.quality_list, 1):
                    tiles_data = (self.database.xs((self.tiling, self.quality), level=('tiling', 'quality'))
                                  .groupby(['tile']).mean())

                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure = np.asarray(img)

                    ax: plt.Axes = fig.add_subplot(3, 2, i)
                    im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal')

                    fig.colorbar(im, ax=ax, location='bottom', anchor=(0, 1))

                    # ax.set_xticks([])
                    # ax.set_yticks([])
                    # ax.set_xticklabels([])
                    # ax.set_yticklabels([])
                    ax.set_title(f'qp{self.quality}')
                fig.show()
                fig.savefig(heatmap_path)
                fig.clf()

    def make_heatmap_quality_tiling(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()

            for n, self.quality in enumerate(self.quality_list, 1):
                heatmap_path = self.heatmap_folder / f'heatmap_{self.metric}_{self.quality}.png'
                if heatmap_path.exists():
                    print(f'\t{heatmap_path} exists.')
                    continue

                fig = plt.figure(figsize=(6, 7.5), layout='tight', dpi=300)
                fig.suptitle(f'{self.metric}')

                for i, self.tiling in enumerate(self.tiling_list, 1):
                    m, n = splitx(self.tiling)
                    tiles_data = (self.database.xs((self.tiling, self.quality), level=('tiling', 'quality'))
                                  .groupby(['tile']).mean())

                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure = np.asarray(img)

                    ax: plt.Axes = fig.add_subplot(3, 2, i)

                    im = ax.matshow(figure, cmap='jet')
                    fig.colorbar(im, ax=ax)

                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.set_title(f'{self.tiling}')

                fig.savefig(heatmap_path)
                fig.clf()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    TileAnalysisTilingQuality(config)
