import asyncio
from collections import defaultdict

import numpy as np

from scripts.analysisbase import AnalysisBase
from scripts.utils import AutoDict

lock = asyncio.Lock()


class ChunkAnalysisGeneralBitrate(AnalysisBase):
    def setup(self):
        self.metric = 'bitrate'
        self.categories = ('dash_mpd', 'dash_init', 'dash_m4s')
        self.bucket_keys_name = ()
        self.database_keys = {'dash_mpd': ['name', 'projection', 'tiling', 'tile'],
                              'dash_init': ['name', 'projection', 'tiling', 'tile', 'quality'],
                              'dash_m4s': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']}
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_bucket(self):
        """
        metric, categories, keys_orders
        """
        print(f'make_bucket')
        self.make_dash_mpd_bucket()
        self.make_dash_init_bucket()
        self.make_dash_m4s_bucket()

    def make_stats(self):
        self.stats_defaultdict['Nome'].append('MPD')
        self.stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_mpd']))
        self.stats_defaultdict['Média'].append(np.average(self.bucket['dash_mpd']))
        self.stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_mpd']))
        self.stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_mpd'], 0))
        self.stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_mpd'], 0.25))
        self.stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_mpd'], 0.5))
        self.stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_mpd'], 0.75))
        self.stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_mpd'], 1))

        self.stats_defaultdict['Nome'].append('Init')
        self.stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_init']))
        self.stats_defaultdict['Média'].append(np.average(self.bucket['dash_init']))
        self.stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_init']))
        self.stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_init'], 0))
        self.stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_init'], 0.25))
        self.stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_init'], 0.5))
        self.stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_init'], 0.75))
        self.stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_init'], 1))

        self.stats_defaultdict['Nome'].append('m4s')
        self.stats_defaultdict['n_arquivos'].append(len(self.bucket['dash_m4s']))
        self.stats_defaultdict['Média'].append(np.average(self.bucket['dash_m4s']))
        self.stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket['dash_m4s']))
        self.stats_defaultdict['Mínimo'].append(np.quantile(self.bucket['dash_m4s'], 0))
        self.stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket['dash_m4s'], 0.25))
        self.stats_defaultdict['Mediana'].append(np.quantile(self.bucket['dash_m4s'], 0.5))
        self.stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket['dash_m4s'], 0.75))
        self.stats_defaultdict['Máximo'].append(np.quantile(self.bucket['dash_m4s'], 1))

    def plots(self):
        pass

    def make_dash_mpd_bucket(self):
        print(f'make_dash_mpd_bucket')
        self.chunk = self.quality = None
        total = 181
        for self.name in self.name_list:
            self.load_database()
            self.start_ui(total, '\t' + self.name)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        self.update_ui(f'{self.tiling}')
                        value = self.get_dataset_value('dash_mpd')
                        self.set_bucket_value(['dash_mpd'], value, )
            self.close_ui()

    def make_dash_init_bucket(self):
        print(f'make_dash_init_bucket')
        self.chunk = None
        for self.name in self.name_list:
            self.load_database()
            total = 181 * len(self.quality_list)
            self.start_ui(total, '\t' + self.name)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        for self.quality in self.quality_list:
                            self.update_ui(f'{self.tiling}_qp{self.quality}')
                            value = self.get_dataset_value('dash_init')
                            self.set_bucket_value(['dash_init'], value, )
            self.close_ui()

    def make_dash_m4s_bucket(self):
        print(f'make_dash_m4s_bucket')
        total = 181 * len(self.quality_list) * len(self.chunk_list)
        for self.name in self.name_list:
            self.load_database()
            self.start_ui(total, '\t' + self.name)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                self.update_ui(f'{self.tiling}_qp{self.quality}')
                                value = self.get_dataset_value('dash_m4s')
                                self.set_bucket_value(['dash_m4s'], value, )
            self.close_ui()


