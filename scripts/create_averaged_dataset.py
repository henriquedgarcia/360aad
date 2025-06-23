import os

import pandas as pd

from scripts.analysisbase import AnalysisPaths
from scripts.utils.config import Config


class CreateAveragedDataset(AnalysisPaths):
    """
    # Análise do movimento de cabeça.
    ## movimento de cabeça (por frame)
        Podemos calcular a velocidade de cada usuário para cada vídeo partindo do repouso v0 = 0 rad/s
            plotar por frame e ver os momentos de maior velocidade (talvez usar um filtro passa baixa para reduzir tremedeira)
        podemos calcular a aceleração pra descobrir momentos que ele fixa atenção (menores acelerações)
        index.names = [name, projection, user, frame]
    """

    """
    # tiles vistos (por frame) → será usado
        calcular numero de tiles vistos por chunk
            index.names = [name, projection, tiling, user, chunk]
    """
    """
    # User session
    index.names = [user, name, projection, tiling, quality, chunk]
    * 
    * Usar tiles_seen
        * bitrate dos tiles vistos (somar todos bitrate)
        * dectime_máximo dos tiles vistos
        * dectime_total dos tiles vistos
        * chunk_quality médio dos tiles vistos (SSIM, MSE, W-MSE, WS-MSE)
        * número de chunks vistos.
        * agrupar viewport quality por chunk

    """

    """
    # chunk quality, dectime, bitrate
        converter chunk quality para chunk (média)
        unificar todos esses.
            index.name = [name, projection, tiling, tile, quality, chunk]
            columns = [bitrate, dectime, ssim, mse, s-mse, ws-mse] (checkar esses hifens)
    """

    """
    # SITI
        não faz nada agora

        boxplot 
            "este boxplot resume como o si e ti se distribuem em cada face para cada vídeo"
            para cada video
                uma figura com dois subplots um pra SI e outro pra TI
                    cada subplot tem seis boxplot, um pra cada face do cubo
        
        plot
            este plot deve mostrar o si e ti ao longo do tempo para todas as faces em cada vídeo. 
            "Isto deve mostrar como cada face tem complexidades diferentes"
        
        Stats
            mostrar as estatísticas de cada tile de cada vídeo
                média e std do si, média e std do ti
            mostrar estatística para cada vídeo
                média das médias dos tiles, std das médias dos tiles
                "isto deve mostrar como o SI/TI variam entre as faces. uma média alta indica que o vídeo é complexo como um todo. Mas se o std da média for alto, quer dizer que o SI/TI variam muito enter as faces. Ou seja, as faces não são uniforme. 
    """

    def __init__(self, config):
        print(f'{self.class_name} initializing...')
        self.config = config
        self.fuse_bitrate_dectime_quality()
        # self.group_tiles_seen()
        # self.group_chunk_tiles_seen_df()
        # self.group_siti_df()

    def convert_head_movement(self):
        head_movement = pd.read_pickle('dataset/head_movement.pickle')
        head_movement.to_hdf('dataset/head_movement.hd5', key='head_movement', complevel=9)

    def group_siti_df(self):
        siti_cmp_qp = pd.read_pickle('dataset/siti_cmp_qp.pickle')
        siti_erp_qp = pd.read_pickle('dataset/siti_erp_qp.pickle')
        siti_qp = pd.concat([siti_cmp_qp, siti_erp_qp], axis=0)
        siti_qp.reset_index(inplace=True)
        siti_qp['chunk'] = siti_qp['frame'].apply(lambda x: x // 30)
        siti_qp['frame'] = siti_qp['frame'].apply(lambda x: x % 30)
        siti_qp.set_index(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'frame'], inplace=True)
        siti_qp.to_hdf('dataset/siti_qp.hd5', key='siti_qp', complevel=9)
        siti_qp_by_chunk_qp = siti_qp.groupby(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']).mean()
        siti_qp_by_chunk_qp.to_hdf('dataset/siti_qp_by_chunk_qp.hd5', key='siti_qp_by_chunk', complevel=9)

    def group_chunk_tiles_seen_df(self):
        user_viewport_quality_cmp_qp = pd.read_pickle('dataset/user_viewport_quality_cmp_qp.pickle')
        user_viewport_quality_erp_qp = pd.read_pickle('dataset/user_viewport_quality_erp_qp.pickle')
        user_viewport_quality_qp_df = pd.concat([user_viewport_quality_cmp_qp, user_viewport_quality_erp_qp], axis=0)
        viewport_quality_by_chunk_qp = user_viewport_quality_qp_df.groupby(['name', 'projection', 'tiling', 'quality', 'user', 'chunk'], sort=False).mean()
        viewport_quality_by_chunk_qp.to_hdf('dataset/viewport_quality_by_chunk_qp.hd5', key='viewport_quality_by_chunk', complevel=9)

    def group_tiles_seen(self):
        seen_tiles_cmp_df = pd.read_pickle('dataset/seen_tiles_cmp_fov110x90.pickle')
        seen_tiles_erp_df = pd.read_pickle('dataset/seen_tiles_erp_fov110x90.pickle')
        seen_tiles_df = pd.concat([seen_tiles_cmp_df, seen_tiles_erp_df], axis=0)
        seen_tiles_df['n_tiles_seen'] = seen_tiles_df['tiles_seen'].apply(len)

        make_set = lambda lista_de_listas: list(set(item for sublista in lista_de_listas for item in sublista))
        a = seen_tiles_df['tiles_seen'].groupby(['name', 'projection', 'tiling', 'user', 'chunk'], sort=False).apply(make_set)
        chunk_tiles_seen_df = pd.DataFrame(a, columns=['tiles_seen'])
        chunk_tiles_seen_df['n_tiles_seen'] = chunk_tiles_seen_df['tiles_seen'].apply(len)
        chunk_tiles_seen_df.to_hdf('dataset/tiles_seen_by_chunk.hd5', key='tiles_seen_by_chunk', complevel=9)

    def fuse_bitrate_dectime_quality(self):
        bitrate_cmp_qp_df = pd.read_pickle('dataset/bitrate_cmp_qp.pickle')
        bitrate_erp_qp_df = pd.read_pickle('dataset/bitrate_erp_qp.pickle')
        bitrate_qp_df = pd.concat([bitrate_cmp_qp_df, bitrate_erp_qp_df], axis=0)

        dectime_cmp_qp_df = pd.read_pickle('dataset/dectime_cmp_qp.pickle')
        dectime_erp_qp_df = pd.read_pickle('dataset/dectime_erp_qp.pickle')
        dectime_qp_df = pd.concat([dectime_cmp_qp_df, dectime_erp_qp_df], axis=0)

        chunk_quality_cmp_qp_df = pd.read_pickle('dataset/chunk_quality_cmp_qp.pickle')
        chunk_quality_cmp_qp_df = chunk_quality_cmp_qp_df.groupby(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']).mean()
        chunk_quality_erp_qp_df = pd.read_pickle('dataset/chunk_quality_erp_qp.pickle')
        chunk_quality_erp_qp_df = chunk_quality_erp_qp_df.groupby(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']).mean()
        chunk_quality_qp_df = pd.concat([chunk_quality_cmp_qp_df, chunk_quality_erp_qp_df], axis=0)

        chunk_data_qp_df = pd.concat([bitrate_qp_df, dectime_qp_df, chunk_quality_qp_df], axis=1)

        chunk_data_qp_df.to_hdf('dataset/chunk_data_qp.hd5', key='chunk_data', complevel=9)
        chunk_data_qp_df.to_pickle('dataset/chunk_data_qp.pickle')

        # store = pd.HDFStore('dataset/chunk_data_qp.hd5')
        # store.keys()
        # store.close()
        # df=pd.read_hdf('dataset/chunk_quality_qp_9.hd5', key='chunk_data')

        print('')


if __name__ == '__main__':
    os.chdir('../')

    CreateAveragedDataset(Config())
