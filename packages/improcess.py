from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import imageio
from scipy import signal
import getimage
import conversion
import numpy as np


def get_processed_image(start_date="2017-10-01", num_days=31, end_date=None,**kwargs):
    '''
    Intake a date range of photo records and then generate the enhanced resulted single image
    param: start date                             type:string
    param: num_days                               type:int
    param: end_date                               type:string
    
    output: np.array 
    
    '''
    l = getimage.get_image_date_range(start_date, num_days, end_date, **kwargs)
    w,h=l[0].shape
    arr=zeros((h,w),float)
    N=len(l)
    for im in l:
        imarr=array(im,dtype=float)
        arr=arr+imarr/N
    out = matrix.round(arr)
    out *= 255.0/out.max()    
    out = signal.wiener(out,5)
    avg=60
    out[out<=1.7*avg and out>=0.9*avg]=out*0.5
    filtered = signal.wiener(out,5)
    return filtered

def get_california_image(tileMatrix=6, tileCol=12, tileRow=10, start_date="2017-10-01", num_days=31):
    im = []
    mask = []
    for i in range(3):
        im1 = get_processed_image(tileMatrix=tileMatrix, tileCol=tileCol, tileRow=tileRow+i, start_date=start_date)
        im2 = get_processed_image(tileMatrix=tileMatrix, tileCol=tileCol+1, tileRow=tileRow+i, start_date=start_date)
        im3 = get_processed_image(tileMatrix=tileMatrix, tileCol=tileCol+2, tileRow=tileRow+i, start_date=start_date)
        im.append(np.concatenate((im1, im2, im3), axis=1))
        mask1 = getimage.get_mask(tileMatrix=tileMatrix, tileCol=tileCol, tileRow=tileRow+i)
        mask2 = getimage.get_mask(tileMatrix=tileMatrix, tileCol=tileCol+1, tileRow=tileRow+i)
        mask3 = getimage.get_mask(tileMatrix=tileMatrix, tileCol=tileCol+2, tileRow=tileRow+i)
        mask.append(np.concatenate((mask1, mask2, mask3), axis=1))
    output_im = np.concatenate(tuple(im), axis=0)
    output_mask = np.concatenate(tuple(mask), axis=0)

    return output_im, output_mask