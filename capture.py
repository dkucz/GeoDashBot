import mss
import cv2
import numpy as np

with mss.mss() as sct:
    monitor = sct.monitors[1]

    while True:
        screenshot = sct.grab(monitor)

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        cv2.imshow("Geometry Dash Capture", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()