import asyncio
import os
from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from scripts.analysisbase import AnalysisBase
from scripts.config import Config
from scripts.utils import AutoDict

lock = asyncio.Lock()


class ChunkAnalysisQuality(AnalysisBase):
    def setup(self):
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'
        del self.dataset_structure['dash_mpd']
        del self.dataset_structure['dash_init']
        del self.dataset_structure['dectime_std']

    def make_stats(self):
        print(f'make_stats')
        self.stats_defaultdict = defaultdict(list)
        for self.metric in self.dataset_structure:
            self.load_database()
            for self.quality in self.quality_list:
                bucket = list(self.database.xs(self.quality, level='quality')['value'])

                self.stats_defaultdict['Metric'].append(self.metric)
                self.stats_defaultdict['Quality'].append(self.quality)
                self.stats_defaultdict['n_arquivos'].append(len(bucket))
                self.stats_defaultdict['Média'].append(np.average(bucket))
                self.stats_defaultdict['Desvio Padrão'].append(np.std(bucket))
                self.stats_defaultdict['Mínimo'].append(np.quantile(bucket, 0))
                self.stats_defaultdict['1º Quartil'].append(np.quantile(bucket, 0.25))
                self.stats_defaultdict['Mediana'].append(np.quantile(bucket, 0.5))
                self.stats_defaultdict['3º Quartil'].append(np.quantile(bucket, 0.75))
                self.stats_defaultdict['Máximo'].append(np.quantile(bucket, 1))

    def plots(self):
        self.make_boxplot1()

    def make_boxplot1(self):
        print(f'Boxplot 1.')
        for self.metric in self.dataset_structure:
            boxplot_path_tiling = self.boxplot_folder / f'boxplot_{self.metric}.png'
            # if boxplot_path_tiling.exists():
            #     print(f'\t{boxplot_path_tiling} exists.')
            #     continue

            self.load_database()

            fig = plt.figure(figsize=(6, 2.4), layout='tight')
            fig.suptitle(f'{self.metric}')
            ax: plt.Axes = fig.add_subplot(1, 1, 1)

            print(f'Making bucket')
            buckets = []
            for self.quality in self.quality_list:
                bucket = list(self.database.xs(self.quality, level='quality')['value'])
                buckets.append(bucket)

            ax.violinplot(buckets, showmeans=False, showmedians=True)
            ax.set_xticks(list(range(1, len(self.quality_list) + 1)),
                          list(self.quality_list))
            ax.set_xlabel(f'Quality (QP)')
            ax.set_ylabel(self.dataset_structure[self.metric]['quantity'])
            fig.savefig(boxplot_path_tiling)
            fig.clf()

