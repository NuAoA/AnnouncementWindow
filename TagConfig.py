import sys
if sys.version_info.major == 2:
    import Tkinter
    import tkColorChooser
    import tkFont
elif  sys.version_info.major == 3:
    import tkinter as Tkinter
    import tkinter.colorchooser as tkColorChooser
    import tkinter.font as tkFont
else:
    raise UserWarning("unknown python version?!")

import Filters
import Config
import util
import re
from functools import partial

LEFT = Tkinter.LEFT
RIGHT = Tkinter.RIGHT
CENTER = Tkinter.CENTER

# TODO list:
# -> Make it possible to add [groups] and [categories] along with regular expressions (currently you can only edit the expressions)
# -> add some color to the window

RE_MODIFIED = False

class ExpressionBar(Tkinter.Frame):
    def __init__(self, parent, category, expression_index):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.expression = category.re_expressions[expression_index]
        self.index = expression_index
        self.category = category
        self.string_ = Tkinter.StringVar()
        self.string_.set(self.expression.pattern)
        modcommand = self.register(self.exp_modified)

        self.entry = Tkinter.Entry(self, width=75, validate='key', validatecommand=(modcommand, '%P'), textvariable=self.string_)
        self.entry.pack(side=LEFT)

        label = Tkinter.Label(self, text=" ")
        label.pack(side=RIGHT)

    def exp_modified(self, text):
        if text == self.expression.pattern:
            return True
        if type(text) is str:
            global RE_MODIFIED
            self.expression = re.compile(text)
            self.category.re_expressions[self.index] = self.expression
            RE_MODIFIED = True
            return True
        return False

class CategoryBar(Tkinter.Frame):
    def __init__(self, parent, category, topparent, dialog):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.topparent = topparent
        self.dialog = dialog
        self.category = category
        self.is_grid = False
        self.window1_selection = Tkinter.IntVar()
        self.window2_selection = Tkinter.IntVar()
        # self.config(background="green")

        self.expand_button = Tkinter.Button(self, text="+", command=self.expand, width=1)
        self.expand_button.grid(row=0, column=0, sticky='w')

        frame = Tkinter.Frame(self, background="gray")

        label = Tkinter.Label(frame, text=self.category.category, anchor="w", width=15, background='gray')
        label.grid(row=0, column=0, sticky="w")

        col_ = 1
        for show_ in self.category.show.items():
            window = show_[0]
            show = show_[1]
            variable = self.window1_selection if col_ == 1 else self.window2_selection
            cbutton = Tkinter.Checkbutton(frame,
                                          background="gray",
                                          variable=variable,
                                          command=partial(self.set_show, window))
            if show:
                cbutton.select()
            cbutton.grid(row=0, column=col_)
            col_ += 1
        frame.grid(row=0, column=1, sticky="w")

        self.expression_frame = Tkinter.Frame(self)

        for row_ in range(0, len(self.category.re_expressions)):
            e_ = ExpressionBar(self.expression_frame, self.category, row_)
            e_.grid(row=row_, column=0, sticky="w")


    def set_show(self, window):
        self.category.show[window] = not self.category.show[window]

    def expand(self):
        if not self.is_grid:
            self.expression_frame.grid(row=1, column=1, sticky='w')
            self.expand_button.config(text="-")
        else:
            self.expression_frame.grid_forget()
            self.expand_button.config(text="+")
        self.is_grid = not self.is_grid

        self.dialog.resize()

class GroupBar(Tkinter.Frame):
    def __init__(self, parent, group, dialog):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.group = group
        self.dialog = dialog
        self.is_grid = False

        self.expand_button = Tkinter.Button(self, text="+", command=self.expand, width=1)
        self.expand_button.grid(row=0, column=0, sticky='w')

        frame = Tkinter.Frame(self)

        label = Tkinter.Label(frame, text=group.group, anchor="w", width=15, pady=0)
        label.grid(row=0, column=0)

        self.color_button = Tkinter.Button(frame, text="Color", command=self.set_color, background=self.group.color)
        self.color_button.grid(row=0, column=1)

        frame.grid(row=0, column=1, sticky="w")

        self.category_frame = Tkinter.Frame(self)
        title_frame = Tkinter.Frame(self.category_frame)
        frame = Tkinter.Frame(title_frame)
        label_frame = Tkinter.Frame(frame, width=128, height=21, background="gray")
        label_frame.pack_propagate(0)
        label = Tkinter.Label(label_frame, text="Window Visibility:", anchor="e", background="gray")
        label.pack(side=RIGHT)
        label_frame.grid(row=0, column=0, sticky="w")
        col_ = 1
        # Need to get window count:
        for category_ in self.group.categories.items():
            category_name = category_[0]
            category = category_[1]
            for show_ in category.show.items():
                window = show_[0]
                show = show_[1]
                win_frame = Tkinter.Frame(frame, width=28, height=21)
                win_frame.pack_propagate(0)
                win = Tkinter.Label(win_frame, text=str(window).rjust(3), anchor="w", background="gray")
                win.pack(fill="both", expand=True)
                win_frame.grid(row=0, column=col_)
                col_ += 1
            break
        frame.grid(row=0, column=1, sticky="w")
        title_frame.grid(row=0, column=0, sticky="w")

        row_ = 1
        for category_ in self.group.categories.items():
            category_name = category_[0]
            category = category_[1]
            c_ = CategoryBar(self.category_frame, category, self.parent, dialog)
            c_.grid(row=row_, column=0, sticky="w")
            row_ += 1


    def set_color(self):
        new_color = tkColorChooser.askcolor(parent=self)[1]
        if new_color is not None:
            self.color_button.config(background=new_color)
            self.group.set_color(new_color)

    def expand(self):
        if not self.is_grid:
            self.category_frame.grid(row=1, column=1, sticky='w')
            self.expand_button.config(text="-")
        else:
            self.category_frame.grid_forget()
            self.expand_button.config(text="+")
        self.is_grid = not self.is_grid

        self.dialog.resize()


