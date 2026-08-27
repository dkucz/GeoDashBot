import csv
import os
import sys


# --------------------------------------------------
# Get session number
# --------------------------------------------------

if len(sys.argv) > 1:
    session_number = int(sys.argv[1])
else:
    session_number = int(
        input("Enter session number: ")
    )


SESSION_DIR = f"data/session_{session_number:03d}"

ACTIONS_PATH = os.path.join(
    SESSION_DIR,
    "actions.csv"
)

FRAME_TIMESTAMPS_PATH = os.path.join(
    SESSION_DIR,
    "frame_timestamps.csv"
)

OUTPUT_PATH = os.path.join(
    SESSION_DIR,
    "labels.csv"
)


# --------------------------------------------------
# Check session exists
# --------------------------------------------------

if not os.path.exists(SESSION_DIR):
    print(f"Session not found: {SESSION_DIR}")
    sys.exit(1)


if not os.path.exists(ACTIONS_PATH):
    print(f"Missing file: {ACTIONS_PATH}")
    sys.exit(1)


if not os.path.exists(FRAME_TIMESTAMPS_PATH):
    print(f"Missing file: {FRAME_TIMESTAMPS_PATH}")
    sys.exit(1)


print(f"Processing {SESSION_DIR}")
print()


# --------------------------------------------------
# Load keyboard events
# --------------------------------------------------

events = []

with open(ACTIONS_PATH, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        events.append({
            "timestamp": float(row["timestamp"]),
            "key": row["key"],
            "event": row["event"]
        })


events.sort(key=lambda event: event["timestamp"])

print(f"Found {len(events)} keyboard events.")


# --------------------------------------------------
# Load frame timestamps
# --------------------------------------------------

frames = []

with open(FRAME_TIMESTAMPS_PATH, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        frames.append({
            "frame": int(row["frame"]),
            "timestamp": float(row["timestamp"])
        })


print(f"Found {len(frames)} frames.")


# --------------------------------------------------
# Reconstruct control state
# --------------------------------------------------

labels = []

space_held = False
up_held = False

event_index = 0


for frame in frames:

    frame_number = frame["frame"]
    frame_time = frame["timestamp"]

    # Apply all keyboard events that happened
    # before this frame.
    while (
        event_index < len(events)
        and events[event_index]["timestamp"] <= frame_time
    ):

        event = events[event_index]

        if event["key"] == "space":
            space_held = event["event"] == "press"

        elif event["key"] == "up":
            up_held = event["event"] == "press"

        event_index += 1

    # HOLD = 1
    # RELEASE = 0
    control = 1 if (space_held or up_held) else 0

    labels.append({
        "frame": frame_number,
        "timestamp": frame_time,
        "control": control
    })


# --------------------------------------------------
# Save labels
# --------------------------------------------------

with open(OUTPUT_PATH, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "frame",
        "timestamp",
        "control"
    ])

    for label in labels:
        writer.writerow([
            label["frame"],
            label["timestamp"],
            label["control"]
        ])


# --------------------------------------------------
# Statistics
# --------------------------------------------------

hold_frames = sum(
    label["control"] == 1
    for label in labels
)

release_frames = len(labels) - hold_frames


print()
print("Preprocessing complete.")
print(f"Session:        {session_number:03d}")
print(f"Total frames:   {len(labels)}")
print(f"Hold frames:    {hold_frames}")
print(f"Release frames: {release_frames}")
print(f"Saved to:       {OUTPUT_PATH}")