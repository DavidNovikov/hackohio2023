import random
import cv2
import glob
import numpy as np


def getIndxOfClass(fileName):
    if 'knife' in fileName:
        return 0
    if 'scissor' in fileName:
        return 1
    if 'tissue' in fileName:
        return 2
    else:
        print(fileName, ' is broken!!!!!!!!!!!')
        exit()

def makeAnnotation(mask, file, image, idx):
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
    
    cv2.imwrite(f'{imgDir}/img_{idx:04}.png', image)
    
    c = getIndxOfClass(file)
    
    f = open(f'{labelDir}/img_{idx:04}.txt', 'x')
    
    img_h, img_w, _  = image.shape
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for obj in contours:
        annotationStr = f'{c} '
        for point in obj:
            annotationStr += f'{point[0][0]/img_w} {point[0][1]/img_h} '
        f.write(f'{annotationStr}\n')
    
    f.close()
    

bgs = glob.glob('images/*/*.jpg')
files = glob.glob('images/*/*/*.jpg')

bgs.extend(files)

numImagesValid = 0

fgbg = cv2.createBackgroundSubtractorKNN()
for file in bgs:
    bg = cv2.imread(file)
    fgbg.apply(bg)

files = random.choices(files, k=10)

for j,file in enumerate(files):
    image = cv2.imread(file)
    numOfExpectedObjects = int(file[file.index('WIN')-2])
    indxOfClass = getIndxOfClass(file)
    
    fgmask = fgbg.apply(image)
    
    cv2.imwrite(f'initalMask{j}.png', fgmask)
    cv2.imwrite(f'datasetImage{j}.png', image)
    
    
    ret, thresheldImage = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY)
    mask = thresheldImage.copy()
    maskCopy = thresheldImage.copy()
    mask[:,:] = 0
    
    kernel = np.ones((3, 3), np.uint8)           
    thresheldImage = cv2.dilate(thresheldImage, kernel, iterations=1) 
    
    contour, hier = cv2.findContours(thresheldImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    for cnt in contour:
        cv2.drawContours(thresheldImage, [cnt], 0, 255, -1)

    thresheldImage = cv2.erode(thresheldImage, kernel, iterations=2) 
    
    nb_components, labels, stats, centroids = cv2.connectedComponentsWithStats(thresheldImage, 8, cv2.CV_32S)
    indxOfBiggest = np.argpartition(stats[1:,cv2.CC_STAT_AREA], -numOfExpectedObjects)[-numOfExpectedObjects:]
    
    for i in range(numOfExpectedObjects):
        label = indxOfBiggest[i] + 1
        mask[labels == label] = 1
        maskCopy[labels == label] = 255
        
    mask = cv2.medianBlur(mask, 5)
    
    cv2.imwrite(f'generatedMask{j}.png', maskCopy)
    
    
    imageCopy = image.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(imageCopy, contours, -1, (0,255,0), 3)
    cv2.imwrite(f'objectsHighlighted{j}.png', imageCopy)
    # imageCopy[mask != 1] = 0.5 * imageCopy[mask != 1]
    # cv2.imshow(f'{numOfExpectedObjects}, {indxOfClass}', imageCopy)
    # keyPressed = cv2.waitKey()
    
    # if keyPressed == ord('y'):
    #     makeAnnotation(mask, file, image, numImagesValid)
    #     numImagesValid += 1