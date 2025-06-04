# %%
import pickle
from pathlib import Path

import pandas as pd

# %%

file_names = [
    'dataset/bitrate_qp.pickle',
    'dataset/dectime_qp.pickle',
    'dataset/chunk_quality_mse_qp.pickle',
    'dataset/chunk_quality_qp.pickle',
    'dataset/chunk_quality_s-mse_qp.pickle',
    'dataset/chunk_quality_ssim_qp.pickle',
    'dataset/chunk_quality_ws-mse_qp.pickle',
    # 'head_movement.pickle',
    # 'seen_tiles_fov110x90.pickle',
    # 'siti_qp.pickle',
    # 'user_viewport_quality_qp.pickle',
]
files = list(map(Path, file_names))
dfs = [pickle.loads(file.read_bytes()) for file in files]


def func(x):
    frame_level_values = x.index.get_level_values('frame')
    chunk_level_values = frame_level_values // 30  # 0, 30, 60,
    return x['bitrate'].groupby(chunk_level_values).mean()


df_grouped = df.groupby(['name', 'projection', 'tiling', 'tile', 'quality'])
df_grouped = df_grouped.apply()

df_final = pd.concat(dfs, axis=1)
df_final.to_pickle('dataset/user_viewport_quality_qp.pickle')
# %%
# "dataset/siti_qp.pickle"
# "dataset/user_viewport_quality_qp.pickle"
# "dataset/bitrate_qp.pickle"
# "dataset/chunk_quality_qp.pickle"
# "dataset/dectime_qp.pickle"
# "dataset/head_movement.pickle"
# file = "dataset/siti_qp.pickle"
# df = pd.read_pickle(file)
# df
# df.index.names
# df.columns
# for name in df.index.names:
#     print(df.index.unique(name))
# print(df.columns)
# print(df.index.names)
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
