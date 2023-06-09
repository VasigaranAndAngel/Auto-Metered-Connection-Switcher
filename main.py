from customtkinter import *
from exclude import Exclude, UNRESTRICTED, FIXED, NOTHING, OFF
from triple_state_switch import Switch
from loading import Loading
from MeteredOnOff import MeteredOnOff
from check_box import CheckBox
import threading
from pyautogui import position as pointer_position

def add_tray_icon():
    from tray_icon import activate_tray_icon
    activate_tray_icon(_on_open, _on_exit)


class UI(CTk):
    def __init__(self):
        super().__init__()
        self.title('Metered Connection')

        self.status_bar = CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.pack(fill=X)

        self.loading_bar = Loading(self.status_bar, height=4)
        self.loading_bar.pack(fill=X)

        self.status_label = CTkLabel(self.status_bar, text='', font=('Maiandra GD', 15))
        self.status_label.pack(side=RIGHT, padx=10)
        self.status_label.bind('<Button>', self._immediate_refresh)

        self.new_entry_frame = CTkFrame(self.status_bar, height=30, width=150, fg_color='transparent', bg_color='transparent')
        self.new_entry_frame.pack(side=LEFT, padx=5, pady=2)

        self.new_entry = CTkEntry(self.new_entry_frame, corner_radius=50, width=150, font=('Maiandra GD', 15))
        self.new_entry.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.new_entry.bind('<Return>', lambda e: self._add_new_entry())

        self.add_button = CTkButton(self.new_entry_frame, 0, 0, text="+", command=self._add_new_entry, border_width=0,
                                    hover_color=ThemeManager.theme["CTkEntry"]["fg_color"], fg_color=ThemeManager.theme["CTkEntry"]["fg_color"], bg_color=ThemeManager.theme["CTkEntry"]["fg_color"])
        self.add_button.place(relx=0.9, rely=0.5, anchor=E)
        # self.add_button = CTkLabel(self.new_entry_frame, 0, 0, text="+",
        #                             fg_color=ThemeManager.theme["CTkEntry"]["fg_color"])
        # self.add_button.place(relx=0.9, rely=0.5, anchor=E)

        self.excludes = Exclude()
        self.type_to_state = {UNRESTRICTED: LEFT, FIXED: RIGHT, NOTHING: CENTER}
        
        self.scrollable_frame = None

        self.after(100, self._draw_list)
        
    def _add_new_entry(self):
        name = self.new_entry.get()
        # name_list = [name == x[0] for x in self.frame_list.keys()]
        if name and all(name != x for x in self.frame_list):
            exclude_type = NOTHING
            switch_state = self.type_to_state[exclude_type]
            ssid_name = name
            self.excludes.add_to_nothing(name)

            if self.scrollable_frame is None and len(self.excludes.get_all_exclude()) > 10:
                self._redraw_list()
            else:
                self._add_frame_to_list(ssid_name, exclude_type, switch_state, )

    def _add_frame_to_list(self, ssid_name, exclude_type, switch_state):
        off = False
        if len(types:=self.excludes.get_exclude_type(ssid_name)) > 1:
            if OFF in types:
                off = True
        def update_state(ssid_name=ssid_name):
            exclude_type = self.excludes.get_exclude_type(ssid_name)[0].title()
            self.frame_list[ssid_name][2].configure(text=exclude_type)
            self.update()

        def switch_callback(state, ssid_name=ssid_name):
            if state == self.type_to_state[UNRESTRICTED]:
                self.excludes.add_to_unrestricted(ssid_name)
            elif state == self.type_to_state[FIXED]:
                self.excludes.add_to_fixed(ssid_name)
            elif state == self.type_to_state[NOTHING]:
                self.excludes.add_to_nothing(ssid_name)
            update_state(ssid_name=ssid_name)

        def on_delete(ssid_name=ssid_name):
            self.excludes.remove(ssid_name, ALL)
            self.excludes.remove(ssid_name, OFF)
            
            if self.scrollable_frame is not None and len(self.excludes.get_all_exclude()) <= 10:
                self._redraw_list()
            else:
                self.frame_list[ssid_name][0].destroy()
                self.frame_list.pop(ssid_name)

        def on_on_off(ssid_name=ssid_name):
            state = self.frame_list[ssid_name][4].get()
            if state:
                if OFF in self.excludes.get_exclude_type(ssid_name):
                    self.excludes.remove(ssid_name, OFF)
            else:
                self.excludes.add_to_off(ssid_name)

        frame = CTkFrame(self.list_frame, 300, 30, fg_color='transparent')
        frame.pack_propagate(False)
        frame.pack(fill=X, padx=10)
        frame.bind('<Button>', lambda e: on_off_checkbox.toggle())
        frame.update()

        remove_button = CTkButton(frame, 30, 20, text='X', command=on_delete)
        remove_button.pack(side=RIGHT)

        on_off_checkbox = CheckBox(frame, 20, 5, default_state=(not off), callback=on_on_off)
        on_off_checkbox.pack(side=LEFT, padx=(0, 10))

        ssid_label = CTkLabel(frame, text=ssid_name, font=('Maiandra GD', 15))
        # ssid_label.place(anchor=W, relx=0, rely=0.5)
        ssid_label.pack(side=LEFT)
        ssid_label.bind('<Button>', lambda e: on_off_checkbox.toggle())

        state_switch = Switch(frame, width=60, height=20, default_state=switch_state, callback=switch_callback)
        # state_switch.place(anchor=CENTER, relx=0.5, rely=0.5)
        state_switch.pack(side=RIGHT, padx=10)

        state_label = CTkLabel(frame, text=exclude_type.title(), font=('Maiandra GD', 15), width=70)
        # state_label.place(anchor=E, relx=0.8, rely=0.5)
        state_label.pack(side=RIGHT, padx=10)
            
        self.frame_list[ssid_name] = ([frame, ssid_label, state_label, state_switch, on_off_checkbox])

    def _draw_list(self):
        self.frame_list = {}
        all_exclude = self.excludes.get_all_exclude()
        self.loading_bar.set_progress_amount(len(all_exclude))
        
        if len(self.excludes.get_all_exclude()) > 10:
            self.scrollable_frame = CTkScrollableFrame(self, 320, 30*10)
            self.scrollable_frame.pack()
            self.list_frame = self.scrollable_frame
        else:
            self.list_frame = self

        for exclude in all_exclude:

            exclude_type = self.excludes.get_exclude_type(exclude)[0]
            switch_state = self.type_to_state[exclude_type]
            ssid_name = exclude

            self._add_frame_to_list(ssid_name, exclude_type, switch_state)
            
            self.loading_bar.progress_completed(update=True)

    def _redraw_list(self):
        if self.scrollable_frame is not None:
            self.scrollable_frame.pack_forget()
            self.scrollable_frame.destroy()
            self.scrollable_frame = None
        else:
            for ssid_name in list(self.frame_list.keys()):
                frame, *_ = self.frame_list.pop(ssid_name)
                frame.destroy()
        self._draw_list()

    def _immediate_refresh(self, event=None):
        immediate_refresh()

def on_status_change():
    if root is not None:
        root.status_label.configure(text=metered_on_off.status)

def immediate_refresh():
    metered_on_off.immediate_refresh()

metered_on_off = MeteredOnOff(on_status_change)
threading.Thread(target=metered_on_off.main).start()

root = None
def _on_open():
    global root
    if root is None:
        root = UI()
        set_appearance_mode('system')
        # root.geometry('350x338+300+300')
        w, h = 370, 338
        pointer_x, pointer_y = pointer_position()
        x, y = pointer_x - (w // 2), pointer_y - h - 47 - 30  # 47 = hight of taskbar, 30 = hight of window title bar
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        root.resizable(False, False)
        root.attributes('-topmost', True)
        root.mainloop()
        root = None

def _on_exit():
    global root
    metered_on_off.kill = True
    if root is not None:
        root.destroy()

add_tray_icon()
# root.after(1000, lambda : threading.Thread(target=add_tray_icon).start())
# root.after(1000, add_tray_icon)
# root.attributes('-topmost', True)
# root.geometry('+1500+720')
# root.mainloop()
