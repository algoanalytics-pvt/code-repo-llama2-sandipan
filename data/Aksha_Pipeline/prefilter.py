import cv2
import numpy as np
from skimage.metrics import structural_similarity
import datetime

def calc_diff(background, original):
  ssim, difference_image = structural_similarity(
    background.astype(np.float32) / 255, original.astype(np.float32) / 255, full=True, channel_axis= None)
  difference_image = (difference_image * 255).astype(np.uint8)
  blur = cv2.GaussianBlur(difference_image, (5, 5), 0)
  thresh, ret = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  kernel = np.ones((2,2),np.uint8)
  ret = cv2.dilate(ret,kernel,iterations = 2)
  ret = 255 - ret
  return ret, ssim


def extract_foreground(current_image, weekly_background_image, daily_background_image):
    current_image_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
    difference_image_weekly, ssim_1 = calc_diff(weekly_background_image, current_image_gray)
    difference_image_daily, ssim_2 = calc_diff(daily_background_image, current_image_gray)
    final_mask = cv2.bitwise_and(difference_image_weekly, difference_image_daily, mask=None)
    nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(final_mask, None, None, None, 8, cv2.CV_32S)
    areas = stats[1:,cv2.CC_STAT_AREA]
    result_mask = np.zeros((labels.shape), np.uint8)
    current_image_copy = current_image.copy()
    for i in range(0, nlabels - 1):
        if areas[i] >= 500:   #keep
            result_mask[labels == i + 1] = 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
    morph_op_result = cv2.morphologyEx(result_mask, cv2.MORPH_CLOSE, kernel, )
    contours, _ = cv2.findContours(morph_op_result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    black = np.zeros(current_image_gray.shape)
    if len(contours) != 0:
 
        c = max(contours, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(c)

        cv2.drawContours(black, [c], 0, 255, -1)
        red = np.ones(black.shape)
        red = red*255
        current_image_copy = cv2.cvtColor(current_image_copy, cv2.COLOR_RGB2BGR)
        current_image_copy[:,:,0][black>0] = red[black>0]
        current_image_copy = cv2.cvtColor(current_image_copy, cv2.COLOR_BGR2RGB)
        cv2.rectangle(current_image_copy,(x,y),(x+w,y+h),(255,255,255),2)


    binary_foreground_image = black
    colored_foreground_image = cv2.bitwise_and(current_image, current_image, mask = black.astype(np.uint8))
    display_image = cv2.resize(current_image_copy, (640,360))
    ssim = (ssim_1 + ssim_2)/2
    return colored_foreground_image, display_image, ssim
