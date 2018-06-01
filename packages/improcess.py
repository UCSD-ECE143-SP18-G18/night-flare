from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import imageio
from scipy import signal
import getimage

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