import os
import sys
import random
import math
import numpy as np
import skimage.io
import time
import matplotlib
import matplotlib.pyplot as plt
import scipy.misc

import coco
import utils
import model as modellib
import visualize

def collapse_segmentation(segmentation):
    sizes = np.zeros(len(segmentation[0][0]))
    for i in range(len(segmentation[0][0])):
        sizes[i] = sum(sum(segmentation[:,:,i]))
    order = np.argsort(sizes)
    output = np.zeros((len(segmentation), len(segmentation[0])))
    for i in order:
        for x in range(len(segmentation)):
            for y in range(len(segmentation[0])):
                if (segmentation[x][y][i] and not output[x][y]):
                    output[x][y] = i + 1
    return output


ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
IMAGE_DIR = os.path.join(ROOT_DIR, "images")

class InferenceConfig(coco.CocoConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    IMAGE_MAX_DIM = 768
    IMAGE_MIN_DIM = 600
    
config = InferenceConfig()
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
model.load_weights(COCO_MODEL_PATH, by_name=True)
class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']
print('beginning inference')
#filenames = ['hackathon.jpg', 'hack1.jpg', 'hack2.jpg', 'hack3.jpg']
filenames = ['cheeza.jpg']
times = []
for filename in filenames:
    start = time.time()
    image = skimage.io.imread(filename)


    results = model.detect([image], verbose=1)

    r = results[0]['masks']
    print(r.shape)
    end = time.time()
    print(end - start)
    times.append(end - start)

    np.savetxt(filename[:-4] + '_mask.txt', collapse_segmentation(r), fmt='%d')
print(times)

def segment_image(filename):
    """segments an image, outputting segmentted masks and files with            
    the segmented masked applied."""
    start = time.time()
    image = skimage.io.imread(filename)
    results = model.detect([image], verbose=0)
    r = results[0]['masks']
    end = time.time()
    print(end - start)

    collapsed = collapse_segmentation(r)
    for i in range(len(r[0][0])):
        scipy.misc.imsave(filename[:-4] + '_' + str(i + 1) + '.jpg',
                          image * np.reshape(collapsed == (i + 1),
                                             (r.shape[0], r.shape[1], 1)))

    np.savetxt(filename[:-4] + '_mask.txt', collapsed, fmt='%d')

segment_image('cheeza3.jpg')
        
