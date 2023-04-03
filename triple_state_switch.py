from customtkinter import *
from PIL import Image, ImageDraw, ImageTk
from typing import Callable, Literal

def create_rectangle(
        width: int = 100,
        height: int = 100,
        corner_radius: int = 20,
        border_width: int = 2,
        background_color: str = 'white',
        border_color: str = 'black'):
    scale = 4
    img = Image.new("RGBA", (width * scale, height * scale))
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width * scale, height * scale), corner_radius * scale, fill=255)
    img.paste(background_color, (0, 0, width * scale, height * scale), mask)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width * scale, height * scale), corner_radius * scale, outline=border_color, width=border_width * scale)
    img = img.resize((width, height), Image.LANCZOS)
    return img


class Switch(CTkFrame):
    def __init__(self, master, default_state: Literal['left', 'right', 'center']=CENTER, callback:Callable=None, width: int=80, height: int=30):
        super().__init__(master, width, height, bg_color='transparent', fg_color='transparent')
        self.WIDTH = width
        self.HEIGHT = height
        self.button_width = self.WIDTH//2
        self.corner_radius = self.HEIGHT // 2
        self.border_width         = ThemeManager.theme["CTkSwitch"]["border_width"]
        self.fg_color             = ThemeManager.theme["CTkSwitch"]["fg_Color"]
        self.button_color         = ThemeManager.theme["CTkSwitch"]["progress_color"]
        self.border_color         = ThemeManager.theme["CTkSwitch"]["progress_color"]
        self.button_hover_color   = ThemeManager.theme["CTkSwitch"]["button_hover_color"]

        # self.back_image  = CTkImage(create_rectangle(width=self.WIDTH, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[0], background_color=self.fg_color[0]),
        #                             create_rectangle(width=self.WIDTH, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[1], background_color=self.fg_color[1]), (self.WIDTH, self.HEIGHT))
        # self.front_image = CTkImage(create_rectangle(width=self.button_width, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[0], background_color=self.button_color[0]),
        #                             create_rectangle(width=self.button_width, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[1], background_color=self.button_color[1]), (self.button_width, self.HEIGHT))

        # self.back_image_light = ImageTk.PhotoImage(create_rectangle(width=self.WIDTH, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[0], background_color=self.fg_color[0]))
        # self.back_image_dark = ImageTk.PhotoImage(create_rectangle(width=self.WIDTH, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[1], background_color=self.fg_color[1]))
        # self.front_image_light = ImageTk.PhotoImage(create_rectangle(width=self.button_width, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[0], background_color=self.button_color[0]))
        # self.front_image_dark = ImageTk.PhotoImage(create_rectangle(width=self.button_width, height=self.HEIGHT, corner_radius=self.corner_radius,
        #                                             border_color=self.border_color[1], background_color=self.button_color[1]))

        self.switch_state = default_state # switch state will change to default state when drawing the images
        self.callback = callback

        self.draw_images()
        self.bind('<Button>', self._on_click)

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        self.draw_images()

    def draw_images(self):
        # redrawing all the images to avoid aliasing issues
        if self._get_appearance_mode() == 'light':
            self.back_img = ImageTk.PhotoImage(create_rectangle(width=self.WIDTH, height=self.HEIGHT, corner_radius=self.corner_radius,
                                                    border_color=self.border_color[0], background_color=self.fg_color[0]))
            self.front_img = ImageTk.PhotoImage(create_rectangle(width=self.button_width, height=self.HEIGHT, corner_radius=self.corner_radius,
                                                    border_color=self.border_color[0], background_color=self.button_color[0]))
        elif self._get_appearance_mode() == 'dark':
            self.back_img = ImageTk.PhotoImage(create_rectangle(width=self.WIDTH, height=self.HEIGHT, corner_radius=self.corner_radius,
                                                    border_color=self.border_color[1], background_color=self.fg_color[1]))
            self.front_img = ImageTk.PhotoImage(create_rectangle(width=self.button_width, height=self.HEIGHT, corner_radius=self.corner_radius,
                                                    border_color=self.border_color[1], background_color=self.button_color[1]))
                                                    
        self.button_back  = self._canvas.create_image(self.WIDTH//2, self.HEIGHT//2, image=self.back_img)
        self.button_front = self._canvas.create_image(self.WIDTH//2, self.HEIGHT//2, image=self.front_img)
        self._move_to(self.switch_state) # return to the current state if the switch redrawn.

    def _on_click(self, event):
        if event.num == 1: # if the switch is left clicked
            order = [RIGHT, CENTER, LEFT]
        elif event.num == 3: # if the switch is right clicked
            order = [LEFT, CENTER, RIGHT]
        else: return

        if self.switch_state == order[0]:
            self._move_to(order[1])
        elif self.switch_state == order[1]:
            self._move_to(order[2])
        elif self.switch_state == order[2]:
            self._move_to(order[0])
        self._callback()

    def _move_to(self, to: str):
        if to == LEFT:
            self._canvas.moveto(self.button_front, self.WIDTH//2, '')
            self.switch_state = LEFT
        elif to == RIGHT:
            self._canvas.moveto(self.button_front, 0, '')
            self.switch_state = RIGHT
        elif to == CENTER:
            self._canvas.moveto(self.button_front, self.WIDTH//4, '')
            self.switch_state = CENTER

    def _callback(self):
        if self.callback is not None:
            self.callback(self.switch_state)

    def get_state(self):
        return self.switch_state


if __name__ == '__main__':
    root = CTk()
    # root.wm_attributes('-transparentcolor', '#ab23ff')

    def callback(state):
        print(state)

    switch = Switch(root, callback=callback)
    switch.pack(padx=100, pady=100)

    root.attributes('-topmost', True)
    root.mainloop()