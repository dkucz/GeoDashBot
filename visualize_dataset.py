import csv
import os

import cv2


SESSION_DIR = "data/session_002"

VIDEO_PATH = os.path.join(
    SESSION_DIR,
    "gameplay.mp4"
)

LABELS_PATH = os.path.join(
    SESSION_DIR,
    "labels.csv"
)


# --------------------------------------------------
# Load labels
# --------------------------------------------------

labels = []

with open(LABELS_PATH, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        labels.append({
            "frame": int(row["frame"]),
            "timestamp": float(row["timestamp"]),
            "control": int(row["control"])
        })


print(f"Loaded {len(labels)} labels.")


# --------------------------------------------------
# Open video
# --------------------------------------------------

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("Could not open video.")
    exit()


video_fps = video.get(cv2.CAP_PROP_FPS)
video_frame_count = int(
    video.get(cv2.CAP_PROP_FRAME_COUNT)
)

print(f"Video FPS: {video_fps}")
print(f"Video frames: {video_frame_count}")


# --------------------------------------------------
# Display frames
# --------------------------------------------------

frame_index = 0

while True:

    success, frame = video.read()

    if not success:
        print("End of video.")
        break

    # Make sure we have a corresponding label
    if frame_index >= len(labels):
        break

    label = labels[frame_index]

    control = label["control"]

    if control == 1:
        action_text = "HOLD"
    else:
        action_text = "RELEASE"

    timestamp = label["timestamp"]

    # Add information to the frame
    cv2.putText(
        frame,
        f"Frame: {frame_index}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Time: {timestamp:.3f}",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Control: {action_text}",
        (10, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0) if control else (0, 0, 255),
        2
    )

    cv2.imshow(
        "Dataset Viewer",
        frame
    )

    # Wait for keyboard input
    key = cv2.waitKey(0) & 0xFF

    # q = quit
    if key == ord("q"):
        break

    # Right arrow / d = next frame
    elif key == ord("d"):
        frame_index += 1

    # Left arrow / a = previous frame
    elif key == ord("a") and frame_index > 0:

        # Re-open video and jump back one frame
        video.set(
            cv2.CAP_PROP_POS_FRAMES,
            frame_index - 1
        )

        frame_index -= 1

    else:
        # Any other key advances
        frame_index += 1


video.release()
cv2.destroyAllWindows()