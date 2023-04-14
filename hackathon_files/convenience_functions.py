from __future__ import print_function, division
import os
import numpy as np
import matplotlib.pyplot as plt
from pylab import get_cmap
from matplotlib.colors import ListedColormap


def color_blocking(n_blocks, color_map, background_color):
    
    '''... requires pylab.get_cmap and matplotlib.colors.ListedColormap
    black background rgba = [0,0,0,1]
    white background rgba = [255, 255, 255, 1]'''
    
    sample_color_map = get_cmap(color_map, n)
    sample_color_map = sample_color_map(np.linspace(0,1, n+1))
    
    background = np.reshape(np.asarray(background_color), (1,4))
    
    color_block_map = np.concatenate((background, sample_color_map), axis = 0)
    color_block_map = ListedColormap(color_block_map)
    
    return color_block_map

###---------------------------------------------------------

def find_sub_directories(rootdir):
    
    sub_directories = []
    
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        
        if os.path.isdir(d):
            sub_directories.append(d)
            
        else:
            continue
            
    return(sub_directories)

###---------------------------------------------------------

