import numpy as np
import cv2
import time

date=time.strftime("%Y-%m-%d_%H-%M")
print(date)

cap = cv2.VideoCapture(1)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(f'{date}_output.avi', fourcc, 20.0, (640, 480))

n=20*60*1
for i in range(n):
	ret, frame = cap.read() 
	out.write(frame)
	cv2.imshow('Original', frame)
	 
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break


cap.release()
out.release()
cv2.destroyAllWindows()