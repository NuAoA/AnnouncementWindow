import io
import os
import subprocess
import sys
if sys.version_info.major == 2:
    import Tkinter
    import tkMessageBox
elif sys.version_info.major == 3:
    import tkinter as Tkinter
    import tkinter.messagebox as tkMessageBox
import util

def native_open(filename):
    try:
        if util.platform.osx:
            subprocess.call(("open", filename))
        elif util.platform.win:
            os.startfile(filename)
        elif util.platform.linux:
            subprocess.call(("xdg-open", filename))
    except Exception:
        pass

class TextEditor(Tkinter.Toplevel):
    def __init__(self, filename):
        Tkinter.Toplevel.__init__(self)
        try:
            with io.open(filename) as f:
                self.buffer = f.read().rstrip("\n")
        except IOError:
            self.destroy()
            tkMessageBox.showerror(message="Could not open file: %s" % filename)
            return
        self.filename = filename

        self.menu = Tkinter.Menu(self)
        file_menu = Tkinter.Menu(self.menu)
        file_menu.add_command(label="Save", command=self.save, accelerator="S")
        file_menu.add_command(label="Revert", command=self.revert, accelerator="R")
        self.menu.add_cascade(menu=file_menu, label="File")
        self.config(menu=self.menu)
        self.bind_key("s", self.save)
        self.bind_key("r", self.revert)

        self.field = Tkinter.Text(self, tabs=("4"))
        self.field.pack(fill="both", expand=1)
        self.field.bind("<KeyRelease>", self.update)
        self.set_contents(self.buffer)
        self.update()

    def bind_key(self, key, command):
        key = key.lower()
        self.bind_all("<Control-%s>" % key, command)
        if util.platform.osx:
            self.bind_all("<Command-%s>" % key, command)

    # Work around various oddities with Tkinter's newline handling
    @property
    def changed(self):
        return self.get_contents() != self.buffer
    def get_contents(self):
        return self.field.get(1.0, "end").rstrip("\n")
    def set_contents(self, text):
        self.field.delete(1.0, "end")
        self.field.insert(1.0, text.rstrip("\n"))

    def update(self, *_):
        self.title("%s%s" % ("*" if self.changed else "", self.filename))

    def save(self, *_):
        new_buffer = self.get_contents()
        if new_buffer != self.buffer:
            try:
                with open(self.filename, "w") as f:
                    f.write(new_buffer + '\n')
            except IOError as e:
                tkMessageBox.showerror(title="Could not save",
                    message="Could not save %s: %s" % (self.filename, e))
                return
        self.buffer = new_buffer
        self.update()

    def revert(self, *_):
        if self.changed and tkMessageBox.askyesno(
                title="Revert",
                message="Are you sure you want to revert to the last saved version?"
            ):
            self.set_contents(self.buffer)
