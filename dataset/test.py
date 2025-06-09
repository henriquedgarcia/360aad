# %%
import os
import pickle
from pathlib import Path

import pandas as pd

local_path = Path().absolute() / 'dataset'
os.chdir(local_path)
# %%
bitrate_file = Path('bitrate_qp.pickle', )
dectime_file = Path('dectime_qp.pickle', )
chunk_quality_file = Path('chunk_quality_qp.pickle', )
head_movement_file = Path('head_movement.pickle', )
seen_tiles_file = Path('seen_tiles_fov110x90.pickle', )
siti_file = Path('siti_qp.pickle', )

bitrate_df = pickle.loads(bitrate_file.read_bytes())
    # index.names = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']
    # columns = ['bitrate']
dectime_df = pickle.loads(dectime_file.read_bytes())
    # index.names = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']
    # columns = ['dectime']
chunk_quality_df = pickle.loads(chunk_quality_file.read_bytes())
    # index.names = ['name', 'projection', 'tiling', 'tile', 'quality', 'chunk', 'frame']
    # columns = ['ssim', 'mse', 'ws-mse', 's-mse']

head_movement_df = pickle.loads(head_movement_file.read_bytes())
    # index.names = ['name', 'projection', 'user', 'frame']
    # columns = ['yaw', 'pitch', 'roll']
seen_tiles_df = pickle.loads(seen_tiles_file.read_bytes())
    # index.names = ['name', 'projection', 'tiling', 'user', 'chunk']
    # columns = ['seen_tiles']
siti_df = pickle.loads(siti_file.read_bytes())
    # index.names = ['name', 'projection', 'tiling', 'tile', 'quality', 'frame']
    # columns = ['si', 'ti']

# %% Show df info
df = bitrate_df
df = dectime_df
df = chunk_quality_df
df = head_movement_df
df = seen_tiles_df
df = siti_df

print(df.index.names)
print(df.columns)

for name in df.index.names:
    print(df.index.unique(name))
print(df.columns)
print(df.index.names)
# %%  concat df
chunk_quality_df_grouped = chunk_quality_df.groupby(['name', 'projection', 'tiling', 'tile', 'quality', 'chunk']).mean()

df_final = pd.concat([bitrate_df, dectime_df, chunk_quality_df_grouped], axis=1)
df_final.to_pickle('chunk_data_qp.pickle')

# %%
f2 = Path('dataset/seen_tiles_fov110x90.pickle')
df2 = pickle.loads(f2.read_bytes())
names_list = list(df2.index.unique('name'))
print(names_list)
# %%
files = Path('seen_tiles.pickle')
df = pickle.loads(files.read_bytes())
df
# %%
df_filtrado = df.loc[df.index.get_level_values('name').isin(names_list)]
df_filtrado
# %%

# Criando um exemplo de DataFrame MultiIndex
index = pd.MultiIndex.from_product([['video1', 'video2'], ['720p', '1080p'], range(90)], names=['video', 'quality', 'frame'])
df = pd.DataFrame({'bitrate': range(360)}, index=index)

# Agrupando por 'video' e 'quality', criando 'chunk' a cada 30 frames
df_grouped = (df.groupby(['video', 'quality', df.index.get_level_values('frame') // 30]).mean())
df_grouped = df_grouped.rename_axis(index={'frame': 'chunk'})

print(df_grouped)
