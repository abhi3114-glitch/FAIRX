import cv2

print("Testing camera index 1...")

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ FAILED to open camera at index 1")
    print("\nTrying to list all available cameras:")
    for i in range(5):
        test_cap = cv2.VideoCapture(i)
        if test_cap.isOpened():
            print(f"✅ Camera found at index {i}")
            test_cap.release()
        else:
            print(f"❌ No camera at index {i}")
    exit(1)

print("✅ Camera opened successfully!")
print("Press 'q' to quit")

frame_count = 0
while True:
    ret, frame = cap.read()
    if ret:
        frame_count += 1
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Camera Test", frame)
        print(f"Frame {frame_count} - Shape: {frame.shape}")
    else:
        print("❌ Failed to read frame")
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"\nTotal frames captured: {frame_count}")