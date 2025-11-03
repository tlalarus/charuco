import cv2
import numpy as np


print('opencv version: ', cv2.__version__) 
print()

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

# 입력값
dpi = 300

square_x_count = 9
square_y_count = 6
square_length_mm = 85
marker_length_mm = 40

bg_width_mm = 800
bg_height_mm = 600

width_mm = square_x_count * square_length_mm
height_mm = square_y_count * square_length_mm

margin_minimum_mm = 0 # 양쪽 마진 최소값 

display_scale = 0.2

remain_width = width_mm - (square_x_count * square_length_mm)
remain_height = height_mm - (square_y_count * square_length_mm)
print('remain_width_mm: ', remain_width)
print('remain_height_mm: ', remain_height)
print()

# margin_mm = min([remain_width, remain_height])
margin_mm = 0
print('margin_mm: ', margin_mm)

### Verify
width_total_mm = square_x_count * square_length_mm + (margin_mm)
height_total_mm = square_y_count * square_length_mm + (margin_mm)


print('width_total_mm: ', width_total_mm)
print('height_total_mm: ', height_total_mm)

if(width_total_mm > width_mm):
  print('width is too long !!!')
  quit()

if(height_total_mm > height_mm):
  print('height is too long !!!')
  quit()

if(margin_mm < margin_minimum_mm):
  print('margin is too short !!!')
  quit()

### Calculate
width_inch = width_mm / 25.4
height_inch = height_mm / 25.4

width_px = int(width_inch * dpi)
height_px = int(height_inch * dpi)

margin_px = int(margin_mm / 25.4 * dpi / 2)

width_without_margin_px = int(width_total_mm / 25.4 * dpi)
height_without_margin_px = int(height_total_mm / 25.4 * dpi)


print()
print('resolution px: ', width_px, height_px)
print('margin px: ', margin_px)


board = cv2.aruco.CharucoBoard(
  size=(square_x_count, square_y_count),
  squareLength=square_length_mm * 0.001,
  markerLength=marker_length_mm * 0.001,
  dictionary=dictionary
)

  # outSize=(9449, 7087),
img = board.generateImage(
  outSize=(width_without_margin_px, height_without_margin_px),
  borderBits=1,
  marginSize=margin_px
)

bg_width_px = int(bg_width_mm / 25.4 * dpi)
bg_height_px = int(bg_height_mm / 25.4 * dpi)
background = np.ones((bg_height_px, bg_width_px, 3), dtype=np.uint8) * 255

print('background resolution: ', bg_width_px, bg_height_px)

# calculate center position
top = (bg_height_px - height_without_margin_px) // 2
left = (bg_width_px - width_without_margin_px) // 2
print('background insert position: ', top, left)

bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
background[top:top + height_without_margin_px, left:left + width_without_margin_px] = bgr

new_size = (int(width_px*display_scale), int(height_px*display_scale))
img_display = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

display_size_bg = (int(bg_width_px*display_scale), int(bg_height_px*display_scale))
background_display = cv2.resize(background, display_size_bg, interpolation=cv2.INTER_AREA)

# cv2.imshow("calibration target", img_display)
cv2.imshow("calibration target", background_display)
cv2.waitKey(0)

fileName = "charuco_{}x{}_{}x{}_{}_{}".format(bg_width_mm, bg_height_mm, square_x_count, square_y_count, square_length_mm, marker_length_mm)

pngName = fileName + '.png'
cv2.imwrite(pngName, background)
cv2.imwrite('./without_margin/'+pngName, img)

from PIL import Image

pdfName = fileName + '.pdf'
Image.open(pngName).convert('RGB').save(pdfName, 'PDF', resolution=300.0)

# 2.7, 1.4