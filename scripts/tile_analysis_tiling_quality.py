import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from PIL.Image import Resampling
from matplotlib import pyplot as plt, colors

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
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    for self.tile in self.tile_list:
                        serie: pd.Series = self.get_tile_data()

                        self.stats_defaultdict['Metric'].append(self.metric)
                        self.stats_defaultdict['Tiling'].append(self.tiling)
                        self.stats_defaultdict['Quality'].append(self.quality)
                        self.stats_defaultdict['Tile'].append(self.tile)
                        self.stats_defaultdict['n_arquivos'].append(len(serie))
                        self.stats_defaultdict['Média'].append(serie.mean())
                        self.stats_defaultdict['Desvio Padrão'].append(serie.std())

                        quartis = serie.quantile([0.00, 0.25, 0.50, 0.75, 1.00])
                        self.stats_defaultdict['Mínimo'].append(quartis[0])
                        self.stats_defaultdict['1º Quartil'].append(quartis[0.25])
                        self.stats_defaultdict['Mediana'].append(quartis[0.5])
                        self.stats_defaultdict['3º Quartil'].append(quartis[0.75])
                        self.stats_defaultdict['Máximo'].append(quartis[1])

    def get_tile_data(self):
        cross_section = self.database.xs(key=(self.tiling, self.quality, self.tile),
                                         level=('tiling', 'quality', 'tile'))
        return cross_section['value']

    def get_tile_data_list(self):
        bucket = [self.get_tile_data()
                  for self.tile in self.tile_list]
        return bucket

    def plots(self):
        self.make_heatmap_tiling_quality()
        self.make_heatmap_quality_tiling()

    @property
    def heatmap_tiling_quality_path(self):
        heatmap_path = self.heatmap_folder / f'heatmap_{self.metric}_{self.tiling}.pdf'
        return heatmap_path

    def make_heatmap_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()

            for self.tiling in self.tiling_list:
                if self.is_ok(self.heatmap_tiling_quality_path):                    continue
                m, n = splitx(self.tiling)

                figure_list = []
                for self.quality in self.quality_list, 1:
                    tiles_data = (self.database.xs((self.tiling, self.quality), level=('tiling', 'quality'))
                                  .groupby(['tile']).mean())

                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure = np.asarray(img)
                    figure_list.append(figure)

                fig, axs = plt.subplots(3, 2, figsize=(6, 7.5), dpi=300, constrained_layout=True)
                fig.suptitle(f'{self.metric}_{self.tiling}')

                norm = colors.Normalize(vmin=float(np.min(figure_list)), vmax=float(np.max(figure_list)))

                images = []
                for ax, figure, self.quality in zip(axs.flat, figure_list, self.quality_list):
                    im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal', norm=norm)
                    images.append(im)

                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.set_title(f'qp{self.quality}')

                cbr = fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)
                if self.metric == 'dash_m4s':
                    cbr.ax.ticklabel_format(axis='x', style='scientific',
                                            scilimits=(6, 6))

                quantity = self.dataset_structure[self.metric]['quantity']
                cbr.ax.set_xlabel(quantity)

                # fig.show()
                fig.savefig(heatmap_path)
                fig.clf()
                plt.close()

    @property
    def boxplot_tiling_quality_path(self):
        return self.boxplot_folder / f'boxplot_{self.metric}_tiling.pdf'

    @staticmethod
    def is_ok(path: Path) -> bool:
        exists = path.exists()
        if exists:
            print(f'\t{path} exists.')
        return exists

    def load_database(self):
        super().load_database()
        self.database = self.database.groupby(['name', 'projection', 'tiling', 'tile', 'quality']).mean()

    def get_bucket_list_by_quality(self):
        buckets = []
        for self.quality in self.quality_list:
            bucket = self.get_tile_data_list()
            buckets.append(bucket)
        return buckets

    def make_heatmap_quality_tiling(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()

            for self.quality in self.quality_list:
                heatmap_path = self.heatmap_folder / f'heatmap_{self.metric}_{self.quality}.pdf'
                if heatmap_path.exists():
                    print(f'\t{heatmap_path} exists.')
                    continue

                figure_list = []
                for i, self.tiling in enumerate(self.tiling_list, 1):
                    m, n = splitx(self.tiling)
                    tiles_data = (self.database.xs((self.tiling, self.quality), level=('tiling', 'quality'))
                                  .groupby(['tile']).mean())

                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure = np.asarray(img)
                    figure_list.append(figure)

                fig, axs = plt.subplots(3, 2, figsize=(6, 7.5), dpi=300, constrained_layout=True)
                fig.suptitle(f'{self.metric}_{self.quality}')

                norm = colors.Normalize(vmin=float(np.min(figure_list)), vmax=float(np.max(figure_list)))

                images = []
                for ax, figure, self.tiling in zip(axs.flat, figure_list, self.tiling_list):
                    im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal', norm=norm)
                    images.append(im)

                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.set_title(f'{self.tiling}')

                cbr = fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)
                if self.metric == 'dash_m4s':
                    cbr.ax.ticklabel_format(axis='x', style='scientific',
                                            scilimits=(6, 6))

                quantity = self.dataset_structure[self.metric]['quantity']
                cbr.ax.set_xlabel(quantity)

                fig.savefig(heatmap_path)
                fig.clf()
                plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    TileAnalysisTilingQuality(config)
