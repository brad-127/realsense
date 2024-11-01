import numpy as np
import os
import argparse

# コマンドライン引数の設定
parser = argparse.ArgumentParser(description="RGBD .npyファイルを表示します。")
parser.add_argument("subdirectory", type=str, help="RGBD .npyファイルが保存されているサブディレクトリ名（例: 20241031）")
args = parser.parse_args()

# 固定のパスを設定
base_directory = "image_data/"
full_directory = os.path.join(base_directory, args.subdirectory, "data")

# ディレクトリ内のすべての.npyファイルをリストアップ
npy_files = [f for f in os.listdir(full_directory) if f.endswith('.npy')]

for npy_file in npy_files:
    # RGBDデータを読み込む
    rgbd_image = np.load(os.path.join(full_directory, npy_file))

    # RGBと深度成分に分割
    rgb_image = rgbd_image[:, :, :-1]  # 最後のチャンネル以外（RGB）
    depth_image = rgbd_image[:, :, -1]  # 最後のチャンネル（深度）

    # RGB画像の数値を表示
    print(f"RGB Image from {npy_file}:")
    print(rgb_image)
   
    # 深度画像の数値を表示
    print(f"Depth Image from {npy_file}:")
    print(depth_image)

    print(f"RGB Image shape: {rgb_image.shape}")
    print(f"Depth Image shape: {depth_image.shape}")

    print("\n" + "="*40 + "\n")  # 区切り
