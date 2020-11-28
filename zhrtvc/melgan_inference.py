#!usr/bin/env python
# -*- coding: utf-8 -*-
# author: kuangdd
# date: 2020/11/28
"""
melgan_inference
"""
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__name__).stem)

import traceback
import numpy as np
import argparse
import librosa
import torch
import time
from tqdm import tqdm
from scipy.io import wavfile

from melgan.inference import MelVocoder, get_default_device

_device = get_default_device()


def parse_args():
    parser = argparse.ArgumentParser()
    # Path(r'E:\githup\zhrtvc\data\best_step10_netG_torch.pt')
    parser.add_argument("-i", "--folder", type=Path, default=Path('../data/samples/aliaudio'),
                        help='输入音频文件的目录路径')
    parser.add_argument("-o", "--save_path", type=Path, default=Path("../data/results/melgan"),
                        help='输出生成语音的目录路径')
    parser.add_argument("-m", "--load_path", type=Path,
                        default=Path("../models/vocoder/saved_models/melgan/melgan_multi_speaker.pt"),
                        help='模型路径')
    parser.add_argument("--mode", type=str, default='default',
                        help='模型模式')
    parser.add_argument("--n_samples", type=int, default=10,
                        help='需要实验多少个音频')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    vocoder = MelVocoder(args.load_path, github=args.mode == 'default', model_name=Path(args.load_path).stem,
                         device=_device, mode=args.mode)
    args.save_path.mkdir(exist_ok=True, parents=True)

    fpath_lst = list(args.folder.glob("**/*"))
    fpath_choices = np.random.choice(fpath_lst, min(args.n_samples, len(fpath_lst)), replace=False)
    for i, fname in enumerate(tqdm(fpath_choices, 'inference', ncols=100)):
        try:
            wav, sr = librosa.core.load(str(fname))

            mel = vocoder(torch.from_numpy(wav[None]))

            recons = vocoder.inverse(mel.to(_device)).squeeze().cpu().numpy()

            strftime = time.strftime('%Y%m%d-%H%M%S')
            outdir = Path(args.save_path).joinpath(f'{args.load_path.stem}_{args.mode}')
            outdir.mkdir(exist_ok=True, parents=True)
            filename = str(outdir.joinpath(f'audio_{strftime}_{fname.stem}_raw.wav'))
            wavfile.write(filename=filename, rate=sr, data=wav)
            filename = str(outdir.joinpath(f'audio_{strftime}_{fname.stem}_syn.wav'))
            wavfile.write(filename=filename, rate=sr, data=recons)
            # librosa.output.write_wav(args.save_path.joinpath(f'{fname.stem}.wav'), recons, sr=sr)
        except:
            traceback.print_exc()


if __name__ == "__main__":
    main()
