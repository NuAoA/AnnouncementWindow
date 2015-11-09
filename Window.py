import sys
if sys.version_info.major == 2:
    import Tkinter
    import tkFileDialog
    import tkColorChooser
    import tkFont
elif  sys.version_info.major == 3:
    import tkinter as Tkinter
    import tkinter.filedialog as tkFileDialog
    import tkinter.colorchooser as tkColorChooser
    import tkinter.font as tkFont
else:
    raise UserWarning("unknown python version?!")

import tkFontChooser
import Config
import Editor
import Filters
import GamelogReader
import util
import subprocess
import os
import TagConfig
from functools import partial
from collections import OrderedDict

# import psutil,time

def dict_to_font(dict_):
    return tkFont.Font(family=dict_["family"], size=dict_["size"], weight=dict_["weight"], slant=dict_["slant"], overstrike=dict_["overstrike"], underline=dict_["underline"])

class announcement_window(Tkinter.Frame):
    def __init__(self, parent, id_):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.id = id_
        self.show_tags = False
        self.index_dict = {}
        Filters.expressions.add_window(self.id)
        self.customFont = dict_to_font(self.parent.gui_data['font_w%s' % self.id])
        self.config_gui = None
        self.vsb_pos = 1.0
        self.init_text_window()
        self.init_pulldown()

    def init_text_window(self):
        self.text = Tkinter.Text(self, bg="black", wrap="word", font=self.customFont)
        self.vsb = Tkinter.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.text.config(cursor="")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.bind(util.mouse_buttons.right, self.popup)


        # link methods
        self.insert = self.text.insert
        self.delete = self.text.delete
        self.get = self.text.get
        self.index = self.text.index
        self.search = self.text.search
        self.tag_add = self.text.tag_add
        self.tag_config = self.text.tag_config
        self.tag_delete = self.text.tag_delete
        self.tag_names = self.text.tag_names
        self.tag_cget = self.text.tag_cget
        self.config = self.text.config
        self.yview = self.text.yview


    def init_pulldown(self):
        self.pulldown = Tkinter.Menu(self, tearoff=0)
        bg = "white"
        if util.platform.win or util.platform.osx:
             bg = "SystemMenu"
        self.pulldown.add_command(label="Window %d" % self.id, activebackground=bg, activeforeground="black")
        self.pulldown.add("separator")
        self.pulldown.add_command(label="Change Font", command=self.edit_font)
        self.pulldown.add_command(label="Toggle Tags", command=self.toggle_tags)
        self.pulldown.add_command(label="Clear Window", command=self.clear_window)
        # self.pulldown.add_command(label="test", command=self.test_todo_remove)

    def popup(self, event):
        if self.focus_get() is not None:
            self.pulldown.tk_popup(event.x_root, event.y_root)

    def toggle_tags(self):
        self.show_tags = not self.show_tags
        self.config(state="normal")
        self.gen_tags()
        self.config(state="disabled")

    def test_todo_remove(self):
        pass

    def edit_font(self):
        tup = tkFontChooser.askChooseFont(self.parent, defaultfont=self.customFont)
        if tup is not None:
            self.customFont = tkFont.Font(font=tup)
            self.parent.gui_data['font_w%s' % self.id] = self.customFont.actual()
            self.config(font=self.customFont)

    def edit_colors(self):
        if self.config_gui is None:
            Filters.expressions.reload()
            self.config_gui = config_gui(self, Filters.expressions)
            self.config_gui.protocol('WM_DELETE_WINDOW', self.close_config_gui)

    def close_config_gui(self):
        self.config_gui.destroy()
        self.config_gui = None
        Filters.expressions.save_filter_data()
        Filters.expressions.reload()
        self.parent.gen_tags()

    def clear_window(self):
        self.config(state="normal")
        self.delete('1.0', "end")
        self.gen_tags(clear_index_dict=True)
        self.config(state="disabled")


    def gen_tags(self, clear_index_dict=False):
        self.vsb_pos = (self.vsb.get()[1])
        for group_ in Filters.expressions.groups.items():
            group = group_[1]
            for category_ in group.categories.items():
                category = category_[1]
                tag_name = "%s.%s" % (group.group, category.category)
                # set_elide =
                self.tag_config('%s.elide' % tag_name, foreground="#FFF", elide=not (self.show_tags and category.get_show(self.id)))
                self.tag_config(tag_name, foreground=group.color, elide=not category.get_show(self.id))
                if clear_index_dict:
                    self.index_dict[tag_name] = 0
                elif not (tag_name in self.index_dict):
                    self.index_dict[tag_name] = 0
        if self.vsb_pos == 1.0:
            self.yview("end")

    def insert_ann(self, ann):
        def insert():
            tag_name = "%s.%s" % (ann.get_group(), ann.get_category())
            self.insert("end", "[%s][%s] " % (ann.get_group(), ann.get_category()), '%s.elide' % tag_name)
            self.insert("end", "%s" % (ann.get_text()), tag_name)
            self.trim_announcements(tag_name)

        if ann.get_show(self.id):
            insert()
        elif Config.settings.save_hidden_announcements:
            insert()

    def trim_announcements(self, tag_name):
        if Config.settings.trim_announcements[self.id]:
            self.index_dict[tag_name] += 1
            if self.index_dict[tag_name] > Config.settings.trim_announcements[self.id]:
                index = int(float(self.text.index('%s.first' % tag_name)))
                self.delete("%d.0" % index, "%d.0" % (index + 1))

