import os
from collections import defaultdict

import matplotlib.pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.utils.config import Config


class ChunkAnalysisGeneral(AnalysisBase):
    def setup(self):
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        self.load_database()
        del self.dataset_structure['seen_tiles']

    def make_stats(self):
        for self.metric in self.dataset_structure:
            chunk_data = self.database[self.metric]

            self.stats_defaultdict['Metric'].append(self.metric)
            self.stats_defaultdict['n_arquivos'].append(len(chunk_data))
            self.stats_defaultdict['Média'].append(chunk_data.mean())
            self.stats_defaultdict['Desvio Padrão'].append(chunk_data.std())
            self.stats_defaultdict['Mínimo'].append(chunk_data.quantile(0.00))
            self.stats_defaultdict['1º Quartil'].append(chunk_data.quantile(0.25))
            self.stats_defaultdict['Mediana'].append(chunk_data.quantile(0.50))
            self.stats_defaultdict['3º Quartil'].append(chunk_data.quantile(0.75))
            self.stats_defaultdict['Máximo'].append(chunk_data.quantile(1.00))

    def plots(self):
        # self.hist()
        # self.boxplot()
        self.violinplot()

    def hist(self):
        for bins in range(5, 101, 5):
            fig, axes = plt.subplots(3, 2, figsize=(8, 6), dpi=300)
            for ax, self.metric in zip(axes.flat, self.metric_list):
                chunk_data = self.database[self.metric]
                ax.hist(chunk_data, bins=bins)
                ax.set_title(f'{self.metric}')
                ax.set_yscale('log')
            fig.suptitle(f'{bins} bins')
            fig.tight_layout()
            fig.savefig(f'{self.histogram_folder}/{bins}_bins.pdf')
            plt.close()

    def boxplot(self):
        fig, axes = plt.subplots(1, 6, figsize=(8, 3), dpi=300)
        for ax, self.metric in zip(axes.flat, self.metric_list):
            serie_list = [self.database[self.metric]]
            ax.boxplot(serie_list, tick_labels=[self.metric])
            ax.set_title(f'{self.metric}')
            ax.set_yscale('log')
        fig.tight_layout()
        fig.savefig(f'{self.boxplot_folder}/boxplot.png')
        plt.close()

    def violinplot(self):
        fig, axes = plt.subplots(1, 6, figsize=(8, 3), dpi=300)
        for ax, self.metric in zip(axes.flat, self.metric_list):
            serie_list = [self.database[self.metric]]
            ax.violinplot(serie_list, showmeans=False, showmedians=True)
            ax.set_xticks([1], [self.metric])
            ax.set_title(f'{self.metric}')
            ax.set_yscale('log')
        fig.tight_layout()
        fig.savefig(f'{self.violinplot_folder}/violinplot.png')
        plt.close()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisGeneral(config)
