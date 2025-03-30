import os
from collections import defaultdict

import numpy as np
from PIL import Image
from PIL.Image import Resampling
from matplotlib import pyplot as plt, colors

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import splitx, AutoDict

cor = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']


class TileAnalysisTilingQuality(AnalysisBase):
    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['seen_tiles']

        self.load_database()
        self.database = self.database.groupby(level=['name', 'projection', 'tiling', 'tile', 'quality']).mean()

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
        # self.make_heatmap_tiling_quality_std()
        # self.make_heatmap_quality_tiling_std()
        # self.make_heatmap_both()
        # self.make_barplot_tiling_quality()
        # self.make_barplot_quality_tiling()
        # self.make_barplot_tiling_quality_frame()
        # self.make_barplot_quality_tiling_frame()

        # self.make_boxplot_quality_tiling()
        # self.make_boxplot_tiling_quality()

    def make_heatmap_tiling_quality(self):
        def main():
            print(f'make_heatmap_tiling_quality.')
            for self.metric in self.dataset_structure:
                for self.tiling in self.tiling_list:
                    heatmap_path = self.heatmap_folder / f'heatmap_tiling_{self.metric}_{self.tiling}.pdf'

                    if file_is_ok(heatmap_path): continue
                    img_list = make_image_list()
                    fig = make_figure(img_list)
                    fig.savefig(heatmap_path)
                    fig.clf()

        def file_is_ok(heatmap_path):
            if heatmap_path.exists():
                print(f'file {heatmap_path} exists.')
                return True
            heatmap_path.parent.mkdir(parents=True, exist_ok=True)
            return False

        def make_image_list():
            m, n = splitx(self.tiling)
            img_list = []
            for i, self.quality in enumerate(self.quality_list, 1):
                tiles_data = self.get_chunk_data(('tiling', 'quality'))
                tiles_data = tiles_data.groupby(level=['tile']).mean()

                array = np.array(tiles_data).reshape((n, m))
                img = Image.fromarray(array).resize((30, 20), resample=Resampling.NEAREST)

                imagem_expandida = Image.new("RGB", (34, 23),
                                             "black")  # Cor do padding (ajustável)
                for linha in range(2):
                    for coluna in range(3):
                        # Cortar uma subimagem da original
                        esquerda, superior = coluna * 10, linha * 10
                        direita, inferior = esquerda + 10, superior + 10
                        subimagem = img.crop((esquerda, superior, direita, inferior))

                        x_offset = coluna * 11 + 1
                        y_offset = linha * 11 + 1
                        imagem_expandida.paste(subimagem,
                                               (x_offset, y_offset))
                img_list.append(np.asarray(imagem_expandida))
            return img_list

        def make_figure(img_list):
            fig, axs = plt.subplots(3, 2, figsize=(6, 7.5), dpi=300, constrained_layout=True)
            norm = colors.Normalize(vmin=float(np.min(img_list)), vmax=float(np.max(img_list)))
            images = []

            for ax, figure, self.quality in zip(axs.flat, img_list, self.quality_list):
                im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal', norm=norm)
                images.append(im)

                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xticklabels([])
                ax.set_yticklabels([])
                ax.set_title(f'qp{self.quality}')

            quantity = self.dataset_structure[self.metric]['quantity']
            cbr = fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)
            cbr.ax.set_xlabel(quantity)
            if self.metric == 'dash_m4s':
                cbr.ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            # fig.show()
            fig.suptitle(f'{self.metric}_{self.tiling}')
            plt.close()
            return fig

        main()

    def make_heatmap_quality_tiling(self):
        def main():
            print(f'make_heatmap_quality_tiling.')
            for self.metric in self.dataset_structure:
                for self.quality in self.quality_list:
                    heatmap_path = self.heatmap_folder / f'heatmap_quality_{self.metric}_qp{self.quality}.pdf'
                    if file_is_ok(heatmap_path): continue
                    img_list = make_image_list()
                    fig = make_figure(img_list)
                    fig.savefig(heatmap_path)
                    fig.clf()

        def make_image_list():
            img_list = []
            for i, self.tiling in enumerate(self.tiling_list, 1):
                m, n = splitx(self.tiling)
                tiles_data = self.get_chunk_data(('tiling', 'quality'))
                tiles_data = tiles_data.groupby(level=['tile']).mean()
                array = np.array(tiles_data).reshape((n, m))
                img = Image.fromarray(array).resize((12, 8), resample=Resampling.NEAREST)
                img_list.append(np.asarray(img))
            return img_list

        def make_figure(img_list):
            fig, axs = plt.subplots(3, 2, figsize=(6, 7.5), dpi=300, constrained_layout=True)
            norm = colors.Normalize(vmin=float(np.min(img_list)), vmax=float(np.max(img_list)))
            images = []

            for ax, figure, self.tiling in zip(axs.flat, img_list, self.tiling_list):
                im = ax.imshow(figure, cmap='jet', interpolation='none', aspect='equal', norm=norm)
                images.append(im)

                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xticklabels([])
                ax.set_yticklabels([])
                ax.set_title(f'{self.tiling}')

            quantity = self.dataset_structure[self.metric]['quantity']
            cbr = fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)
            cbr.ax.set_xlabel(quantity)
            if self.metric == 'dash_m4s':
                cbr.ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            # fig.show()
            fig.suptitle(f'{self.metric}_qp{self.quality}')
            plt.close()
            return fig

        def file_is_ok(heatmap_path):
            if heatmap_path.exists():
                print(f'file {heatmap_path} exists.')
                return True
            heatmap_path.parent.mkdir(parents=True, exist_ok=True)
            return False

        main()

    def make_heatmap_tiling_quality_std(self):
        def callback():
            self.database = self.database.groupby(['name', 'projection', 'tiling', 'quality', 'tile']).mean()

        self.load_database(callback)

        print(f'make_heatmap_tiling_quality.')
        for self.metric in self.dataset_structure:
            for self.tiling in self.tiling_list:
                heatmap_path = self.heatmap_folder / f'heatmap_std_{self.metric}_{self.tiling}.pdf'
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

    def make_heatmap_quality_tiling_std(self):
        print(f'make_heatmap_quality_tiling.')
        for self.metric in self.dataset_structure:
            for self.quality in self.quality_list:
                heatmap_path = self.heatmap_folder / f'heatmap_std_{self.metric}_qp{self.quality}.pdf'
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

    def make_boxplot_quality_tiling(self):
        boxplot_folder = self.boxplot_folder / 'quality_tiling'
        for self.metric in self.dataset_structure:
            barplot_path = boxplot_folder / f'boxplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
            for index, self.quality in enumerate(self.quality_list, 1):
                data = [self.get_chunk_data(('tiling', 'quality'))
                        for self.tiling in self.tiling_list]

                ax: plt.Axes = fig.add_subplot(3, 2, index)
                ax.boxplot(data, tick_labels=list(self.tiling_list))
                ax.set_title(f'qp{self.quality}')
                #                 ax.legend(loc='upper right')
                ax.set_xlabel('tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)), list(self.tiling_list))
                # ax.set_yscale('log')
                if self.metric == 'ssim':
                    ax.set_ylim(top=1.0)
                else:
                    ax.set_ylim(bottom=0)

            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_boxplot_tiling_quality(self):
        boxplot_folder = self.boxplot_folder / 'tiling_quality'
        for self.metric in self.dataset_structure:
            barplot_path = boxplot_folder / f'boxplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
            for index, self.quality in enumerate(self.quality_list, 1):
                data = [self.get_chunk_data(('tiling', 'quality'))
                        for self.tiling in self.tiling_list]

                ax: plt.Axes = fig.add_subplot(3, 2, index)
                ax.boxplot(data, tick_labels=list(self.tiling_list))
                ax.set_title(f'qp{self.quality}')
                #                 ax.legend(loc='upper right')
                ax.set_xlabel('tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)), list(self.tiling_list))
                # ax.set_yscale('log')
                if self.metric == 'ssim':
                    ax.set_ylim(top=1.0)
                else:
                    ax.set_ylim(bottom=0)

            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_barplot_tiling_quality(self):
        barplot_folder = self.barplot_folder / 'tiling_quality'
        for self.metric in self.dataset_structure:
            barplot_path = barplot_folder / f'barplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
            for index, self.quality in enumerate(self.quality_list, 1):
                x = [i for i in range(len(self.tiling_list))]
                data = [self.get_chunk_data(('tiling', 'quality')).mean().mean()
                        for self.tiling in self.tiling_list]

                ax: plt.Axes = fig.add_subplot(3, 2, index)
                ax.bar(x, data)
                ax.set_title(f'qp{self.quality}')
                #                 ax.legend(loc='upper right')
                ax.set_xlabel('tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)), list(self.tiling_list))
                # ax.set_yscale('log')
                if self.metric == 'ssim':
                    ax.set_ylim(top=1.0)
                else:
                    ax.set_ylim(bottom=0)
            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_barplot_quality_tiling(self):
        barplot_folder = self.barplot_folder / 'quality_tiling'
        barplot_folder.mkdir(parents=True, exist_ok=True)
        for self.metric in self.dataset_structure:
            barplot_path = barplot_folder / f'barplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
            for index, self.quality in enumerate(self.quality_list, 1):
                x = [i for i in range(len(self.tiling_list))]
                data = [self.get_chunk_data(('tiling', 'quality')).mean().mean()
                        for self.tiling in self.tiling_list]

                ax: plt.Axes = fig.add_subplot(3, 2, index)
                ax.bar(x, data)
                ax.set_title(f'qp{self.quality}')
                #                 ax.legend(loc='upper right')
                ax.set_xlabel('tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)), list(self.tiling_list))
                # ax.set_yscale('log')
                if self.metric == 'ssim':
                    ax.set_ylim(top=1.0)
                else:
                    ax.set_ylim(bottom=0)

            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_barplot_tiling_quality_frame(self):
        barplot_folder = self.barplot_folder / 'tiling_quality_frame'
        for self.metric in self.dataset_structure:
            barplot_path = barplot_folder / f'barplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
            for index, self.quality in enumerate(self.quality_list, 1):
                x = [i for i in range(len(self.tiling_list))]
                if self.metric in ['dectime', 'bitrate']:
                    data = [self.get_chunk_data(('tiling', 'quality')).mean().sum()
                            for self.tiling in self.tiling_list]
                else:
                    data = [self.get_chunk_data(('tiling', 'quality')).mean().mean()
                            for self.tiling in self.tiling_list]

                ax: plt.Axes = fig.add_subplot(3, 2, index)
                ax.bar(x, data)
                ax.set_title(f'qp{self.quality}')
                #                 ax.legend(loc='upper right')
                ax.set_xlabel('tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)), list(self.tiling_list))
                # ax.set_yscale('log')
                if self.metric == 'ssim':
                    ax.set_ylim(top=1.0)
                else:
                    ax.set_ylim(bottom=0)
            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()

    def make_barplot_quality_tiling_frame(self):
        barplot_folder = self.barplot_folder / 'quality_tiling_frame'
        barplot_folder.mkdir(parents=True, exist_ok=True)
        for self.metric in self.dataset_structure:
            barplot_path = barplot_folder / f'barplot_{self.metric}.pdf'
            if barplot_path.exists():
                print(f'\t{barplot_path} exists.')
                continue

            fig = plt.figure(figsize=(7.5, 6), layout='tight', dpi=300)
            for index, self.quality in enumerate(self.quality_list, 1):
                x = [i for i in range(len(self.tiling_list))]
                if self.metric in ['dectime', 'bitrate']:
                    data = [self.get_chunk_data(('tiling', 'quality')).sum()
                            for self.tiling in self.tiling_list]
                else:
                    data = [self.get_chunk_data(('tiling', 'quality')).mean()
                            for self.tiling in self.tiling_list]

                ax: plt.Axes = fig.add_subplot(3, 2, index)
                ax.bar(x, data)
                ax.set_title(f'qp{self.quality}')
                #                 ax.legend(loc='upper right')
                ax.set_xlabel('tiling')
                ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
                ax.set_xticks(range(len(self.tiling_list)), list(self.tiling_list))
                # ax.set_yscale('log')
                if self.metric == 'ssim':
                    ax.set_ylim(top=1.0)
                else:
                    ax.set_ylim(bottom=0)

            barplot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(barplot_path)
            fig.clf()
            plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    TileAnalysisTilingQuality(config)