# class GetTilesChunkGeneralAnalysis(AnalysisBase):
#     def main(self):
#         self.metric = 'get_tiles'
#         self.categories = ['frame', 'chunk']
#         self.category = 'chunks'
#
#         self.database = database_factory(self.metric, self.config)
#
#         # self.plot_n_tiles_by_name_tiling_user_chunk()
#         self.stats_n_tiles_by_name_tiling_user_chunk()
#         # self.make_table()
#         # self.make_boxplot()
#         # self.make_hist()
#
#     def plot_n_tiles_by_name_tiling_user_chunk(self):
#         """
#         Compare users
#         name_tiling = filename
#         user = plot
#         chunk = x axis
#         n_tiles = len(seen_tiles by chunk)
#         """
#         file_name = lambda: Path(f'graphs/GetTiles/n_tiles_by_name_tiling_user_chunk/'
#                                  f'{self.name}_{self.tiling}.png')
#
#         for self.name in self.name_list:
#             self.database.load(self.database_json)
#             for self.tiling in self.tiling_list:
#                 file = file_name()
#                 if file.exists(): continue
#
#                 fig = plt.figure()
#                 ax = fig.add_subplot(1, 1, 1)
#                 get_tiles_values_array = np.zeros((len(self.users_list), len(self.chunk_list)))
#                 for n, self.user in enumerate(self.users_list):
#                     get_tiles_values = []
#                     for self.chunk in self.chunk_list:
#                         value = self.database.get_value()
#                         size = len(value)
#                         get_tiles_values.append(size)
#                     ax.plot(get_tiles_values)
#                     get_tiles_values_array[n] = get_tiles_values
#                 ax.plot(np.average(get_tiles_values_array, axis=0), label=f'user{self.user}')
#                 ax.set_title(f'Users by {self.tiling}')
#                 ax.set_xlabel(f'Chunks')
#                 ax.set_ylabel(f'n. tiles')
#                 fig.suptitle(f'{self.name}')
#                 fig.tight_layout()
#                 # fig.show()
#                 file.parent.mkdir(parents=True, exist_ok=True)
#                 fig.savefig(file)
#                 plt.close(fig)
#
#     def stats_n_tiles_by_name_tiling_user_chunk(self):
#         """
#         Compare users
#         name_tiling = filename
#         user = plot
#         chunk = x axis
#         n_tiles = len(seen_tiles by chunk)
#         """
#         file = Path(f'stats/GetTiles/n_tiles_by_name_tiling_user_chunk/stats.csv')
#         if file.exists(): return
#
#         table = defaultdict(list)
#         for self.name in self.name_list:
#             self.database.load(self.database_json)
#             for self.tiling in self.tiling_list:
#                 for n, self.user in enumerate(self.users_list):
#                     n_tiles_seen_list = []
#                     for self.chunk in self.chunk_list:
#                         n_tiles_seen = len(self.database.get_value())
#                         n_tiles_seen_list.append(n_tiles_seen)
#
#                     table['name'].append(self.name)
#                     table['tiling'].append(self.tiling)
#                     table['user'].append(self.user)
#                     table['avg'].append(np.average(n_tiles_seen_list))
#                     table['std'].append(np.std(n_tiles_seen_list))
#                     table['min'].append(np.min(n_tiles_seen_list))
#                     table['med'].append(np.median(n_tiles_seen_list))
#                     table['max'].append(np.max(n_tiles_seen_list))
#
#         file.parent.mkdir(parents=True, exist_ok=True)
#         pd.DataFrame(table).to_csv(file)
#
#         table1 = defaultdict(list)
#         for user in set(table['user']):
#             df_filtrado = table[table['user'] == user]
#             table1['user'].append(user)
#             table1['avg'].append(df_filtrado["avg"].mean())
#             table1['std'].append(df_filtrado["avg"].std())
#         file = Path(f'stats/GetTiles/n_tiles_by_name_tiling_user_chunk/stats_user.csv')
#         pd.DataFrame(table1).to_csv(file)
#
#     @LazyProperty
#     def n_tiles_for_plot_by_tiling_user_chunk(self):
#         """ Compara usuários por tiling """
#         my_dict = AutoDict()
#         for self.tiling in self.tiling_list:
#             for self.user in self.users_list:
#                 my_dict[self.tiling][self.user] = defaultdict(list)
#
#     @LazyProperty
#     def n_tiles_for_plot_by_name_tiling_chunk(self):
#         """ Compara vídeos """
#         my_dict = AutoDict()
#         for self.name in self.name_list:
#             for self.tiling in self.tiling_list:
#                 my_dict[self.name][self.tiling] = defaultdict(list)
#
#     @LazyProperty
#     def n_tiles_for_plot_by_tiling(self):
#         """ Compara tiling """
#         my_dict = AutoDict()
#         for self.tiling in self.tiling_list:
#             my_dict[self.tiling] = defaultdict(list)
#
#     def make_bucket(self):
#         data_heatmap_by_tiling = AutoDict()
#         for self.tiling in self.tiling_list:
#             for self.tile in self.tile_list:
#                 data_heatmap_by_tiling[self.tiling][self.tile] = 0
#
#         data_heatmap_by_name_tiling = AutoDict()
#         for self.name in self.name_list:
#             for self.tiling in self.tiling_list:
#                 for self.tile in self.tile_list:
#                     data_heatmap_by_name_tiling[self.name][self.tiling][self.tile] = 0
#
#         self.ui = ProgressBar(28 * 181, str(['make_bucket'] + self.bucket_keys_name))
#         for self.name in self.name_list:
#             for self.tiling in self.tiling_list:
#                 count_tiles_seen_by_name_tiling = Counter()
#
#                 for self.user in self.users_list:
#                     self.ui.update(f'{self}')
#
#                     count_tiles_seen_by_name_tiling_user = \
#                         {tile: 0 for tile in self.tile_list}
#
#                     for self.chunk in self.chunk_list:
#                         # get value
#                         get_tiles_value = self.database.get_value()
#
#                         # add in bucket
#                         keys = ['tiles_seen']
#                         self.bucket.set_bucket_value(get_tiles_value, keys)
#
#                         # count tiles seen
#                         for tile in get_tiles_value:
#                             count_tiles_seen_by_name_tiling_user[tile] += 1
#                     else:
#                         self.chunk = None
#
#                     keys = ['c_por_tiling']
#                     self.bucket.set_bucket_value(self.database.get_value(), keys)
#
#     def make_table(self):
#         if self.stats_csv.exists(): return
#
#         print(f'Calculating stats.')
#         self.stats_defaultdict = defaultdict(list)
#         for cat in self.categories:
#             self.stats_defaultdict['Nome'].append(cat)
#             self.stats_defaultdict['n_arquivos'].append(len(self.bucket[cat]))
#             self.stats_defaultdict['Média'].append(np.average(self.bucket[cat]))
#             self.stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket[cat]))
#             self.stats_defaultdict['Mínimo'].append(np.quantile(self.bucket[cat], 0))
#             self.stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket[cat], 0.25))
#             self.stats_defaultdict['Mediana'].append(np.quantile(self.bucket[cat], 0.5))
#             self.stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket[cat], 0.75))
#             self.stats_defaultdict['Máximo'].append(np.quantile(self.bucket[cat], 1))
#
#         self.stats_df: pd.DataFrame = pd.DataFrame(self.stats_defaultdict)
#         self.stats_df.to_csv(self.stats_csv, index=False)
#
#     def make_boxplot(self):
#         if self.boxplot_path.exists(): return
#         print(f'Boxplot 1.')
#
#         fig = plt.Figure((3, 9))
#         for n, cat in enumerate(self.categories):
#             ax = fig.add_subplot(1, len(self.categories), n + 1)
#             ax.boxplot(self.bucket[cat], whis=(0, 100))
#             ax.set_title(cat)
#         fig.tight_layout()
#         fig.savefig(self.boxplot_path)
#         fig.clf()
#
#     def make_hist(self):
#         if self.hist_path.exists(): return
#         print(f'Histogram 1.')
#         fig = plt.Figure((10, 3))
#         for n, cat in enumerate(self.categories):
#             ax1 = fig.add_subplot(1, len(self.categories), n + 1)
#             ax1.hist(self.bucket[cat], bins=30)
#             ax1.set_title(cat)
#         fig.tight_layout()
#         fig.savefig(self.hist_path)
#         fig.clf()


if __name__ == '__main__':
    os.chdir('../')

    config = Config()
    ChunkAnalysisQuality(config)