class ChunkAnalysisGeneralTime(AnalysisBase):
    def setup(self):
        self.metric = 'time'
        # self.categories = ('dectime', 'dectime_avg', 'dectime_med', 'dectime_std')
        self.categories = ('dectime_avg', 'dectime_std')
        self.bucket_keys_name = ()
        self.database_keys = {'dectime_avg': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              'dectime_std': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              }
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_bucket(self):
        print(f'make_dectime_bucket')
        total = (181 * len(self.quality_list) * len(self.chunk_list))
        for self.name in self.name_list:
            self.load_database()
            self.start_ui(total, '\t' + self.name)
            for self.tiling in self.tiling_list:
                for self.tile in self.tile_list:
                    for self.quality in self.quality_list:
                        for self.chunk in self.chunk_list:
                            self.update_ui(f'{self.tiling}-{self.tile}_qp{self.quality}')

                            value = self.get_dataset_value('dectime_avg')
                            self.set_bucket_value(['dectime_avg'], value, )

                            value = self.get_dataset_value('dectime_std')
                            self.set_bucket_value(['dectime_std'], value, )
            self.close_ui()

    def make_stats(self):
        print(f'Calculating stats.')
        for cat in self.categories:
            self.stats_defaultdict['Nome'].append(cat)
            self.stats_defaultdict['n_arquivos'].append(len(self.bucket[cat]))
            self.stats_defaultdict['Média'].append(np.average(self.bucket[cat]))
            self.stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket[cat]))
            self.stats_defaultdict['Mínimo'].append(np.quantile(self.bucket[cat], 0))
            self.stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket[cat], 0.25))
            self.stats_defaultdict['Mediana'].append(np.quantile(self.bucket[cat], 0.5))
            self.stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket[cat], 0.75))
            self.stats_defaultdict['Máximo'].append(np.quantile(self.bucket[cat], 1))

    def plots(self):
        ...


class ChunkAnalysisGeneralQuality(AnalysisBase):
    def setup(self):
        self.metric = 'chunk_quality'
        self.categories = ('ssim', 'mse', 's-mse', 'ws-mse')
        self.bucket_keys_name = ()
        self.database_keys = {'ssim': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              'mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              's-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              'ws-mse': ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk'],
                              }
        self.bucket = AutoDict()
        self.stats_defaultdict = defaultdict(list)
        self.projection = 'cmp'

    def make_bucket(self):
        print(f'make_quality_bucket')
        total = (181 * len(self.quality_list) * len(self.chunk_list))
        for self.name in self.name_list:
            self.load_database()
            self.start_ui(total, '\t' + self.name)
            for self.projection in self.projection_list:
                for self.tiling in self.tiling_list:
                    for self.tile in self.tile_list:
                        for self.quality in self.quality_list:
                            for self.chunk in self.chunk_list:
                                self.update_ui(f'{self.tiling}-{self.tile}_qp{self.quality}')

                                for cat in self.categories:
                                    value = self.get_dataset_value(cat)
                                    self.set_bucket_value([cat], value, )
            self.close_ui()

    def make_stats(self):
        print(f'Calculating stats.')
        for cat in self.categories:
            self.stats_defaultdict['Nome'].append(cat)
            self.stats_defaultdict['n_arquivos'].append(len(self.bucket[cat]))
            self.stats_defaultdict['Média'].append(np.average(self.bucket[cat]))
            self.stats_defaultdict['Desvio Padrão'].append(np.std(self.bucket[cat]))
            self.stats_defaultdict['Mínimo'].append(np.quantile(self.bucket[cat], 0))
            self.stats_defaultdict['1º Quartil'].append(np.quantile(self.bucket[cat], 0.25))
            self.stats_defaultdict['Mediana'].append(np.quantile(self.bucket[cat], 0.5))
            self.stats_defaultdict['3º Quartil'].append(np.quantile(self.bucket[cat], 0.75))
            self.stats_defaultdict['Máximo'].append(np.quantile(self.bucket[cat], 1))

    def plots(self):
        """
        Não faz sentido aqui. O desvio padrão é muito grande por
        misturar diferentes qualidades e tiling. Os dados estão muito misturados ainda

        Returns
        -------

        """

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
