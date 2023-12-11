import numpy as np
import util as U
import matplotlib.pyplot as plt
import argparse
import cv2
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=str, required=True)
    parser.add_argument('--output-dir', type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.output_dir): os.makedirs(args.output_dir)

    for sub_dir in os.listdir(args.input_dir):

        output_sub_dir = os.path.join(args.output_dir, sub_dir)
        if not os.path.exists(output_sub_dir): os.makedirs(output_sub_dir)

        imgs = U.getImgs(os.path.join(args.input_dir, sub_dir), color=True)

        # and now get albedo
        # for boundary conditions we assume the boundary of the image
        # is set to zero
        imgs = U.zeroPadding(imgs, 2)

        imR, dxs, dys, dx, dy, invKhat = U.getAlbedo(imgs)

        cv2.imwrite(os.path.join(output_sub_dir, 'reflectance.jpg'), imR)

        # to get lighting we subtract median lighting from the gradient
        # and reconstruct
        for idx in range(len(imgs)):
            light, _ = U.reconsEdge3(dxs[idx]-dx, dys[idx]-dy, invKhat)
            cv2.imwrite(os.path.join(output_sub_dir, f'light{idx}.jpg'), light)


if __name__ == "__main__":
    main()