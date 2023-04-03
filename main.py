from customtkinter import *
from exclude import Exclude, UNRESTRICTED, FIXED, NOTHING
from triple_state_switch import Switch
from loading import Loading
import threading

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

        self.label = CTkLabel(self.status_bar, text='Nothing....')
        self.label.pack(side=RIGHT, padx=10)

        self.new_entry_frame = CTkFrame(self.status_bar, height=30, width=150, fg_color='transparent', bg_color='transparent')
        self.new_entry_frame.pack(side=LEFT, padx=5, pady=2)

        self.new_entry = CTkEntry(self.new_entry_frame, corner_radius=50, width=150)
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

        self._draw_list()
        
    def _add_new_entry(self):
        name = self.new_entry.get()
        name_list = [x[0] for x in self.frame_list]
        if name and name not in name_list:
            id = len(name_list)
            exclude_type = NOTHING
            switch_state = self.type_to_state[exclude_type]
            ssid_name = name

            self._add_frame_to_list(id, exclude_type, switch_state, ssid_name)
            

    def _add_frame_to_list(self, id, exclude_type, switch_state, ssid_name):
        def update_state(id=id):
            ssid_name = self.frame_list[id][0]
            exclude_type = self.excludes.get_exclude_type(ssid_name)[0]
            self.frame_list[id][3].configure(text=exclude_type)
            self.update()

        def switch_callback(state, id=id):
            if state == self.type_to_state[UNRESTRICTED]:
                self.excludes.add_to_unrestricted(self.frame_list[id][0])
            elif state == self.type_to_state[FIXED]:
                self.excludes.add_to_fixed(self.frame_list[id][0])
            elif state == self.type_to_state[NOTHING]:
                self.excludes.add_to_nothing(self.frame_list[id][0])
            update_state(id=id)

        def on_delete(id=id):
            name = self.frame_list[id][0]
            self.excludes.remove(name)
            self.frame_list[id][1].destroy()

        frame = CTkFrame(self, 300, 30, fg_color='transparent')
        frame.pack_propagate(False)
        frame.pack(fill=X, padx=10)

        remove_button = CTkButton(frame, 30, 20, text='X', command=on_delete)
        remove_button.pack(side=RIGHT)

        ssid_label = CTkLabel(frame, text=ssid_name)
        # ssid_label.place(anchor=W, relx=0, rely=0.5)
        ssid_label.pack(side=LEFT)

        state_switch = Switch(frame, width=60, height=20, default_state=switch_state, callback=switch_callback)
        # state_switch.place(anchor=CENTER, relx=0.5, rely=0.5)
        state_switch.pack(side=RIGHT, padx=10)

        state_label = CTkLabel(frame, text=exclude_type, width=70)
        # state_label.place(anchor=E, relx=0.8, rely=0.5)
        state_label.pack(side=RIGHT, padx=10)
            
        self.frame_list.append([ssid_name, frame, ssid_label, state_label, state_switch])

    def _draw_list(self):
        self.frame_list = []
        all_exclude = self.excludes.get_all_exclude()
        self.loading_bar.set_progress_amount(len(all_exclude))

        for id, exclude in enumerate(all_exclude):

            exclude_type = self.excludes.get_exclude_type(exclude)[0]
            switch_state = self.type_to_state[exclude_type]
            ssid_name = exclude

            self._add_frame_to_list(id, exclude_type, switch_state, ssid_name)
            
            self.loading_bar.progress_completed(update=True)

    def _redraw_list(self):
        while self.frame_list:
            name, frame, _, _, _ = self.frame_list.pop()
            frame.destroy()
        self._draw_list()

root = None
def _on_open():
    global root
    if root is None:
        root = UI()
        root.mainloop()
        root = None

def _on_exit():
    global root
    if root is not None:
        root.destroy()

add_tray_icon()
# root.after(1000, lambda : threading.Thread(target=add_tray_icon).start())
# root.after(1000, add_tray_icon)
# root.attributes('-topmost', True)
# root.geometry('+1500+720')
# root.mainloop()
