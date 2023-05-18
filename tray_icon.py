from PIL import Image
from pystray import *

def activate_tray_icon(on_open=None, on_exit=None, on_pause=None):

    def _on_open(icon):
        if on_open is not None:
            on_open()

    def _on_exit(icon):
        if on_exit is not None:
            on_exit()
        icon.stop()

    def _on_pause(icon):
        if on_pause is not None:
            on_pause()

    menu = Menu(
        MenuItem("Open", _on_open, default=True),
        MenuItem("Pause for", Menu(
            MenuItem("1 Minute", _on_pause)
            )
                 ),
        MenuItem("Exit", _on_exit),
    )
    
    icon_image = Image.open("icons\\wifi-regular-24-white.png")

    tray_icon = Icon("My Icon", icon_image, "Metered Connection", menu)
    tray_icon.run()

# test
if __name__ == "__main__":
    activate_tray_icon()