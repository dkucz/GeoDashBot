from pynput import keyboard


def on_press(key):
    if key == keyboard.Key.space:
        print("SPACE pressed")

    elif key == keyboard.Key.up:
        print("UP pressed")


def on_release(key):
    if key == keyboard.Key.space:
        print("SPACE released")

    elif key == keyboard.Key.up:
        print("UP released")

    elif key == keyboard.Key.esc:
        print("Stopping...")
        return False


with keyboard.Listener(
    on_press=on_press,
    on_release=on_release
) as listener:
    print("Listening for Space and Up Arrow...")
    print("Press ESC to stop.")

    listener.join()