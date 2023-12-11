import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import cv2
import os
import glob

def getImgs(dir_path, color=False, pattern="*"):
    img_list = glob.glob(os.path.join(dir_path,pattern))
    imgs = []
    color_flag = cv2.IMREAD_GRAYSCALE if not color else cv2.IMREAD_COLOR
    for img_path in img_list:
        img = cv2.imread(img_path, color_flag)
        imgs.append(img)
    return np.array(imgs)

def zeroPadding(imgs, num=None):
    if num is None: num = 1

    imgs[:,:,:num] = 0
    imgs[:,:num,:] = 0
    imgs[:,-num:,:] = 0
    imgs[:,:,-num:] = 0

    return imgs

def getAlbedo(bigIm1, invKhat=None):
    dxs = np.zeros(bigIm1.shape)
    dys = np.zeros(bigIm1.shape)

    for i in range(bigIm1.shape[0]):
        if np.ndim(bigIm1[0]) == 2:
            dx = signal.convolve2d(bigIm1[i,:,:], np.atleast_2d([0, 1, -1]), mode='same')
            dy = signal.convolve2d(bigIm1[i,:,:], np.atleast_2d([0, 1, -1]).T, mode='same')
            dxs[i,:,:] = dx
            dys[i,:,:] = dy

        elif np.ndim(bigIm1[0]) == 3:
            for c in range(bigIm1[i].shape[-1]):
                dx = signal.convolve2d(bigIm1[i,:,:,c], np.atleast_2d([0, 1, -1]), mode='same')
                dy = signal.convolve2d(bigIm1[i,:,:,c], np.atleast_2d([0, 1, -1]).T, mode='same')
                dxs[i,:,:,c] = dx
                dys[i,:,:,c] = dy
                
    dx = np.median(dxs, axis=0)
    dy = np.median(dys, axis=0)

    if invKhat is None: imR, invKhat = reconsEdge3(dx, dy)
    else: imR=reconsEdge3(dx,dy,invKhat)

    return imR, dxs, dys, dx, dy, invKhat

def reconsEdge3(dx, dy, invKhat=None):
    # given dx dy reconstruct image
    # here we do the convolutions using FFT2
    if np.ndim(dx) == 2:
        img = np.zeros(dx.shape)
        sx, sy = dx.shape
        max_size = max(sx, sy)

        if invKhat is None:
            invK = invDel2(2*max_size)
            invKhat = np.fft.fft2(invK)
        
        imgX = signal.convolve2d(dx, np.atleast_2d([0,1,-1])[:,::-1], mode='same')
        imgY = signal.convolve2d(dy, np.atleast_2d([0,1,-1]).T[::-1,:], mode='same')
        
        imgS = imgX+imgY

        imgShat = np.fft.fft2(imgS, s=[2*max_size, 2*max_size])
        img = np.real(np.fft.ifft2(imgShat*invKhat))
        img = img[max_size:max_size+sx, max_size:max_size+sy]

    elif np.ndim(dx) == 3:
        if invKhat is None:
            img = np.zeros(dx.shape)
            invKhats = []
            for c in range(dx.shape[-1]):
                img[:,:,c], invKhat = reconsEdge3(dx[:,:,c], dy[:,:,c])
                invKhats.append(invKhat)
            invKhat = np.transpose(np.array(invKhats), (1,2,0))
        else:
            img = np.zeros(dx.shape)
            for c in range(dx.shape[-1]):
                img[:,:,c], _ = reconsEdge3(dx[:,:,c], dy[:,:,c], invKhat[:,:,c])
    
    img = cv2.normalize(src=img, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    return img, invKhat

def invDel2(img_size, color=False):
    if not color:
        K = np.zeros((img_size, img_size))
        K[img_size//2, img_size//2] = -4
        K[img_size//2 + 1, img_size//2] = 1
        K[img_size//2, img_size//2 + 1] = 1
        K[img_size//2 - 1, img_size//2] = 1
        K[img_size//2, img_size//2 - 1] = 1

        Khat = np.fft.fft2(K)
        I = np.nonzero(Khat == 0)
        Khat[I] = 1
        invKhat = 1/Khat
        invKhat[I] = 0
        invK = np.fft.ifft2(invKhat)
        invK = -np.real(invK)
        invK = signal.convolve2d(invK, np.array([[1,0,0],[0,0,0],[0,0,0]]), mode='same') # shift by one
    else:
        invK = np.zeros((img_size, img_size, 3))
        for c in range(3):
            invK[:,:,c] = invDel2(img_size)
    return invK