class main_gui(Tkinter.Tk):
    def __init__(self):
        Tkinter.Tk.__init__(self)
        self.iconbitmap(Config.settings.icon_path)
        self.title("Announcement Window+")
        self.protocol('WM_DELETE_WINDOW', self.clean_exit)
        self.pack_propagate(False)
        self.config(bg="Gray", height=700, width=640)
        self.customFont = tkFont.Font(family='Lao UI', size=10)
        self.gui_data = Config.settings.load_gui_data()
        self.gamelog = GamelogReader.gamelog()
        self.gamelog.connect()
        self.announcement_windows = OrderedDict([])
        self.cpu_max = {}
        self.py = None
        if self.gui_data is None:
            self.gui_data = {"sash_place":int(700 / 3.236), "font_w0":self.customFont.actual(), "font_w1":self.customFont.actual()}
        self.locked = False
        self.init_menu()
        self.init_windows()
        self.gen_tags()
        # self.parallel()
        self.get_announcements(old=Config.settings.load_previous_announcements)
        self.pack_announcements()

    def init_menu(self):
        self.menu = Tkinter.Menu(self, tearoff=0)

        options_menu = Tkinter.Menu(self.menu, tearoff=0)
        options_menu.add_command(label="Filter Configuration", command=self.config_gui)
        options_menu.add_command(label="Edit filters.txt", command=self.open_filters)
        options_menu.add_command(label="Reload filters.txt", command=Filters.expressions.reload)

        self.settings_menu = Tkinter.Menu(self.menu, tearoff=0)
        self.settings_menu.add_command(label="Set Directory", command=self.askpath)
        self.settings_menu.add_command(label="Lock Window", command=self.lock_window)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.menu.add_separator()
        self.menu.add_cascade(label="Options", menu=options_menu)
        # self.menu.add_command(label="Dump CPU info",command = self.dump_info)

        self.config(menu=self.menu)

    def dump_info(self):
        print('CPU-MAX:%f' % max(self.cpu_max["CPU"]))
        print('CPU-AVG:%f' % (sum(self.cpu_max["CPU"]) / len(self.cpu_max["CPU"])))

        print('MEM-MAX:%f MB' % max(self.cpu_max["MEM"]))
        print('MEM-AVG:%f MB' % (sum(self.cpu_max["MEM"]) / len(self.cpu_max["MEM"])))
        self.cpu_max["CPU"] = []
        self.cpu_max["MEM"] = []

    def init_windows(self):
        self.panel = Tkinter.PanedWindow(self, orient="vertical", sashwidth=5)
        self.panel.pack(fill="both", expand=1)
        for i in range(0, 2):
            self.announcement_windows[i] = announcement_window(self, i)
        self.panel.add(self.announcement_windows[0])
        self.panel.add(self.announcement_windows[1])
        self.panel.update_idletasks()
        self.panel.sash_place(0, 0, self.gui_data["sash_place"])  # TODO: update to support multiple sashes

    def gen_tags(self):
        Filters.expressions.reload()
        for announcement_win in self.announcement_windows.items():
            announcement_win[1].config(state="normal")
            announcement_win[1].gen_tags()
            announcement_win[1].config(state="disabled")

    def clean_exit(self):
        self.gui_data["sash_place"] = self.panel.sash_coord(0)[1]
        Config.settings.save_gui_data(self.gui_data)
        self.destroy()

    def edit_filters(self):
        Editor.TextEditor(Config.settings.filters_path)

    def open_filters(self):
        Editor.native_open(Config.settings.filters_path)

    def config_gui(self):
        Filters.expressions.reload()
        TagConfig.MainDialog(self)
        self.gen_tags()

    def askpath(self):
        path = Config.settings.get_gamelog_path()
        if os.path.isfile(path):
            new_path = tkFileDialog.askopenfilename(initialfile=path, parent=self, filetypes=[('text files', '.txt')], title="Locate DwarfFortress/gamelog.txt")
        else:
            new_path = tkFileDialog.askopenfilename(initialdir=path, parent=self, filetypes=[('text files', '.txt')], title="Locate DwarfFortress/gamelog.txt")
        if os.path.isfile(new_path):
            Config.settings.set_gamelog_path(new_path)
            Config.settings.save()
            self.gamelog.connect()

    def lock_window(self):
        if util.platform.win:  # TODO: make this work on osx/linux
            self.overrideredirect(not self.locked)
            self.locked = not self.locked
            self.wm_attributes("-topmost", self.locked)
            tog_ = 'Unlock Window' if self.locked else 'Lock Window'
            self.settings_menu.entryconfig(self.settings_menu.index('end'), label=tog_)

    def get_announcements(self, old=False):
        if old:
            new_announcements = self.gamelog.get_old_announcements()
        else:
            new_announcements = self.gamelog.new()
        if new_announcements:
            for announcement_win in self.announcement_windows.items():
                announcement_win[1].vsb_pos = (announcement_win[1].vsb.get()[1])  # Jumps to end of list if the users scrollbar is @ end of list, otherwise holds current position
                announcement_win[1].text.config(state="normal")
            for ann in new_announcements:
                for announcement_win in self.announcement_windows.items():
                    announcement_win[1].insert_ann(ann)
            for announcement_win in self.announcement_windows.items():
                if announcement_win[1].vsb_pos == 1.0:
                    announcement_win[1].yview("end")
                announcement_win[1].text.config(state="disabled")
        self.after(1000, self.get_announcements)

    def pack_announcements(self):
        for announcement_win in self.announcement_windows.items():
            announcement_win[1].text.pack(side="top", fill="both", expand=True)
            # Why doesn't this always move to the end when you launch with setting: load_previous_announcements = True  ??
            announcement_win[1].yview("end")

    #===========================================================================
    # def parallel(self): #TODO: remove
    #     def find_process():
    #         for pid in psutil.pids():
    #             if psutil.Process(pid).name() == "python.exe":
    #                 if abs(psutil.Process(pid).create_time()-time.time()) < 5:
    #                     #was made less than 5 seconds ago
    #                     return psutil.Process(pid)
    #     if self.py is None:
    #         self.py = find_process()
    #         self.cpu_max["CPU"] = []
    #         self.cpu_max["MEM"] = []
    #         self.py.cpu_percent()
    #     else:
    #         self.cpu_max["MEM"].append(self.py.memory_info().rss/(1000*1024))
    #         self.cpu_max["CPU"].append(self.py.cpu_percent())
    #     self.after(5000,self.parallel)
    #
    #===========================================================================

if __name__ == "__main__":
    app = main_gui()
    app.mainloop()