# Modified tkSimpleDialog
class MainDialog(Tkinter.Toplevel):
    def __init__(self, parent, expressions=None):
        Tkinter.Toplevel.__init__(self, parent)

        self.parent = parent
        self.expressions = expressions
        # self.expressions.reload()
        self.withdraw()
        self.iconbitmap(Config.settings.icon_path)
        if parent.winfo_viewable():
            self.transient(parent)
        self.resizable(0, 1)
        self.title("Filter Configuration")
        self.result = None

        self.gen_body()
        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.deiconify()  # become visibile now
        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def gen_body(self):
        self.body_frame = Tkinter.Frame(self)
        self.initial_focus = self.body(self.body_frame)
        if not util.platform.osx:
            menu = Tkinter.Menu(self)
            menu.add_command(label="Accept", command=self.ok)
            menu.add_command(label="Cancel", command=self.cancel)
            self.config(menu=menu)
        else:
            frame = Tkinter.Frame(self.body_frame)
            ok_button = Tkinter.Button(frame, text="Accept", command=self.ok)  # , background=self.group.color)
            cancel_button = Tkinter.Button(frame, text="Cancel", command=self.cancel)  # .cancel, background=self.group.color)
            ok_button.pack(side=LEFT)
            cancel_button.pack(side=RIGHT)
            frame.grid(row=0, column=1, sticky='sw')
            # frame.grid(row=1, column=1, sticky="nsew")

        self.body_frame.grid(row=1, column=1, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.body_frame.grid_columnconfigure(1, weight=1)
        self.body_frame.grid_rowconfigure(1, weight=1)


    def body(self, master):
        canvas = Tkinter.Canvas(master, borderwidth=0, width=168)
        self.canvas = canvas
        frame = Tkinter.Frame(canvas, borderwidth=0)
        self.canvas_frame = frame
        vsb = Tkinter.Scrollbar(master, orient="vertical", command=canvas.yview)

        for i, group_ in enumerate(Filters.expressions.groups.items()):
            group_name = group_[0]
            group = group_[1]
            g = GroupBar(frame, group, self)
            g.grid(row=i, column=1, sticky="ew")

        canvas.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=2, sticky="ns")
        canvas.grid(row=1, column=1, sticky="nsew")
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.update_idletasks()

        self.minsize(frame.winfo_width(), 500)
        self.maxsize(1080, frame.winfo_height())
        self.resize()

    def resize(self):
        self.update_idletasks()
        self.canvas.config(width=self.canvas_frame.winfo_width(), height=self.winfo_height(),
            scrollregion=self.canvas.bbox('all'))
        self.config(width=self.canvas.winfo_width())

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()
        try:
            self.apply()
        finally:
            self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()
        Filters.expressions.reload()

    def apply(self):
        Filters.expressions.save_filter_data()
        if RE_MODIFIED:
            Filters.expressions.save_filter_expressions()

    def destroy(self):
        self.initial_focus = None
        Tkinter.Toplevel.destroy(self)

# A test configuation:
if __name__ == '__main__':
    def launch_dialog():
        MainDialog(root)

    # I need to call these or color&visibility data will not be loaded:
    for i in range(0, 8):
        Filters.expressions.add_window(i)

    Filters.expressions.reload()

    root = Tkinter.Tk()
    frame = Tkinter.Frame(root)
    frame.pack()
    button = Tkinter.Button(frame, text="Open Editor", command=launch_dialog)
    button.pack()
    root.mainloop()



