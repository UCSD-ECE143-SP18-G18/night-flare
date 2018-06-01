from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import imageio
from scipy import signal
import getimage

def get_processed_image(start_date="2017-10-01", num_days=31, end_date=None,**kwargs):
    
    l = getimage.get_image_date_range(start_date, num_days, end_date, **kwargs)

    #plt.axis('off')

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

    for i in range(out.shape[1]):
        for j in range(out.shape[0]):
            if out[i][j]<=1.7*avg and out[i][j]>=0.9*avg:
                out[i][j]*=0.5

    filtered = signal.wiener(out,5)
    #fig=plt.figure(figsize=(10,10))
    #plt.imshow(filtered)
    return filtered