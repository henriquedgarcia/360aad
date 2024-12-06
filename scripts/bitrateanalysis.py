"""
# Bitrate Structure

`bitrate[name][projection][tiling][tile][quality][chunk]['dash_m4s']: int`

or

`bitrate[name][projection][tiling][tile][quality]['dash_init']: int`

or

`bitrate[name][projection][tiling][tile]['dash_mpd']: int`
"""
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.config import Config
from scripts.utils import Bucket, save_json, ProgressBar

# Config
config = Config()
database_path = Path('dataset/bitrate')


class BitrateAnalysis:
    def __init__(self):
        GeneralAnalysis()
        ByQuality()
        ByTiling()
        ByTilingByQuality()


class GeneralAnalysis:
    bucket: Bucket
    stats_df: pd.DataFrame

    def __init__(self):
        self.fill_bucket()
        self.make_table()
        self.make_plots()

    ui: ProgressBar

    def fill_bucket(self):
        self.bucket = Bucket(config)

        if self.bucket_json.exists():
            self.bucket.set_bucket(self.bucket_json)
            return

        self.ui = ProgressBar(28 * 181 * 6, self.class_name)
        for config.name in config.name_list:
            self.bucket.set_database(self.video_json)

            for config.projection in config.projection_list:
                for config.tiling in config.tiling_list:
                    for config.tile in config.get_tile_list(config.tiling):
                        self.bucket.set_value(metric='dash_mpd')
                        for config.quality in config.quality_list:
                            self.ui.update(f'{self}')
                            self.bucket.set_value(metric='dash_init')
                            for config.chunk in config.chunk_list:
                                self.bucket.set_value(metric='dash_m4s')
        self.save_bucket()

    def save_bucket(self):
        bucket = self.bucket.get_bucket()
        save_json(bucket, self.bucket_json)

    def __str__(self):
        return f'{config.name} - {config.tiling} - tile{config.tile} - QP{config.quality}'

    def make_table(self):
        stats_defaultdict = defaultdict(list)

        stats_defaultdict['Nome'].append('MPD')
        stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_mpd']))
        stats_defaultdict['Média'].append(np.average(self.bucket['dash_mpd']))
        stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_mpd']))
        stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_mpd'], 0))
        stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_mpd'], 0.25))
        stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_mpd'], 0.5))
        stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_mpd'], 0.75))
        stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_mpd'], 1))

        stats_defaultdict['Nome'].append('Init')
        stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_init']))
        stats_defaultdict['Média'].append(np.average(self.bucket['dash_init']))
        stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_init']))
        stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_init'], 0))
        stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_init'], 0.25))
        stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_init'], 0.5))
        stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_init'], 0.75))
        stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_init'], 1))

        stats_defaultdict['Nome'].append('m4s')
        stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_m4s']))
        stats_defaultdict['Média'].append(np.average(self.bucket['dash_m4s']))
        stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_m4s']))
        stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_m4s'], 0))
        stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_m4s'], 0.25))
        stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_m4s'], 0.5))
        stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_m4s'], 0.75))
        stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_m4s'], 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.bitrate_stats_csv, index=False)

    def make_plots(self):
        self.make_boxplot()
        self.make_hist()

    def make_boxplot(self):
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        ax1.boxplot(self.bucket['dash_mpd'], whis=(0, 100))
        ax1.title.set_text('Arquivo mpd')
        ax2.boxplot(self.bucket['dash_init'], whis=(0, 100))
        ax2.title.set_text('Arquivo init')
        ax3.boxplot(self.bucket['dash_m4s'], whis=(0, 100))
        ax3.title.set_text('Arquivo m4s')
        fig.tight_layout()
        fig: plt.Figure
        fig.savefig(self.bitrate_boxplot_path)

    def make_hist(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        ax1.hist(self.bucket['dash_mpd'], bins=30)
        ax1.set_title('MPD')
        ax2.hist(self.bucket['dash_init'], bins=30)
        ax2.set_title('Init')
        ax3.hist(self.bucket['dash_m4s'], bins=30)
        ax3.set_title('chunk')
        fig.tight_layout()
        fig.savefig(self.bitrate_hist_path)

    @property
    def graphs_workfolder(self):
        folder = Path(f'graphs/bitrate/{self.class_name}/')
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def stats_workfolder(self):
        folder = Path(f'stats/bitrate/{self.class_name}/')
        folder.mkdir(exist_ok=True, parents=True)
        return folder

    @property
    def bucket_workfolder(self):
        return self.stats_workfolder

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def bitrate_boxplot_path(self):
        return self.graphs_workfolder / 'boxplot.png'

    @property
    def bitrate_hist_path(self):
        return self.graphs_workfolder / 'histogram.png'

    @property
    def bitrate_stats_csv(self):
        return self.stats_workfolder / 'stats.csv'

    @property
    def bucket_json(self):
        return self.bucket_workfolder / 'bucket.json'

    @property
    def video_json(self):
        return database_path / f'bitrate_{config.name}.json'


class ByQuality(GeneralAnalysis):
    def fill_bucket(self):
        self.bucket = Bucket(config)

        if self.bucket_json.exists():
            self.bucket.set_bucket(self.bucket_json)
            return

        self.ui = ProgressBar(28 * 181 * 6, self.class_name)
        for config.name in config.name_list:
            self.bucket.set_database(self.video_json)

            for config.projection in config.projection_list:
                for config.tiling in config.tiling_list:
                    for config.tile in config.get_tile_list(config.tiling):
                        for config.quality in config.quality_list:
                            self.ui.update(f'{self}')
                            self.bucket.set_value(metric='dash_init', quality=config.quality)
                            for config.chunk in config.chunk_list:
                                self.bucket.set_value(metric='dash_m4s', quality=config.quality)

        self.save_bucket()

    def make_table(self):
        if self.bitrate_stats_csv.exists():
            return

        stats_defaultdict = defaultdict(list)
        for config.quality in config.quality_list:

            metrics = ['dash_init', 'dash_m4s']
            for metric in metrics:
                samples = self.bucket.get_bucket([metric, config.quality])
                stats_defaultdict['Nome'].append(metric)
                stats_defaultdict['Quality'].append(config.quality)
                stats_defaultdict['n_arquivos'].append(len(samples))
                stats_defaultdict['Média'].append(np.average(samples))
                stats_defaultdict['Desvio Padrão'].append(np.std(samples))
                stats_defaultdict['Mínimo'].append(np.quantile(samples, 0))
                stats_defaultdict['1º Quartil'].append(np.quantile(samples, 0.25))
                stats_defaultdict['Mediana'].append(np.quantile(samples, 0.5))
                stats_defaultdict['3º Quartil'].append(np.quantile(samples, 0.75))
                stats_defaultdict['Máximo'].append(np.quantile(samples, 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.bitrate_stats_csv, index=False)

    def make_boxplot(self):
        if not self.bitrate_boxplot_path.exists():
            fig, ax = plt.subplots(1, 2, figsize=(10, 5))
            fig: plt.Figure
            ax: list[plt.Axes]
            legends = []
            for n, quality in enumerate(config.quality_list):
                ax[0].boxplot(self.bucket['dash_init'][quality], whis=(0, 100), positions=[n])
                ax[1].boxplot(self.bucket['dash_m4s'][quality], whis=(0, 100), positions=[n])
            ax[0].title.set_text('Arquivo ini')
            ax[1].title.set_text('Arquivo m4s')
            ax[1].legend(legends)
            ax[0].set_xticklabels(config.quality_list)
            ax[1].set_xticklabels(config.quality_list)
            ax[0].ticklabel_format(axis='y', style='scientific')
            ax[1].ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
            ax[0].set_xlabel('QP')
            ax[1].set_xlabel('QP')
            ax[0].set_ylabel('Bitrate (bps)')
            ax[1].set_ylabel('Bitrate (Mbps)')
            fig.tight_layout()
            fig.savefig(self.bitrate_boxplot_path)

        if not self.bitrate_boxplot_path1.exists():
            fig1 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, quality in enumerate(config.quality_list):
                ax1 = fig1.add_subplot(1, 6, n+1)
                ax1.boxplot(self.bucket['dash_init'][quality], whis=(0, 100), positions=[n])
                ax1.title.set_text('Arquivo ini')
                ax1.set_xticklabels([quality])
                ax1.ticklabel_format(axis='y', style='scientific')
                ax1.set_xlabel('QP')
                ax1.set_ylabel('Bitrate (bps)')

            fig1.savefig(self.bitrate_boxplot_path1)

        if not self.bitrate_boxplot_path2.exists():
            fig2 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, quality in enumerate(config.quality_list):
                ax2 = fig2.add_subplot(1, 6, n+1)
                ax2.boxplot(self.bucket['dash_m4s'][quality], whis=(0, 100), positions=[n])
                ax2.title.set_text('Arquivo m4s')
                ax2.set_xticklabels([quality])
                ax2.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax2.set_xlabel('QP')
                ax2.set_ylabel('Bitrate (bps)')

            fig2.savefig(self.bitrate_boxplot_path2)

    def make_hist(self):
        if self.bitrate_hist_path.exists():
            return
        fig: plt.Figure
        ax: plt.Axes
        for n, config.quality in enumerate(config.quality_list):
            fig = plt.figure(dpi=600, linewidth=0.5, tight_layout=True)
            ax = fig.add_subplot(1, 1, 1)

            ax.hist(self.bucket['dash_m4s'][config.quality], bins=30)

            ax.set_xlabel('Bitrate (Mbps)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'QP{config.quality}')
            ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            fig.suptitle('dash_m4s')
            fig.savefig(self.bitrate_hist_path)

    @property
    def bitrate_boxplot_path(self):
        return self.graphs_workfolder / 'boxplot.pdf'

    @property
    def bitrate_boxplot_path1(self):
        return self.graphs_workfolder / 'boxplot_ini.pdf'

    @property
    def bitrate_boxplot_path2(self):
        return self.graphs_workfolder / 'boxplot_m4s.pdf'

    @property
    def bitrate_hist_path(self):
        return self.graphs_workfolder / f'histogram_qp{config.quality}.pdf'


class ByTiling(GeneralAnalysis):
    def fill_bucket(self):
        self.bucket = Bucket(config)

        if self.bucket_json.exists():
            self.bucket.set_bucket(self.bucket_json)
            return

        self.ui = ProgressBar(28 * 181 * len(config.tiling_list), self.class_name)
        for config.name in config.name_list:
            self.bucket.set_database(self.video_json)

            for config.projection in config.projection_list:
                for config.tiling in config.tiling_list:
                    for config.tile in config.get_tile_list(config.tiling):
                        for config.quality in config.quality_list:
                            self.ui.update(f'{self}')
                            self.bucket.set_value(metric='dash_init', tiling=config.tiling)
                            for config.chunk in config.chunk_list:
                                self.bucket.set_value(metric='dash_m4s', tiling=config.tiling)

        self.save_bucket()

    def make_table(self):
        if self.bitrate_stats_csv.exists():
            return
        stats_defaultdict = defaultdict(list)

        for config.tiling in config.tiling_list:

            metrics = ['dash_init', 'dash_m4s']
            for metric in metrics:
                samples = self.bucket.get_bucket([metric, config.tiling])
                stats_defaultdict['Nome'].append(metric)
                stats_defaultdict['Tiling'].append(config.tiling)
                stats_defaultdict['n_arquivos'].append(len(samples))
                stats_defaultdict['Média'].append(np.average(samples))
                stats_defaultdict['Desvio Padrão'].append(np.std(samples))
                stats_defaultdict['Mínimo'].append(np.quantile(samples, 0))
                stats_defaultdict['1º Quartil'].append(np.quantile(samples, 0.25))
                stats_defaultdict['Mediana'].append(np.quantile(samples, 0.5))
                stats_defaultdict['3º Quartil'].append(np.quantile(samples, 0.75))
                stats_defaultdict['Máximo'].append(np.quantile(samples, 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.bitrate_stats_csv, index=False)

    def make_boxplot(self):
        if not self.bitrate_boxplot_path.exists():
            fig, ax = plt.subplots(1, 2, figsize=(10, 5))
            fig: plt.Figure
            ax: list[plt.Axes]
            legends = []
            for n, tiling in enumerate(config.tiling_list):
                ax[0].boxplot(self.bucket['dash_init'][tiling], whis=(0, 100), positions=[n])
                ax[1].boxplot(self.bucket['dash_m4s'][tiling], whis=(0, 100), positions=[n])
            ax[0].title.set_text('Arquivo ini')
            ax[1].title.set_text('Arquivo m4s')
            ax[1].legend(legends)
            ax[0].set_xticklabels(config.tiling_list)
            ax[1].set_xticklabels(config.tiling_list)
            ax[0].ticklabel_format(axis='y', style='scientific')
            ax[1].ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
            ax[0].set_xlabel('QP')
            ax[1].set_xlabel('QP')
            ax[0].set_ylabel('Bitrate (bps)')
            ax[1].set_ylabel('Bitrate (Mbps)')
            fig.tight_layout()
            fig.savefig(self.bitrate_boxplot_path)

        if not self.bitrate_boxplot_path1.exists():
            fig1 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, tiling in enumerate(config.tiling_list):
                ax1 = fig1.add_subplot(1, 6, n+1)
                ax1.boxplot(self.bucket['dash_init'][tiling], whis=(0, 100), positions=[n])
                ax1.title.set_text('Arquivo ini')
                ax1.set_xticklabels([tiling])
                ax1.ticklabel_format(axis='y', style='scientific')
                ax1.set_xlabel('QP')
                ax1.set_ylabel('Bitrate (bps)')

            fig1.savefig(self.bitrate_boxplot_path1)

        if not self.bitrate_boxplot_path2.exists():
            fig2 = plt.figure(figsize=(11, 3), dpi=600, linewidth=0.5, tight_layout=True)

            for n, tiling in enumerate(config.tiling_list):
                ax2 = fig2.add_subplot(1, 6, n+1)
                ax2.boxplot(self.bucket['dash_m4s'][tiling], whis=(0, 100), positions=[n])
                ax2.title.set_text('Arquivo m4s')
                ax2.set_xticklabels([tiling])
                ax2.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax2.set_xlabel('QP')
                ax2.set_ylabel('Bitrate (bps)')

            fig2.savefig(self.bitrate_boxplot_path2)

    def make_hist(self):
        if self.bitrate_hist_path.exists():
            return
        fig: plt.Figure
        ax: plt.Axes
        for n, tiling in enumerate(config.tiling_list):
            fig = plt.figure(dpi=600, linewidth=0.5, tight_layout=True)
            ax = fig.add_subplot(1, 1, 1)

            ax.hist(self.bucket['dash_m4s'][tiling], bins=30)

            ax.set_xlabel('Bitrate (Mbps)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'{tiling}')
            ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            fig.suptitle('dash_m4s')
            fig.savefig(self.bitrate_hist_path)

    @property
    def bitrate_boxplot_path(self):
        return self.graphs_workfolder / 'boxplot.pdf'

    @property
    def bitrate_boxplot_path1(self):
        return self.graphs_workfolder / 'boxplot_ini.pdf'

    @property
    def bitrate_boxplot_path2(self):
        return self.graphs_workfolder / 'boxplot_m4s.pdf'

    @property
    def bitrate_hist_path(self):
        return self.graphs_workfolder / f'histogram_qp{config.tiling}.pdf'


class ByTilingByQuality(GeneralAnalysis):
    def fill_bucket(self):
        self.bucket = Bucket(config)

        if self.bucket_json.exists():
            self.bucket.set_bucket(self.bucket_json)
            return

        self.ui = ProgressBar(28 * 181 * len(config.tiling_list), self.class_name)
        for config.name in config.name_list:
            self.bucket.set_database(self.video_json)

            for config.projection in config.projection_list:
                for config.tiling in config.tiling_list:
                    for config.tile in config.get_tile_list(config.tiling):
                        for config.quality in config.quality_list:
                            self.ui.update(f'{self}')
                            self.bucket.set_value(metric='dash_init', tiling=config.tiling, quality=config.quality)
                            for config.chunk in config.chunk_list:
                                self.bucket.set_value(metric='dash_m4s', tiling=config.tiling, quality=config.quality)

        self.save_bucket()

    def make_table(self):
        if self.bitrate_stats_csv.exists():
            return

        metrics = ['dash_init', 'dash_m4s']
        stats_defaultdict = defaultdict(list)

        for metric in metrics:
            for config.tiling in config.tiling_list:
                for config.quality in config.quality_list:
                    samples = self.bucket[metric][config.tiling][config.quality]
                    stats_defaultdict['Nome'].append(metric)
                    stats_defaultdict['Tiling'].append(config.tiling)
                    stats_defaultdict['Quality'].append(config.quality)
                    stats_defaultdict['n_arquivos'].append(len(samples))
                    stats_defaultdict['Média'].append(np.average(samples))
                    stats_defaultdict['Desvio Padrão'].append(np.std(samples))
                    stats_defaultdict['Mínimo'].append(np.quantile(samples, 0))
                    stats_defaultdict['1º Quartil'].append(np.quantile(samples, 0.25))
                    stats_defaultdict['Mediana'].append(np.quantile(samples, 0.5))
                    stats_defaultdict['3º Quartil'].append(np.quantile(samples, 0.75))
                    stats_defaultdict['Máximo'].append(np.quantile(samples, 1))

        self.stats_df: pd.DataFrame = pd.DataFrame(stats_defaultdict)
        self.stats_df.to_csv(self.bitrate_stats_csv, index=False)

    def make_boxplot(self):
        if not self.bitrate_boxplot_path1.exists():
            for config.tiling in config.tiling_list:
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, config.quality in enumerate(config.quality_list):
                    ax.boxplot(self.bucket['dash_init'][config.tiling][config.quality], whis=(0, 100), positions=[n])

                ax.title.set_text('Arquivo ini')
                ax.set_xticklabels(config.quality_list)
                ax.ticklabel_format(axis='y', style='scientific')
                ax.set_xlabel('QP')
                ax.set_ylabel('Bitrate (bps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path1)

        if not self.bitrate_boxplot_path2.exists():
            for config.tiling in config.tiling_list:
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, config.quality in enumerate(config.quality_list):
                    ax.boxplot(self.bucket['dash_m4s'][config.tiling][config.quality], whis=(0, 100), positions=[n])
                ax.title.set_text('Arquivo m4s')
                ax.set_xticklabels(config.quality_list)
                ax.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax.set_xlabel('QP')
                ax.set_ylabel('Bitrate (Mbps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path2)

        if not self.bitrate_boxplot_path3.exists():
            for config.quality in config.quality_list:
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, config.tiling in enumerate(config.tiling_list):
                    ax.boxplot(self.bucket['dash_init'][config.tiling][config.quality], whis=(0, 100), positions=[n])
                ax.title.set_text('Arquivo ini')
                ax.set_xticklabels(config.tiling_list)
                ax.ticklabel_format(axis='y', style='scientific')
                ax.set_xlabel('Tiling')
                ax.set_ylabel('Bitrate (bps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path3)

        if not self.bitrate_boxplot_path4.exists():
            for config.quality in config.quality_list:
                fig, ax = plt.subplots(1, 1)
                fig: plt.Figure
                ax: plt.Axes

                for n, config.tiling in enumerate(config.tiling_list):
                    ax.boxplot(self.bucket['dash_m4s'][config.tiling][config.quality], whis=(0, 100), positions=[n])
                ax.title.set_text('Arquivo m4s')
                ax.set_xticklabels(config.tiling_list)
                ax.ticklabel_format(axis='y', style='scientific', scilimits=(6, 6))
                ax.set_xlabel('Tiling')
                ax.set_ylabel('Bitrate (Mbps)')
                fig.tight_layout()
                fig.savefig(self.bitrate_boxplot_path4)

    def make_hist(self):
        if self.bitrate_hist_path.exists():
            return

        fig: plt.Figure
        ax: plt.Axes
        for n, quality in enumerate(config.quality_list):
            fig = plt.figure(dpi=600, linewidth=0.5, tight_layout=True)
            ax = fig.add_subplot(1, 1, 1)

            ax.hist(self.bucket['dash_m4s'][quality], bins=30)

            ax.set_xlabel('Bitrate (Mbps)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'QP{quality}')
            ax.ticklabel_format(axis='x', style='scientific', scilimits=(6, 6))

            fig.suptitle('dash_m4s')
            fig.savefig(self.bitrate_hist_path)

    @property
    def bitrate_boxplot_path1(self):
        return self.graphs_workfolder / f'boxplot_ini_{config.tiling}.pdf'

    @property
    def bitrate_boxplot_path2(self):
        return self.graphs_workfolder / f'boxplot_m4s_{config.tiling}.pdf'

    @property
    def bitrate_boxplot_path3(self):
        return self.graphs_workfolder / f'boxplot_ini_{config.quality}.pdf'

    @property
    def bitrate_boxplot_path4(self):
        return self.graphs_workfolder / f'boxplot_m4s_{config.quality}.pdf'

    @property
    def bitrate_hist_path(self):
        return self.graphs_workfolder / f'histogram_qp{config.tiling}.pdf'
