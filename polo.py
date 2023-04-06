#!/usr/bin/env python
# coding: utf-8

# In[ ]:

def find_sub_directories(rootdir):
    
    sub_directories = []
    
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        
        if os.path.isdir(d):
            sub_directories.append(d)
            
        else:
            continue
            
    return(sub_directories)

###----------------------------------------------------------------------

def load_orientation_files(fpath, str_filter, file_type):
    
    files = os.listdir(fpath)
    filt_files = []
    filt_names = []
    
    for i in files:
        if str_filter in i:
            if file_type == '.tif':
                filt_files.append(io.imread(os.path.join(fpath,i)))
            elif file_type == '.npy':
                filt_files.append(np.load(os.path.join(fpath,i)))
            filt_names.append(i)
        else:
            continue
    
    return filt_files, filt_names

###----------------------------------------------------------------------

def load_retardance_files(fpath, str_filter, ceiling_filter = 'Retardance Ceiling (nm)'):
    
    files = os.listdir(fpath)
    
    filt_files = []
    filt_ceilings = []
    filt_names = []
    
    for i in files:
        
        if str_filter in i:
            with TiffFile(os.path.join(fpath, i)) as tif:
                arr = tif.asarray()
                imagej_metadata = tif.imagej_metadata 
            test_metadata = list(imagej_metadata.values())[-1].split(',')
            
            counter = 0
            for i in test_metadata:
                if ceiling_filter in i:
                    break
                counter += 1
            ceiling = int(test_metadata[counter].split(':')[-1])
            
            filt_files.append(arr)
            filt_ceilings.append(ceiling)
            filt_names.append(i)
        else:
            continue
    
    return filt_files, filt_ceilings, filt_names
    
###----------------------------------------------------------------------

def prepro_orientation(files, process_type = 'float'):
    
    prepro_files = [0] * len(files)
    counter = 0
    for i in files:
        if process_type == 'float':
            prepro_files[counter] = np.around(i/100, decimals = 3).astype(np.float)
            counter += 1
        elif process_type == 'int':
            prepro_files[counter] = (i/100).astype(i.dtype)
            counter += 1
        else:
            print('unknown process type')
        
    return prepro_files

###----------------------------------------------------------------------

def prepro_retardance(files, ceilings, process_type = 'float', floor = 0):
    
    prepro_files = [0] * len(files)
    for i in range(len(files)):
        i_arr = files[i]
        i_ceil = ceilings[i]
        if process_type == 'float':
            prepro_files[i] = np.around(i_arr/i_ceil, decimals = 3).astype(np.float)
        elif process_type == 'int':
            prepro_files[i] = (i_arr/i_ceil).astype(i.dtype)
    
    return prepro_files

###----------------------------------------------------------------------

def percentile_pairs(arr, step_size):
    
    idx_steps = np.arange(0, 101, step_size)
    arr_steps = np.percentile(arr, idx_steps).astype(float)
    val_pairs = np.asarray([(arr_steps[i], arr_steps[i+1]) for i in range(arr_steps.shape[0]-1)])
    
    return idx_steps, arr_steps, val_pairs

###----------------------------------------------------------------------

def filter_arr_vals(arr, val_pairs):
    
    expanded_arr = np.empty(np.concatenate(((val_pairs.shape[0],), arr.shape)))
    
    for i in range(val_pairs.shape[0]):
        p = val_pairs[i,:]
        i_arr = np.copy(arr)
        i_arr[arr <= p[0]] = 0
        i_arr[arr > p[1]] = 0
        expanded_arr[i, ...] = i_arr
    
    return expanded_arr

###----------------------------------------------------------------------

def check_pixel_balance(expanded_arr, n_checks):
    
    '''something is wrong with this function. n_checks = expanded_arr.shape[0]'''
    
    px_cts = np.empty(n_checks, dtype = int)
    
    for i in range(n_checks):
        px_cts[i] = np.sum(expanded_arr[i,...].astype(bool).astype(np.uint8))
    
    return px_cts

###----------------------------------------------------------------------

def label_expansion(expanded_arr, se_size = 3):
    
    '''runs with minimial small noise removal.'''
    
    dims = len(expanded_arr.shape)-1
    n_layers = expanded_arr.shape[0]
    
    labeled_arr = np.empty_like(expanded_arr)
    obj_ct = np.empty(n_layers, dtype=int)
    
    if dims == 3:
        se = cube(se_size)
    elif dims == 2:
        se = square(se_size)
    else:
        print('problem!')
    
    for i in range(n_layers):
        i_arr = expanded_arr[i,...]
        i_lab, i_ct = label(binary_opening(i_arr, structure=se), structure=se)
        labeled_arr[i,...] = i_lab
        obj_ct[i] = i_ct
    
    return labeled_arr, obj_ct

###----------------------------------------------------------------------

def det_obj_sizes(labeled_arr, obj_ct, n_layers, bg_val = 0):
    
    '''n_layers = labeled_arr.shape[0]'''
    
    sizes = [0] * n_layers
    for i in range(n_layers):
        i_arr = labeled_arr[i,...]
        
        i_sizes = np.empty((obj_ct[i]+1), dtype = int)
        for j in range(obj_ct[i]+1):
            if j > bg_val:
                i_sizes[j] = np.where(i_arr.flatten() == j)[0].shape[0]
            else:
                i_sizes[j] = 0
        
        sizes[i] = np.vstack((np.arange(obj_ct[i]+1), i_sizes)).T
    
    return sizes

###----------------------------------------------------------------------

def mask_adj_obj(arr, labeled_arr, se_size = 3):
    
    mask = np.sum(labeled_arr, axis = 0)
    indexed = arr[mask == False] = 0
    
    dims = len(expanded_arr.shape)-1
    if dims == 3:
        se = cube(se_size)
    elif dims == 2:
        se = square(se_size)
    else:
        print('problem!')
    
    umbrella_label = label(indexed, structure = se)
    
    return mask, indexed, umbrella_label

###----------------------------------------------------------------------

def orientation_angles(indexed_arr):
    
    x = indexed_arr.flatten()
    x = x[x > 0]
    
    return x

###----------------------------------------------------------------------

def rotate_angles(angles, val):
    
    rotated = np.empty_like(angles)
    
    for i in range(angles.shape[0]):
        i_a = angles[i]
        if i_a < val:
            rotated[i] = i_a - val + 180
        else:
            rotated[i] = i_a - val
    
    return rotated

