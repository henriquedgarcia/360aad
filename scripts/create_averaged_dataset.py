import json
import os
from typing import Union

import numpy as np
import pandas as pd

from scripts.analysisbase import AnalysisPaths
from scripts.utils.config import Config
from scripts.utils.progressbar import ProgressBar


class CreateAveragedDataset(AnalysisPaths):
    """
    # Análise do movimento de cabeça.
    ## movimento de cabeça (por frame)
        Podemos calcular a velocidade de cada usuário para cada vídeo partindo do repouso v0 = 0 rad/s
            plotar por frame e ver os momentos de maior velocidade (talvez usar um filtro passa baixa para reduzir tremedeira)
        podemos calcular a aceleração para descobrir momentos que ele fixa atenção (menores acelerações)
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
            columns = [bitrate, dectime, ssim, mse, s-mse, ws-mse] (verificar esses hifens)
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
        self.create_session_dataset()
        # self.group_siti_df()

        # self.convert_head_movement()
        # self.group_chunk_tiles_seen_df()
        # self.group_tiles_seen()
        # self.fuse_bitrate_dectime_quality()

        # chunk_data = pd.read_hdf('dataset/chunk_data.hd5')
        # head_movement = pd.read_hdf('dataset/head_movement.hd5')
        # tiles_seen = pd.read_hdf('dataset/tiles_seen.hd5')
        # viewport_quality = pd.read_hdf('dataset/viewport_quality.hd5')


    @staticmethod
    def fuse_bitrate_dectime_quality():
        print('Loading Raw Datasets')
        bitrate_cmp_qp_df = pd.read_pickle('dataset/raw/bitrate_cmp_qp_raw.pickle')
        bitrate_erp_qp_df = pd.read_pickle('dataset/raw/bitrate_erp_qp_raw.pickle')
        bitrate_qp_df = pd.concat([bitrate_cmp_qp_df, bitrate_erp_qp_df], axis=0)

        dectime_cmp_qp_df = pd.read_pickle('dataset/raw/dectime_cmp_qp_raw.pickle')
        dectime_erp_qp_df = pd.read_pickle('dataset/raw/dectime_erp_qp_raw.pickle')
        dectime_qp_df = pd.concat([dectime_cmp_qp_df, dectime_erp_qp_df], axis=0)
        somas = np.array([sum(lista) for lista in dectime_qp_df['dectime']])
        tamanhos = np.array([len(lista) for lista in dectime_qp_df['dectime']])
        dectime_qp_df['dectime'] = somas / tamanhos

        chunk_quality_cmp_qp_df = pd.read_pickle('dataset/raw/chunk_quality_cmp_qp_raw.pickle')
        chunk_quality_cmp_qp_df = chunk_quality_cmp_qp_df.groupby(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']).mean()
        chunk_quality_erp_qp_df = pd.read_pickle('dataset/raw/chunk_quality_erp_qp_raw.pickle')
        chunk_quality_erp_qp_df = chunk_quality_erp_qp_df.groupby(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']).mean()
        chunk_quality_qp_df = pd.concat([chunk_quality_cmp_qp_df, chunk_quality_erp_qp_df], axis=0)

        chunk_data_qp_df = pd.concat([bitrate_qp_df, dectime_qp_df, chunk_quality_qp_df], axis=1)

        print('Creating chunk_file list')
        decodable_path = []
        for name, projection, tiling, tile, quality, chunk in chunk_data_qp_df.index:
            file = f'decodable/{name}/{projection}/{tiling}/tile{tile}/qp{quality}/chunk{chunk + 1}.mp4'
            decodable_path.append(file)
        chunk_data_qp_df['path'] = decodable_path

        print('Saving HDF5 files')
        chunk_data_qp_df.to_hdf('dataset/chunk_data_qp.hd5', key='chunk_data', complevel=9, mode='a')

        # store = pd.HDFStore('dataset/chunk_data_qp.hd5')
        # store.keys()
        # store.close()
        # df=pd.read_hdf('dataset/chunk_quality_qp_9.hd5', key='chunk_data')

        print('')

    @staticmethod
    def create_session_dataset():
        chunk_data_qp: Union[object, pd.DataFrame] = pd.read_hdf('dataset/chunk_data_qp.hd5')
        viewport_quality_by_chunk_qp: Union[object, pd.DataFrame] = pd.read_hdf('dataset/viewport_quality_by_chunk_qp.hd5')
        tiles_seen_by_chunk: Union[object, pd.DataFrame] = pd.read_hdf('dataset/tiles_seen_by_chunk.hd5')
        user_session_qp: Union[object, pd.DataFrame] = pd.read_hdf('dataset/user_session_qp.hd5')

        session_data = []
        ui = ProgressBar(total=8 * 2 * 5 * 5 * 30 * 60, desc='create_session_dataset')
        for name, projection, tiling, quality, user, chunk in viewport_quality_by_chunk_qp.index:
            ui.update(f'{name=}, {projection=}, {tiling=}, {quality=}, {user=}, {chunk=}')
            viewport = viewport_quality_by_chunk_qp.xs(key=(name, projection, tiling, quality, user, chunk),
                                                       level=('name', 'projection', 'tiling', 'quality', 'user', 'chunk'))
            tiles_seen = tiles_seen_by_chunk.xs(key=(name, projection, tiling, user, chunk),
                                                level=('name', 'projection', 'tiling', 'user', 'chunk'))
            chunk_data = chunk_data_qp.xs(key=(name, projection, tiling, quality, chunk),
                                          level=('name', 'projection', 'tiling', 'quality', 'chunk'))
            list_of_tiles = tiles_seen['tiles_seen'][0]

            bitrate = chunk_data.loc[list_of_tiles]['bitrate'].sum()
            dectime_serial = chunk_data.loc[list_of_tiles]['dectime'].sum()
            dectime_parallel = chunk_data.loc[list_of_tiles]['dectime'].max()
            ssim = chunk_data.loc[list_of_tiles]['ssim'].mean()
            mse = chunk_data.loc[list_of_tiles]['mse'].mean()
            s_mse = chunk_data.loc[list_of_tiles]['s-mse'].mean()
            ws_mse = chunk_data.loc[list_of_tiles]['ws-mse'].mean()
            viewport_mse = viewport['mse'][0]
            viewport_ssim = viewport['ssim'][0]
            n_tiles_seen = len(list_of_tiles)
            decodable_path = {}
            for tile in list_of_tiles:
                decodable_path.update({tile: f'decodable/{name}/{projection}/{tiling}/tile{tile}/qp{quality}/chunk{chunk}.mp4'})
            decodable_path = json.dumps(decodable_path)
            data = (name, projection, tiling, quality, user, chunk,
                    bitrate, dectime_serial, dectime_parallel, ssim,
                    mse, s_mse, ws_mse, viewport_mse, viewport_ssim,
                    n_tiles_seen, decodable_path)
            session_data.append(data)

        print(f'\nSaving')
        df = pd.DataFrame(session_data, columns=['name', 'projection', 'tiling', 'quality', 'user', 'chunk',
                                                 'bitrate', 'dectime_serial', 'dectime_parallel', 'ssim', 'mse', 's_mse',
                                                 'ws_mse', 'viewport_mse', 'viewport_ssim', 'n_tiles_seen'])
        df.set_index(['name', 'projection', 'tiling', 'quality', 'user', 'chunk'], inplace=True)
        df.to_hdf(f'dataset/user_session_qp.hd5', key='df')

    @staticmethod
    def convert_head_movement():
        head_movement = pd.read_pickle('dataset/raw/head_movement_raw.pickle')
        head_movement.to_hdf('dataset/head_movement.hd5', key='head_movement', complevel=9)

    @staticmethod
    def group_siti_df():
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

    @staticmethod
    def group_chunk_tiles_seen_df():
        user_viewport_quality_cmp_qp = pd.read_pickle('dataset/raw/user_viewport_quality_cmp_qp_raw.pickle')
        user_viewport_quality_erp_qp = pd.read_pickle('dataset/raw/user_viewport_quality_erp_qp_raw.pickle')
        user_viewport_quality_qp_df = pd.concat([user_viewport_quality_cmp_qp, user_viewport_quality_erp_qp], axis=0)
        user_viewport_quality_qp_df.to_hdf('dataset/viewport_quality.hd5', key='viewport_quality', complevel=9)
        # viewport_quality_by_chunk_qp = user_viewport_quality_qp_df.groupby(['name', 'projection', 'tiling', 'quality', 'user', 'chunk'], sort=False).mean()
        # viewport_quality_by_chunk_qp.to_hdf('dataset/viewport_quality_by_chunk_qp.hd5', key='viewport_quality', complevel=9)

    @staticmethod
    def group_tiles_seen():
        seen_tiles_cmp_df = pd.read_pickle('dataset/raw/seen_tiles_cmp_fov110x90_raw.pickle')
        seen_tiles_erp_df = pd.read_pickle('dataset/raw/seen_tiles_erp_fov110x90_raw.pickle')

        tiles_seen_df = pd.concat([seen_tiles_cmp_df, seen_tiles_erp_df], axis=0)
        tiles_seen_df = tiles_seen_df['tiles_seen'].apply(tuple)

        # make_set = lambda lista_de_listas: list(set(item for sub_lista in lista_de_listas for item in sub_lista))
        # a = seen_tiles_df['tiles_seen'].groupby(['name', 'projection', 'tiling', 'user', 'chunk'], sort=False).apply(make_set)
        # chunk_tiles_seen_df = pd.DataFrame(a, columns=['tiles_seen'])

        tiles_seen_df.to_hdf('dataset/tiles_seen.hd5', key='tiles_seen_by_chunk', complevel=9)


if __name__ == '__main__':
    os.chdir('../')

    CreateAveragedDataset(Config())
