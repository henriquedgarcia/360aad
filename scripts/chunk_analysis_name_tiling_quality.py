import os
from collections import defaultdict
from contextlib import contextmanager

from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config
from scripts.utils.utils import AutoDict


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
                        chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
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

    def plots(self):
        self.make_boxplot_name_quality_tiling()
        self.make_boxplot_name_tiling_quality()
        self.make_boxplot_quality_tiling_name()
        self.make_boxplot_tiling_quality_name()

        self.make_violinplot_name_quality_tiling()
        self.make_violinplot_name_tiling_quality()
        self.make_violinplot_quality_tiling_name()
        self.make_violinplot_tiling_quality_name()

    def make_boxplot_name_quality_tiling(self):
        print(f'make_boxplot_name_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                self.filename = (self.boxplot_folder / f'metric_name_quality_tiling' /
                                 f'boxplot_quality_tiling_{self.metric}_{self.name}.pdf')
                if self.check_filename(): continue
                with self.make_figure(figsize=(6, 7.5), dpi=300, layout="tight",
                                      title=f'{self.metric}_{self.name}') as fig:
                    for n, self.quality in enumerate(self.quality_list, 1):
                        print(f'\r\tPlot {self.metric} {self.name}_qp{self.quality}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'qp{self.quality}',
                                               xticklabels=list(self.tiling_list),
                                               xlabel='Tiling') as ax:
                            for pos, self.tiling in enumerate(self.tiling_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.boxplot(chunk_data, positions=[pos], widths=0.8)

    def make_boxplot_name_tiling_quality(self):
        print(f'make_boxplot_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                self.filename = (self.boxplot_folder / f'metric_name_tiling_quality' /
                                 f'boxplot_tiling_quality_{self.metric}_{self.name}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(6, 7.5), dpi=300, layout="tight",
                                      title=f'{self.metric}_{self.name}') as fig:
                    for n, self.tiling in enumerate(self.tiling_list, 1):
                        print(f'\r\tPlot {self.metric} {self.name}_{self.tiling}', end='')

                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'{self.tiling}',
                                               xticklabels=list(self.quality_list),
                                               xlabel='Quality') as ax:
                            for pos, self.quality in enumerate(self.quality_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.boxplot(chunk_data, positions=[pos], widths=0.8)

    def make_boxplot_quality_tiling_name(self):
        print(f'make_boxplot_quality_tiling_name.')

        ticks_position = list(range(1, len(self.name_list) + 1))
        legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, self.name_list)]

        for self.metric in self.dataset_structure:
            self.load_database()
            for self.quality in self.quality_list:
                self.filename = (self.boxplot_folder / f'metric_quality_tiling_name' /
                                 f'boxplot_tiling_name_{self.metric}_qp{self.quality}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(14, 6), dpi=300, layout="constrained",
                                      legends_list=legends_list,
                                      title=f'{self.metric}_qp{self.quality}') as fig:
                    for n, self.tiling in enumerate(self.tiling_list, 1):
                        print(f'\r\tPlot {self.metric} {self.quality}_{self.tiling}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'{self.tiling}',
                                               xticklabels=ticks_position
                                               ) as ax:
                            for pos, self.name in enumerate(self.name_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.boxplot(chunk_data, positions=[pos], widths=0.8)

    def make_boxplot_tiling_quality_name(self):
        print(f'make_boxplot_tiling_quality_name.')

        ticks_position = list(range(1, len(self.name_list) + 1))
        legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, self.name_list)]

        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                self.filename = (self.boxplot_folder / f'metric_tiling_quality_name' /
                                 f'boxplot_quality_name_{self.metric}_{self.tiling}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(14, 6), dpi=300, layout="constrained",
                                      legends_list=legends_list,
                                      title=f'{self.metric}_{self.tiling}') as fig:
                    for n, self.quality in enumerate(self.quality_list, 1):
                        print(f'\r\tPlot {self.metric}_{self.tiling}_qp{self.quality}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=self.quality,
                                               xticklabels=ticks_position
                                               ) as ax:
                            for pos, self.name in enumerate(self.name_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.boxplot(chunk_data, positions=[pos], widths=0.8)

    def make_violinplot_name_quality_tiling(self):
        print(f'make_violinplot_name_quality_tiling.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                self.filename = (self.violinplot_folder / f'metric_name_quality_tiling' /
                                 f'violinplot_{self.metric}_{self.name}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(6, 7.5), dpi=300, layout="tight",
                                      title=f'{self.metric}_{self.name}') as fig:

                    for n, self.quality in enumerate(self.quality_list, 1):
                        print(f'\r\tPlot {self.metric} {self.name}_qp{self.quality}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'qp{self.quality}',
                                               xticklabels=list(self.tiling_list),
                                               xlabel='Tiling') as ax:

                            for pos, self.tiling in enumerate(self.tiling_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.violinplot(chunk_data, positions=[pos], widths=0.8, showmeans=False, showmedians=True)

    def make_violinplot_name_tiling_quality(self):
        print(f'make_violinplot_name_tiling_quality.')
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.name in self.name_list:
                self.filename = (self.violinplot_folder / f'metric_name_tiling_quality' /
                                 f'violinplot_{self.metric}_{self.name}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(6, 7.5), dpi=300, layout="tight",
                                      title=f'{self.metric}_{self.name}') as fig:

                    for n, self.tiling in enumerate(self.tiling_list, 1):
                        print(f'\r\tPlot {self.metric} {self.name}_{self.tiling}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'{self.tiling}',
                                               xticklabels=list(self.quality_list),
                                               xlabel='Quality') as ax:
                            for pos, self.quality in enumerate(self.quality_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.violinplot(chunk_data, positions=[pos], widths=0.8, showmeans=False, showmedians=True)

    def make_violinplot_quality_tiling_name(self):
        print(f'make_violinplot_quality_tiling_name.')

        ticks_position = list(range(1, len(self.name_list) + 1))
        legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, self.name_list)]

        for self.metric in self.dataset_structure:
            self.load_database()
            for self.quality in self.quality_list:
                self.filename = (self.violinplot_folder / f'metric_quality_tiling_name' /
                                 f'violinplot_{self.metric}_qp{self.quality}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(14, 6), dpi=300, layout="constrained",
                                      legends_list=legends_list,
                                      title=f'{self.metric}_qp{self.quality}') as fig:

                    for n, self.tiling in enumerate(self.tiling_list, 1):
                        print(f'\r\tPlot {self.metric} qp{self.quality}_{self.tiling}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'{self.tiling}',
                                               xticklabels=ticks_position,
                                               ) as ax:

                            for pos, self.name in enumerate(self.name_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.violinplot(chunk_data, positions=[pos], widths=0.8, showmeans=False, showmedians=True)

    def make_violinplot_tiling_quality_name(self):
        print(f'make_violinplot_tiling_quality_name.')

        ticks_position = list(range(1, len(self.name_list) + 1))
        legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, self.name_list)]

        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                self.filename = (self.violinplot_folder / f'metric_tiling_quality_name' /
                                 f'violinplot_{self.metric}_{self.tiling}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(14, 6), dpi=300, layout="constrained",
                                      legends_list=legends_list,
                                      title=f'{self.metric}_{self.tiling}') as fig:

                    for n, self.quality in enumerate(self.quality_list, 1):
                        print(f'\r\tPlot {self.metric} {self.quality}_{self.tiling}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=f'qp{self.quality}',
                                               xticklabels=ticks_position,
                                               ) as ax:

                            for pos, self.name in enumerate(self.name_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality'))
                                ax.violinplot(chunk_data, positions=[pos], widths=0.8, showmeans=False, showmedians=True)

    @contextmanager
    def make_figure(self, figsize=(14, 6), dpi=300, layout="constrained", legends_list=None,
                    title=None):
        fig: plt.Figure = plt.figure(figsize=figsize, dpi=dpi, layout=layout)
        try:
            yield fig
        finally:
            pass
        print(f'\n\tSaving.')
        if legends_list is not None:
            legend = fig.legend(legends_list,
                                loc='outside right center',
                                handlelength=0, handletextpad=0)

            for handler in legend.legend_handles:
                handler.set_visible(False)

        if title is not None:
            fig.suptitle(title)
        # fig.show()
        fig.savefig(self.filename)
        fig.clf()
        plt.close()

    @contextmanager
    def make_subplot(self, fig, nrows: int, ncols: int, index: int,
                     title=None, xlabel=None,
                     xticklabels=None, legends_list=None):
        ax: plt.Axes = fig.add_subplot(nrows, ncols, index)
        try:
            yield ax
        finally:
            pass

        if legends_list is not None:
            ax.legend(legends_list, loc='top right', handlelength=0, handletextpad=0)
        if title is not None:
            ax.set_title(title)
        if xticklabels is not None:
            ax.set_xticklabels(xticklabels)
        if xlabel is not None:
            ax.set_xlabel(xlabel)

        ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
        if self.metric == 'dash_m4s':
            ax.ticklabel_format(axis='y', style='scientific',
                                scilimits=(6, 6))

    def make_barplot_quality_tiling_name(self):
        print(f'make_barplot_quality_tiling_name.')

        ticks_position = list(range(1, len(self.name_list) + 1))
        legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, self.name_list)]

        for self.metric in self.dataset_structure:
            self.load_database()
            for self.quality in self.quality_list:
                self.filename = (self.barplot_folder / f'metric_quality_tiling_name' /
                                 f'barplot_tiling_name_{self.metric}_qp{self.quality}.pdf')
                if self.check_filename(): continue

                with self.make_figure(figsize=(14, 6), dpi=300, layout="constrained",
                                      legends_list=legends_list,
                                      title=f'{self.metric}_qp{self.quality}',
                                      hide_legend_handles=True) as fig:
                    for n, self.tiling in enumerate(self.tiling_list, 1):
                        print(f'\r\tPlot {self.metric} {self.quality}_{self.tiling}', end='')
                        with self.make_subplot(fig, 3, 2, n, title=self.tiling) as ax:
                            for pos, self.name in enumerate(self.name_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality')).mean()
                                ax.bar(pos, chunk_data, color='#1f77b4')

    def make_barplot_tiling_quality_name(self):
        print(f'make_barplot_tiling_quality_name.')
        ticks_position = list(range(1, len(self.name_list) + 1))
        legends_list = [f'{pos}-{name}' for pos, name in zip(ticks_position, self.name_list)]
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.tiling in self.tiling_list:
                self.filename = self.barplot_folder / f'metric_tiling_quality_name' / f'barplot_tiling_quality_{self.metric}_{self.name}.pdf'
                if self.check_filename(): continue
                with self.make_figure(figsize=(14, 6), dpi=300, layout="constrained",
                                      legends_list=legends_list,
                                      title=f'{self.metric}_{self.quality}',
                                      ) as fig:
                    for n, self.quality in enumerate(self.quality_list, 1):
                        print(f'\r\tPlot {self.metric} {self.tiling}_{self.quality}', end='')
                        with self.make_subplot(fig, 3, 2, n,
                                               title=self.tiling,
                                               xlabel=None,
                                               legends_list=None,
                                               xticklabels=list(range(1, len(self.name_list) + 1))) as ax:
                            for pos, self.name in enumerate(self.name_list):
                                chunk_data = self.get_chunk_data(levels=('name', 'tiling', 'quality')).mean()
                                ax.bar(pos, chunk_data, color='#1f77b4')


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisNameTilingQuality(config)
