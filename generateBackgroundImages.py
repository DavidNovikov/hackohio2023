import glob
import os
import random
import cv2


bgs = glob.glob('images/*/*.jpg')

for i, bg in enumerate(bgs):
    place = random.random()
    imgDir = ''
    labelDir = ''

    if place < 0.7:
        imgDir = 'dataset/train/images'
        labelDir = 'dataset/train/labels'
    elif place < 0.9:
        imgDir = 'dataset/val/images'
        labelDir = 'dataset/val/labels'
    else:
        imgDir = 'dataset/test/images'
        labelDir = 'dataset/test/labels'
    
    cv2.imwrite(f'{imgDir}/img_{i+1000:04}.png', cv2.imread(bg))
    os.system(f'touch {labelDir}/img_{i+1000:04}.txt')
    

