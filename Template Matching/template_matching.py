# test based on the example given by the OpenCV official documentation https://docs.opencv.org/trunk/d4/dc6/tutorial_py_template_matching.html

import cv2 as cv
from matplotlib import pyplot as plt

# read images
img = cv.imread('test_black.png', 0)
template = cv.imread('template_rad_th_2.png', 0)

# getting template chape to draw the rectangle
w, h = template.shape[::-1]
img_final = img.copy()

# selecting the correlation method
method = eval('cv.TM_CCOEFF_NORMED')

# applying template matching
res = cv.matchTemplate(img_final, template, method)

# getting max / min values
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
top_left = max_loc

# drawing result
bottom_right = (top_left[0] + w, top_left[1] + h)
cv.rectangle(img, top_left, bottom_right, 255, 2)
plt.imshow(img, cmap='gray')
plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
plt.show()
