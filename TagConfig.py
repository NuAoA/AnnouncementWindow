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
    def __init__(self, parent, category, canvas, topparent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.canvas = canvas
        self.topparent = topparent
        self.category = category
        self.is_grid = False
        # self.config(background="green")

        self.expand_button = Tkinter.Button(self, text="+", command=self.expand, width=1)
        self.expand_button.grid(row=0, column=0, sticky='w')

        frame = Tkinter.Frame(self)

        label = Tkinter.Label(frame, text=self.category.category, anchor="w", width=15)
        label.grid(row=0, column=0, sticky="w")

        col_ = 1
        for show_ in self.category.show.items():
            window = show_[0]
            show = show_[1]
            cbutton = Tkinter.Checkbutton(frame)
            if show:
                cbutton.select()
            cbutton.config(command=partial(self.set_show, window, show, cbutton))
            cbutton.grid(row=0, column=col_)
            col_ += 1
        frame.grid(row=0, column=1, sticky="w")

        self.expression_frame = Tkinter.Frame(self)

        for row_ in range(0, len(self.category.re_expressions)):
            e_ = ExpressionBar(self.expression_frame, self.category, row_)
            e_.grid(row=row_, column=0, sticky="w")


    def set_show(self, window, currentVal, button):
        self.category.show[window] = not self.category.show[window]

    def expand(self):
        if not self.is_grid:
            self.expression_frame.grid(row=1, column=1, sticky='w')
            self.expand_button.config(text="-")
        else:
            self.expression_frame.grid_forget()
            self.expand_button.config(text="+")
        self.is_grid = not self.is_grid

        self.parent.update_idletasks()
        self.canvas.config(width=self.parent.winfo_width() + 17)

class GroupBar(Tkinter.Frame):
    def __init__(self, parent, group, canvas):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.group = group
        self.canvas = canvas
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

        label = Tkinter.Label(frame, text="Window Visibility:", anchor="e", width=17, padx=2)
        label.grid(row=0, column=0, sticky="w")

        col_ = 1
        # Need to get window count:
        for category_ in self.group.categories.items():
            category_name = category_[0]
            category = category_[1]
            for show_ in category.show.items():
                window = show_[0]
                show = show_[1]
                win = Tkinter.Label(frame, text=str(window), width=3, anchor="center", padx=1)  # Could use work, window #'s tend to drift off center
                win.grid(row=0, column=col_)
                col_ += 1
            break
        frame.grid(row=0, column=1, sticky="w")
        title_frame.grid(row=0, column=0, sticky="w")

        row_ = 1
        for category_ in self.group.categories.items():
            category_name = category_[0]
            category = category_[1]
            c_ = CategoryBar(self.category_frame, category, canvas, self.parent)
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

        # resize window:
        self.parent.update_idletasks()
        self.canvas.config(width=self.parent.winfo_width())


# Modified tkSimpleDialog
class MainDialog(Tkinter.Toplevel):
    def __init__(self, parent, expressions=None):
        Tkinter.Toplevel.__init__(self, parent)
        self.parent = parent
        self.expressions = expressions
        # self.expressions.reload()
        self.withdraw()
        if parent.winfo_viewable():
            self.transient(parent)
        self.resizable(0, 1)
        self.title("Filter Configuration")
        self.result = None

        self.gen_body()
        self.menubar()
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

    def resize(self, canvas, event):
        canvas.config(height=self.winfo_height() - 14)

    def gen_body(self):
        self.body_frame = Tkinter.Frame(self)
        self.initial_focus = self.body(self.body_frame)
        self.body_frame.pack(padx=5, pady=5)

    def body(self, master):
        def onFrameConfigure(canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.config(height=self.winfo_height() - 14)  # why that -14 needs to be there I will never know, but the window increases by that amount every time this is called

        canvas = Tkinter.Canvas(master, borderwidth=0, width=168)
        frame = Tkinter.Frame(canvas, borderwidth=0)
        vsb = Tkinter.Scrollbar(master, orient="vertical", command=canvas.yview)

        for group_ in Filters.expressions.groups.items():
            group_name = group_[0]
            group = group_[1]
            g = GroupBar(frame, group, canvas)
            g.pack(fill=Tkinter.X)

        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill="y")
        canvas.pack(side=LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
        frame.update_idletasks()

        self.minsize(frame.winfo_width(), 300)
        self.maxsize(1080, frame.winfo_height())

        canvas.config(width=frame.winfo_width())
        canvas.config(height=self.winfo_height())
        self.bind("<Configure>", partial(self.resize, canvas))

    def menubar(self):
        menu = Tkinter.Menu(self)
        menu.add_command(label="Accept", command=self.ok)
        menu.add_command(label="Cancel", command=self.cancel)
        self.config(menu=menu)

        # self.bind("<Return>", self.ok)
        # self.bind("<Escape>", self.cancel)

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
    for i in range(0, 2):
        Filters.expressions.add_window(i)

    Filters.expressions.reload()

    root = Tkinter.Tk()
    frame = Tkinter.Frame(root)
    frame.pack()
    button = Tkinter.Button(frame, text="Open Editor", command=launch_dialog)
    button.pack()
    root.mainloop()



