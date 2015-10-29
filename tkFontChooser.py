import sys
if sys.version_info.major == 2:
    import tkSimpleDialog
    import tkFont
    import Tkinter
    import ttk
elif sys.version_info.major == 3:
    import tkinter.simpledialog as tkSimpleDialog
    import tkinter.font as tkFont
    import tkinter as Tkinter
    import tkinter.ttk as ttk


_default_font = 'Arial'

class myFontChooser(tkSimpleDialog.Dialog):
    def __init__(self, parent, defaultFont=None):
        if defaultFont is None:
            self._family = Tkinter.StringVar(value=_default_font)
            self._size = Tkinter.StringVar(value='10')
            self._weight = Tkinter.StringVar(value=tkFont.NORMAL)
            self._slant = Tkinter.StringVar(value=tkFont.ROMAN)
            self._isUnderline = Tkinter.BooleanVar(value=False)
        else:
            self._family = Tkinter.StringVar(value=defaultFont.actual()['family'])
            self._size = Tkinter.StringVar(value=defaultFont.actual()['size'])
            self._weight = Tkinter.StringVar(value=defaultFont.actual()['weight'])
            self._slant = Tkinter.StringVar(value=defaultFont.actual()['slant'])
            self._isUnderline = Tkinter.BooleanVar(value=defaultFont.actual()['underline'])

        tkSimpleDialog.Dialog.__init__(self, parent, 'Choose Font')

    def body(self, master):
        self.resizable(0, 0)
        theRow = 0
        Tkinter.Label(master, text="Font Family").grid(row=theRow, column=0)
        Tkinter.Label(master, text="Font Size").grid(row=theRow, column=2)
        theRow += 1
        # Font Families

        self.familyList = list(tkFont.families())
        self.familyList.sort()
        self.sizeList = []

        for i in range(6, 30):
            self.sizeList.append(i)
        self.fontBox = ttk.Combobox(master, values=self.familyList)
        self.sizeBox = ttk.Combobox(master, values=self.sizeList)


        if self._family.get() in self.familyList:
            self.fontBox.current(self.familyList.index(self._family.get()))
        elif _default_font in self.familyList:
            self.fontBox.current(self.familyList.index(_default_font))
        self.sizeBox.current(self.sizeList.index(int(self._size.get())))


        self.defaultFont = tkFont.Font(font=self.getFontTuple())

        self.fontBox.grid(row=theRow, column=0, columnspan=2, sticky=Tkinter.N + Tkinter.S + Tkinter.E + Tkinter.W, padx=10)
        self.fontBox.bind("<<ComboboxSelected>>", self.modifyFont)
        self.sizeBox.grid(row=theRow, column=2, columnspan=2, sticky=Tkinter.N + Tkinter.S + Tkinter.E + Tkinter.W, padx=10)
        self.sizeBox.bind("<<ComboboxSelected>>", self.modifyFont)
        theRow += 1

        Tkinter.Label(master, text='Styles', anchor=Tkinter.W).grid(row=theRow, column=0, pady=10, sticky=Tkinter.W)
        theRow += 1
        Tkinter.Checkbutton(master, command=self.modifyStyle, text="bold", offvalue='normal', onvalue='bold', variable=self._weight).grid(row=theRow, column=0)
        Tkinter.Checkbutton(master, command=self.modifyStyle, text="italic", offvalue='roman', onvalue='italic', variable=self._slant).grid(row=theRow, column=1)
        Tkinter.Checkbutton(master, command=self.modifyStyle, text="underline", offvalue=False, onvalue=True, variable=self._isUnderline).grid(row=theRow, column=2)
        theRow += 1
        Tkinter.Label(master, text='Sample Text', anchor=Tkinter.W).grid(row=theRow, column=0, pady=10, sticky=Tkinter.W)
        theRow += 1
        self.sampleText = Tkinter.Text(master, height=11, width=50, background="black")
        self.sampleText.insert(Tkinter.INSERT,
                                'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\nA vile force of darkness has arrived!', 'fontStyle')
        self.sampleText.config(state=Tkinter.DISABLED)
        self.sampleText.tag_config('fontStyle', font=self.defaultFont, foreground="red")
        self.sampleText.grid(row=theRow, column=0, columnspan=4, padx=10)

    def modifyFont(self, event):
        self.defaultFont.configure(family=self.familyList[self.fontBox.current()], size=self.sizeList[int(self.sizeBox.current())] ,
                                    weight=self._weight.get(), slant=self._slant.get(),
                                    underline=self._isUnderline.get())
    def modifyStyle(self):
        self.modifyFont(None)
    def getFontTuple(self):
        family = self.familyList[self.fontBox.current()]
        size = self.sizeList[int(self.sizeBox.current())]
        styleList = [ ]
        if self._weight.get() == tkFont.BOLD:
            styleList.append('bold')
        if self._slant.get() == tkFont.ITALIC:
            styleList.append('italic')
        if self._isUnderline.get():
            styleList.append('underline')

        if len(styleList) == 0:
            return family, size
        else:
            return family, size, ' '.join(styleList)

    def apply(self):
        self.result = self.getFontTuple()

def askChooseFont(parent, defaultfont=None):
    return myFontChooser(parent, defaultFont=defaultfont).result

if __name__ == '__main__':
    root = Tkinter.Tk()
    print(askChooseFont(root))
