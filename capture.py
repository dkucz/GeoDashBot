import csv
import json
import os
import time

import mss
import cv2
import numpy as np
from pynput import keyboard


FPS = 60

keyboard_events = []
stop_capture = False


def on_press(key):
    timestamp = time.perf_counter()

    if key == keyboard.Key.space:
        keyboard_events.append((timestamp, "space", "press"))

    elif key == keyboard.Key.up:
        keyboard_events.append((timestamp, "up", "press"))

    elif key == keyboard.Key.esc:
        global stop_capture
        stop_capture = True
        return False


def on_release(key):
    timestamp = time.perf_counter()

    if key == keyboard.Key.space:
        keyboard_events.append((timestamp, "space", "release"))

    elif key == keyboard.Key.up:
        keyboard_events.append((timestamp, "up", "release"))


# --------------------------------------------------
# Create session directory
# --------------------------------------------------

os.makedirs("data", exist_ok=True)

session_number = len(
    [
        name
        for name in os.listdir("data")
        if name.startswith("session_")
    ]
) + 1

session_dir = f"data/session_{session_number:03d}"
os.makedirs(session_dir, exist_ok=True)

video_path = os.path.join(session_dir, "gameplay.mp4")
actions_path = os.path.join(session_dir, "actions.csv")
timestamps_path = os.path.join(session_dir, "frame_timestamps.csv")
metadata_path = os.path.join(session_dir, "metadata.json")


# --------------------------------------------------
# Start keyboard listener
# --------------------------------------------------

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

listener.start()


# --------------------------------------------------
# Screen capture
# --------------------------------------------------

with mss.MSS() as sct:

    monitor = sct.monitors[1]

    # Screenshot used for region selection
    screenshot = sct.grab(monitor)

    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    region = cv2.selectROI(
        "Select Geometry Dash Region",
        frame,
        fromCenter=False,
        showCrosshair=True
    )

    cv2.destroyWindow("Select Geometry Dash Region")

    x, y, width, height = region

    if width == 0 or height == 0:
        print("No region selected.")
        listener.stop()
        exit()

    game_region = {
        "top": monitor["top"] + y,
        "left": monitor["left"] + x,
        "width": width,
        "height": height
    }

    print("Selected region:")
    print(game_region)

    # --------------------------------------------------
    # Create video writer
    # --------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video_writer = cv2.VideoWriter(
        video_path,
        fourcc,
        FPS,
        (width, height)
    )

    if not video_writer.isOpened():
        print("Could not open video writer.")
        listener.stop()
        exit()

    print()
    print("================================")
    print("Recording started")
    print("Press SPACE or UP to jump")
    print("Press ESC to stop")
    print("================================")
    print()

    # This is the reference time for the entire session.
    session_start = time.perf_counter()

    frame_count = 0
    frame_timestamps = []

    next_frame = session_start

    # --------------------------------------------------
    # Main recording loop
    # --------------------------------------------------

    while not stop_capture:

        frame_start = time.perf_counter()

        screenshot = sct.grab(game_region)

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Save frame to video
        video_writer.write(frame)

        # Record the actual timestamp of this frame
        frame_timestamps.append(
            (frame_count, frame_start)
        )

        # Show live capture
        cv2.imshow("Geometry Dash Recording", frame)

        frame_count += 1

        # Maintain approximately 60 FPS
        next_frame += 1 / FPS

        sleep_time = next_frame - time.perf_counter()

        if sleep_time > 0:
            time.sleep(sleep_time)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_writer.release()
    cv2.destroyAllWindows()


listener.stop()


# --------------------------------------------------
# Save keyboard events
# --------------------------------------------------

with open(actions_path, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "timestamp",
        "key",
        "event"
    ])

    writer.writerows(keyboard_events)


# --------------------------------------------------
# Save frame timestamps
# --------------------------------------------------

with open(timestamps_path, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "frame",
        "timestamp"
    ])

    writer.writerows(frame_timestamps)


# --------------------------------------------------
# Save metadata
# --------------------------------------------------

metadata = {
    "fps_target": FPS,
    "frame_count": frame_count,
    "width": width,
    "height": height,
    "session_start": session_start,
    "capture_region": game_region
}

with open(metadata_path, "w") as file:
    json.dump(metadata, file, indent=4)


# --------------------------------------------------
# Print summary
# --------------------------------------------------

session_duration = time.perf_counter() - session_start

print()
print("================================")
print("Recording finished")
print("================================")
print(f"Session: {session_dir}")
print(f"Frames: {frame_count}")
print(f"Duration: {session_duration:.2f} seconds")
print(f"Approx FPS: {frame_count / session_duration:.2f}")
print(f"Keyboard events: {len(keyboard_events)}")
print()
print(f"Video:      {video_path}")
print(f"Actions:    {actions_path}")
print(f"Timestamps: {timestamps_path}")
print(f"Metadata:   {metadata_path}")