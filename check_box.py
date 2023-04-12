from customtkinter import *
from PIL import Image, ImageDraw, ImageTk
from typing import Union, Tuple, List, Any, Literal, Callable, Optional
from colorsys import rgb_to_hls, hls_to_rgb
from PyAnimator.PyAnimator import Animator
import threading

SPAWN = 'spawn'
DESTROY = 'destroy'
ON = 'on'
OFF = 'off'

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

class CheckBox(CTkFrame):
    def __init__(self, master, radius: int = 30, inner_border_width: int = 5, border_width: int = 2, default_state: bool = False, callback: Callable = None):
        """
        Master : Parent widget\n
        radius : radius of the checkbox\n
        inner_border_width : the border width of the checkbox checked. inner border width must be smaller than half of radius(<radius/2)\n
        border_width : the border width of the checkbox\n
        default_state : the current state of the checkbox\n
        callback : callable to be called when the checkbox is checked or unchecked
        """
        super().__init__(master, height=radius, width=radius,
                         bg_color='transparent', fg_color='transparent', border_width=0)

        self._master:CTkBaseClass = master  # master is parent widget of this widget
        self._RADIUS = radius
        self._check_border_width = border_width
        self._inner_radius = radius - inner_border_width * 2
        self._callback = callback
        self._color_1 = ThemeManager.theme["CTkCheckbox"]["fg_color"][0]
        self._color_2 = ThemeManager.theme["CTkCheckbox"]["border_color"][0]
        self._color_3 = ThemeManager.theme["CTkCheckbox"]["fg_color"][1]
        self._color_4 = ThemeManager.theme["CTkCheckbox"]["border_color"][1]
        self._update_image_colors()

        self._current_radius = 0
        self._current_inner_radius = 0
        self._current_color = self._back_color
        self._animation_on = True
        self._animating = False
        self._break_animation = False
        
        self._current_state = default_state
        self.bind('<Button>', self._change_state)

    def _animate_checkbox(self, mode, animate:bool=True):
        # def do():
            target_inner_radius = None
            target_radius = None
            target_color_saturation = None
            if mode == SPAWN:
                target_inner_radius = 0
                target_radius = self._RADIUS
                target_color_saturation = False
            elif mode == DESTROY:
                target_inner_radius = 0
                target_radius = 0
            
            if mode == ON or (mode == SPAWN and self._current_state):
                target_inner_radius = self._inner_radius
                target_color_saturation = True
            elif mode == OFF or (mode == SPAWN and not self._current_state):
                target_inner_radius = 0
                target_color_saturation = False
            
            if target_radius is None:
                target_radius = self._current_radius

            if target_inner_radius is None:
                target_inner_radius = self._current_inner_radius

            if target_color_saturation is not None:

                if target_color_saturation:
                    target_color = self._back_color
                else:
                    c = self._back_color.removeprefix('#')
                    r, g, b = int(c[0]+c[1], 16), int(c[2]+c[3], 16), int(c[4]+c[5], 16)
                    h, l, s = rgb_to_hls(r, g, b)
                    r, g, b = hls_to_rgb(h, l, 0)
                    target_color = '#'
                    for x in [r, g, b]:
                        x = hex(int(x))[2:]
                        if len(x) == 1: target_color += '0' + x
                        elif len(x) == 2: target_color += x
            else:
                target_color = self._current_color
            
            duration = 0.2
            fps = 60
            easing = 'ease'

            if animate and self._animation_on:

                if self._animating:
                    self._break_animation = True
                    self._current_state = not self._current_state
                    self.after(1, lambda : self._change_state(None))
                    return

                self._animating = True
                radius_animator = Animator(self._current_radius, target_radius, duration, fps, easing)
                inner_radius_animator = Animator(self._current_inner_radius, target_inner_radius, duration, fps, easing)
                color_animator = Animator(self._current_color, target_color, duration, fps, easing)

                for radius, inner_radius, color in zip(radius_animator,
                                                    inner_radius_animator.values,
                                                    color_animator.values):
                    self._render_checkbox(int(radius), int(inner_radius), color)

                    if self._break_animation:
                        break
                
                self._break_animation = False
                self._animating = False
                
            else:
                self._render_checkbox(target_radius, target_inner_radius, target_color)

        # self._animation_thread = threading.Thread(target=do)
        # self._animation_thread.start()
        # do()

    def _rerender(self):
        # self._render_checkbox(self._current_radius, self._current_inner_radius, self._current_color)
        self._animate_checkbox(ON if self._current_state else OFF)

    def _render_checkbox(self, radius, inner_radius, color) -> None:
        self._back_image = ImageTk.PhotoImage(create_rectangle(radius, radius, self._RADIUS/2, self._check_border_width, color, self._front_color))
        self._front_image = ImageTk.PhotoImage(create_rectangle(inner_radius, inner_radius, self._inner_radius/2, 0, self._front_color))
        self._canvas.create_image(self._RADIUS/2, self._RADIUS/2, image=self._back_image)
        self._canvas.create_image(self._RADIUS/2, self._RADIUS/2, image=self._front_image)
        self._current_radius = radius
        self._current_inner_radius = inner_radius
        self._current_color = color
        self.update()

    def _apply_appearance_mode(self, input: Union[Any, Tuple[Any, Any], List[Any]]) -> Any:
        """input can be either a single input or it can be a tuple input with(input_for_light, input_for_dark).
        The functions returns always a single input according to the theme mode (Light, Dark)."""
        return super()._apply_appearance_mode(input)

    def _update_image_colors(self):
        self._back_color = self._apply_appearance_mode((self._color_4, self._color_2))
        self._front_color = self._apply_appearance_mode((self._color_1, self._color_3))

    def _change_state(self, event=None, state:bool = None):
        if state is not None:
            self._current_state = state
            animate = ON if state else OFF
        else:
            if self._current_state:
                self._current_state = False
                animate = OFF
            else:
                self._current_state = True
                animate = ON
        self._call_callback()
        self._animate_checkbox(animate)

    def _animate_on_pack_grid_place(func):
        """If the parent widget of this widget is mapped, This will run 'spawn' animation when the pack, grid or place called."""
        def wrapper(self, **kwargs):
            ret = func(self, **kwargs)
            self:CheckBox = self
            threading.Thread(target=self._animate_checkbox, args=(SPAWN, self._master.winfo_viewable())).start()
            return ret
        return wrapper

    @_animate_on_pack_grid_place
    def pack(self, **kwargs):
        return super().pack(**kwargs)
    
    @_animate_on_pack_grid_place
    def grid(self, **kwargs):
        return super().grid(**kwargs)
    
    @_animate_on_pack_grid_place
    def place(self, **kwargs):
        return super().place(**kwargs)
    
    def get(self) -> bool:
        """Returns True if the checkbox is checked."""
        return self._current_state
    
    def set(self, state: bool) -> None:
        """Sets the checkbox to the given state"""
        self._change_state(state)

    def toggle(self) -> None:
        """Toggles the checkbox"""
        self._change_state()

    def animation(self, state: Optional[bool] = None) -> Optional[bool]:
        """Turns on or off the animations. if no perameter given, will return current animation state"""
        if state is not None:
            self._animation_on = state
        else:
            return self._animation_on

    def animate(self, anim: Literal['spawn', 'destroy', 'on', 'off']) -> None:
        if anim in [SPAWN, DESTROY, ON, OFF]:
            self._animate_checkbox(anim)
        else:
            raise ValueError("anim must be one 'spawn', 'destroy', 'on', or 'off'.")
        
    def _call_callback(self):
        if self._callback is not None:
            self._callback()

    def _draw(self, no_color_updates=False):
        if not no_color_updates:
            self._update_image_colors()
            self.after(1, self._rerender)
        return super()._draw(no_color_updates)



if __name__ == '__main__':
    root = CTk()

    cb = CheckBox(root)
    cb.pack(pady = 20)
    # root.after(1000, lambda: cb.pack(pady = 20))

    cb2 = CheckBox(root, 100, 10)
    cb2.pack(pady = 20)
    # root.after(1000, lambda: cb2.pack(pady = 20))

    cb3 = CTkCheckBox(root, checkbox_width=30, checkbox_height=30)
    cb3.pack(pady = 20)

    def run():
        for v in range(100):
            v = (100 - v) / 100
            cb.scale(cb._front, v,0, 1,1)
            root.update()
            root.after(100)

    # root.after(1000, run)

    root.attributes('-topmost', True)
    root.geometry()
    root.mainloop()