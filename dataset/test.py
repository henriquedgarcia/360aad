# %%
import pandas as pd

pd.__version__
# %%
import pickle
from pathlib import Path

# %%

files = [
    Path("dataset/user_viewport_quality_mse_qp.pickle"),
    Path("dataset/user_viewport_quality_ssim_qp.pickle"),
]
dfs = [pickle.loads(file.read_bytes()) for file in files]
df_final = pd.concat(dfs, axis=1)
df_final.to_pickle('dataset/user_viewport_quality_qp.pickle')
# %%
# "dataset/siti_qp.pickle"
# "dataset/user_viewport_quality_qp.pickle"
# "dataset/bitrate_qp.pickle"
# "dataset/chunk_quality_qp.pickle"
# "dataset/dectime_qp.pickle"
# "dataset/head_movement.pickle"
file = "dataset/siti_qp.pickle"
df = pd.read_pickle(file)
df
df.index.names
df.columns
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

pickle.dumps(df_filtrado)
