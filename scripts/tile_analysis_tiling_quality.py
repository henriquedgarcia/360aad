import os
from collections import defaultdict

import numpy as np
from PIL import Image
from PIL.Image import Resampling
from matplotlib import pyplot as plt, colors

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import splitx, AutoDict


class TileAnalysisTilingQuality(AnalysisBase):
    @staticmethod
    def callback(self):
        self.database = self.database.groupby(['tiling', 'quality', 'tile']).mean()

    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['seen_tiles']
        self.load_database(self.callback)

    def make_stats(self):
        print(f'make_stats.')
        for self.metric in self.dataset_structure:
            for self.tiling in self.tiling_list:
                for self.quality in self.quality_list:
                    serie_data = self.get_chunk_data(('tiling', 'quality'))
                    quartis = serie_data.quantile([0.00, 0.25, 0.50, 0.75, 1.00])

                    self.stats_defaultdict['Metric'].append(self.metric)
                    self.stats_defaultdict['Tiling'].append(self.tiling)
                    self.stats_defaultdict['Quality'].append(self.quality)
                    self.stats_defaultdict['n_arquivos'].append(len(serie_data))
                    self.stats_defaultdict['Média'].append(serie_data.mean())
                    self.stats_defaultdict['Desvio Padrão'].append(serie_data.std())
                    self.stats_defaultdict['Mínimo'].append(quartis[0])
                    self.stats_defaultdict['1º Quartil'].append(quartis[0.25])
                    self.stats_defaultdict['Mediana'].append(quartis[0.5])
                    self.stats_defaultdict['3º Quartil'].append(quartis[0.75])
                    self.stats_defaultdict['Máximo'].append(quartis[1])

    def plots(self):
        self.make_heatmap_tiling_quality()
        self.make_heatmap_quality_tiling()
        self.make_heatmap_both()

    def make_heatmap_tiling_quality(self):
        print(f'make_heatmap_tiling_quality.')
        for self.metric in self.dataset_structure:
            for self.tiling in self.tiling_list:
                heatmap_path = self.heatmap_folder / f'heatmap_{self.metric}_{self.tiling}.pdf'
                if heatmap_path.exists():
                    print(f'file {heatmap_path} exists.')
                    continue
                heatmap_path.parent.mkdir(parents=True, exist_ok=True)

                m, n = splitx(self.tiling)
                figure_list = []
                for i, self.quality in enumerate(self.quality_list, 1):
                    tiles_data = self.get_chunk_data(('tiling', 'quality'))

                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure_list.append(np.asarray(img))

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

    def make_heatmap_quality_tiling(self):
        print(f'make_heatmap_quality_tiling.')
        for self.metric in self.dataset_structure:
            for self.quality in self.quality_list:
                heatmap_path = self.heatmap_folder / f'heatmap_{self.metric}_qp{self.quality}.pdf'
                if heatmap_path.exists():
                    print(f'file {heatmap_path} exists.')
                    continue
                heatmap_path.parent.mkdir(parents=True, exist_ok=True)

                figure_list = []
                for i, self.tiling in enumerate(self.tiling_list, 1):
                    m, n = splitx(self.tiling)
                    tiles_data = self.get_chunk_data(('tiling', 'quality'))

                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure_list.append(np.asarray(img))

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

                # fig.show()
                fig.savefig(heatmap_path)
                fig.clf()
                plt.close()

    def make_heatmap_both(self):
        print(f'make_heatmap_both.')
        figure_dict = AutoDict()
        metric_norm = {}
        heatmap_folder = self.heatmap_folder / 'normalized'
        heatmap_folder.mkdir(parents=True, exist_ok=True)

        for self.metric in self.dataset_structure:
            figure_list = []
            for self.tiling in self.tiling_list:
                m, n = splitx(self.tiling)
                for self.quality in self.quality_list:
                    tiles_data = self.get_chunk_data(('tiling', 'quality'))
                    array = np.array(tiles_data).reshape((n, m))
                    img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                    figure = np.asarray(img)
                    figure_list.append(figure)
                    figure_dict[self.metric][self.tiling][self.quality] = figure
            metric_norm[self.metric] = colors.Normalize(vmin=float(np.min(figure_list)), vmax=float(np.max(figure_list)))

        for self.metric in self.dataset_structure:
            norm = metric_norm[self.metric]

            for self.tiling in self.tiling_list:
                heatmap_path = heatmap_folder / f'heatmap_{self.metric}_{self.tiling}.pdf'

                fig, axs = plt.subplots(3, 2, figsize=(6, 7.5), dpi=300, constrained_layout=True)
                fig.suptitle(f'{self.metric}_{self.tiling}')
                im = None
                for ax, self.quality in zip(axs.flat, self.quality_list):
                    figure = figure_dict[self.metric][self.tiling][self.quality]
                    im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal', norm=norm)

                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.set_title(f'qp{self.quality}')

                cbr = fig.colorbar(im, ax=axs, orientation='horizontal', fraction=.1)
                if self.metric == 'dash_m4s':
                    cbr.ax.ticklabel_format(axis='x', style='scientific',
                                            scilimits=(6, 6))

                quantity = self.dataset_structure[self.metric]['quantity']
                cbr.ax.set_xlabel(quantity)

                # fig.show()
                fig.savefig(heatmap_path)
                fig.clf()
                plt.close()

        for self.metric in self.dataset_structure:
            norm = metric_norm[self.metric]

            for self.quality in self.quality_list:
                heatmap_path = heatmap_folder / f'heatmap_{self.metric}_{self.quality}.pdf'

                fig, axs = plt.subplots(3, 2, figsize=(6, 7.5), dpi=300, constrained_layout=True)
                fig.suptitle(f'{self.metric}_{self.quality}')
                im = None
                for ax, self.tiling in zip(axs.flat, self.tiling_list):
                    figure = figure_dict[self.metric][self.tiling][self.quality]
                    im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal', norm=norm)

                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                    ax.set_title(f'{self.tiling}')

                cbr = fig.colorbar(im, ax=axs, orientation='horizontal', fraction=.1)
                if self.metric == 'dash_m4s':
                    cbr.ax.ticklabel_format(axis='x', style='scientific',
                                            scilimits=(6, 6))

                quantity = self.dataset_structure[self.metric]['quantity']
                cbr.ax.set_xlabel(quantity)

                # fig.show()
                fig.savefig(heatmap_path)
                fig.clf()
                plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    TileAnalysisTilingQuality(config)
