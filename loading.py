import customtkinter
import threading

class UI:
    def __init__(self):
        pass

class Loading(customtkinter.CTkProgressBar):
    def __init__(self, root=None, frame_per_second = 20, anim_milli_seconds = 1000, *args, **kwargs):
        """Loading progress bar widget"""

        super().__init__(root, *args, **kwargs)
        super().set(0.0)

        self.progress_amount = 1 # default value
        self.progress_complete = 0

        self.frames = anim_milli_seconds / 1000 * frame_per_second
        self.frame_per_second = frame_per_second
        self.anim_milli_seconds = anim_milli_seconds
        
        self.frame_count = 0
        self.break_anim = False

    def progress_completed(self, amount: int = 1, update: bool = False):
        self.progress_complete += amount
        if update: self.update()

        self.progress_value = (self.progress_complete / self.progress_amount) - self.get()
        self.set(self.progress_value + self.get())
        # print(self.progress_value)

        # self.frame_count = 1
        # self.break_anim = True
        # self.break_anim = False    
        # self._anim_set_progress()

    def set_progress_amount(self, amount):
        if amount == 0:
            self._progress_amount = 1
            self.progress_completed(1)
        self.progress_amount = amount

    def reset_progress_complete(self, update: bool = False):
        self.progress_complete = 0
        self.set(0.0)
        if update: self.update()

    def _anim_set_progress(self):
        while self.frame_count <= self.frames:
            value_for_frame = (self.progress_value / self.frames) + self.get()
            self.set(value_for_frame)
            self.frame_count += 1
            if self.break_anim: break
            customtkinter.CTk().after(int(self.anim_milli_seconds / self.frame_per_second), 'idle')
            print(value_for_frame, self.frame_count, self.frames, self.progress_complete)
            if self.break_anim: break


# for test
if __name__ == "__main__":

    from time import sleep

    def action():
        for i in range(4):
            loading.progress_completed(2)
            sleep(0.1)
            root.update()

    root = customtkinter.CTk()

    button = customtkinter.CTkButton(root, command=action)
    button.pack()

    loading = Loading(root, width=500, height=5, frame_per_second=60)
    loading.pack(padx=10, pady=10)

    loading.set_progress_amount(10)

    root.mainloop()