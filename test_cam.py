import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Camera Test", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
