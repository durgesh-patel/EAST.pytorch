from config import Config
from tqdm import tqdm
import os
import torch
import torch.nn as nn
import numpy as np
import pandas as pd

config = {k:v for k,v in vars(Config).items() if not k.startswith("__")}

image_size = config['image_size']
geometry = config["geometry"]
label_method = config["label_method"]

train_data_dir = config["train_data_dir"]
dev_data_dir = config["dev_data_dir"]

n_H, n_W, n_C = image_size


def quads_to_rboxes(quads_coords):

    raise NotImplementedError()
    

def load_shapes_coords(annotation_path):

    """
    > TODO: Ensure and correct the clockwise order of the coords of a QUAD
    """

    quads_coords = pd.read_csv(annotation_path, header=None)
    quads_coords = quads_coords.iloc[:,:-1].values # [n_box, 8]
    quads_coords = quads_coords.reshape(-1, 4, 2)
    
    if geometry == "QUAD":
        shapes_coords = quads_coords
    elif geometry == "RBOX":
        shapes_coords =  quads_to_rboxes(coords)
    else:
        raise ValueError("Invalid Geometry")
    
    return shapes_coords


representation = geometry + "_" + label_method

if representation == "QUAD_single":
    
    print("Formatting data in", representation, "...")
    for data_dir in [train_data_dir, dev_data_dir]:
        
        print("Processing", data_dir, "...")
        annotations_dir = os.path.join(data_dir, "annotations")
        annotations_representation_dir = os.path.join(data_dir, "annotations_" + representation)
        
        if not os.path.exists(annotations_representation_dir):
            os.mkdir(annotations_representation_dir)
            
        for annotation_file in tqdm(os.listdir(annotations_dir)):
            
            #geometry_map_raw = np.zeros([n_H, n_W, 8])
            geometry_map = np.zeros([128,128, 8])
            
            annotation_path = os.path.join(annotations_dir, annotation_file)
            annotation_representation_path = os.path.join(annotations_representation_dir, annotation_file)
            shapes_coords = load_shapes_coords(annotation_path)
            shapes_centre = shapes_coords.mean(axis=1).astype(np.int32)
            
            for shape_coords, shape_centre in zip(shapes_coords, shapes_centre): # shape_coords -> [4, 2], shape_centre -> [2]
                c_h, c_w = shape_centre
                geometry_map[c_h//4, c_w//4] = shape_coords.flatten() # [8]
            geometry_map = geometry_map.reshape(-1, 8)               
                
            """
            geometry_map_raw = np.moveaxis(geometry_map_raw, 2, 0) # channel_last to channel_first
            geometry_map_raw = torch.from_numpy(geometry_map_raw)
            geometry_map = nn.MaxPool2d((4,4), stride=4)(geometry_map_raw)
            geometry_map = geometry_map.numpy().astype(np.int)
            geometry_map = np.moveaxis(geometry_map, 0, 2) # channel_first to channel_last; geometry_map: [128, 128, 8]
            geometry_map = geometry_map.reshape(-1, 8)
            """
            
            np.savetxt(annotation_representation_path, geometry_map, fmt="%d", delimiter=",")
        
elif representation = "QUAD_multiple":
    

else:
    
    raise NotImplementedError()