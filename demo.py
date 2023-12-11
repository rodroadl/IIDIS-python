import numpy as np
import util as U
import matplotlib.pyplot as plt
import argparse
import cv2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, default="")

    args = parser.parse_args()
    if args.dir:
        with_image(args.dir)
    else:
        figure4()

def figure4():
    # make a demo of circle in square shadow
    x,y = np.mgrid[0:64., 0:64.]
    x -= 32
    y -= 32
    circle_img = (x**2+y**2) < 225

    fnum = 1
    big_im1 = np.zeros((2*fnum + 1, 64, 64))

    for i in range(-fnum-1,fnum):
        im1 = np.zeros((64,64))
        im1[5*i+11:5*i+51, 5*i+11:5*i+51] = .6 # this puts shadow
        im1 = im1 + circle_img
        big_im1[i+fnum,:,:] = im1

    # and now get albedo
    # for boundary conditions we assume the boundary of the image
    # is set to zero
    big_im1 = U.zeroPadding(big_im1, 2)

    imR, dxs, dys, dx, dy, invKhat = U.getAlbedo(big_im1)


    plt.subplot(331)
    plt.imshow(big_im1[-1,:,:], cmap='gray')
    plt.title('frame 1')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(334)
    plt.imshow(big_im1[0,:,:], cmap='gray')
    plt.title('frame 2')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(337)
    plt.imshow(big_im1[1,:,:], cmap='gray')
    plt.title('frame 3')
    plt.xticks([])
    plt.yticks([])

    light1, _ = U.reconsEdge3(dxs[-1,:,:]-dx, dys[-1,:,:]-dy, invKhat)
    light2, _ = U.reconsEdge3(dxs[0,:,:]-dx, dys[0,:,:]-dy, invKhat)
    light3, _ = U.reconsEdge3(dxs[1,:,:]-dx, dys[1,:,:]-dy, invKhat)

    plt.subplot(332)
    plt.imshow(light1, cmap='gray')
    plt.title('light 1')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(335)
    plt.imshow(light2, cmap='gray')
    plt.title('light 2')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(338)
    plt.imshow(light3, cmap='gray')
    plt.title('light 3')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(133)
    plt.imshow(imR, cmap='gray')
    plt.title('reflectance')
    plt.xticks([])
    plt.yticks([])
    plt.show()

def with_image(dir_path):
    imgs = U.getImgs(dir_path, color=True)
    
    # and now get albedo
    # for boundary conditions we assume the boundary of the image
    # is set to zero
    imgs = U.zeroPadding(imgs, 2)

    imR, dxs, dys, dx, dy, invKhat = U.getAlbedo(imgs)

    # to get lighting we subtract median lighting from the gradient
    # and reconstruct

    for idx in range(len(imgs)):
        light1, _ = U.reconsEdge3(dxs[idx]-dx, dys[idx]-dy, invKhat)

        _, axs = plt.subplots(3)
        axs[0].imshow(cv2.cvtColor(imgs[idx], cv2.COLOR_BGR2RGB))
        axs[0].set_title(f"imgs{idx}")
        axs[0].set_xticks([])
        axs[0].set_yticks([])
        axs[1].imshow(cv2.cvtColor(imR,cv2.COLOR_BGR2RGB))
        axs[1].set_title("reflectance")
        axs[1].set_xticks([])
        axs[1].set_yticks([])
        axs[2].imshow(cv2.cvtColor(light1, cv2.COLOR_BGR2RGB))
        axs[2].set_title(f"illum{idx}")
        axs[2].set_xticks([])
        axs[2].set_yticks([])
        plt.tight_layout()
        plt.show()
    return

if __name__ == "__main__":
    main()