# test_opencv_display.py
import cv2

# Create a simple image using numpy
import numpy as np
image = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(image, 'OpenCV Display Test', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

cv2.imshow('Test Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()