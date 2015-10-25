import Tix
import tkSimpleDialog
import tkFont

class FontChooser( tkSimpleDialog.Dialog ):
    BASIC = 1
    ALL   = 2

    def __init__( self, parent, defaultfont=None, showstyles=None ):
        self._family       = Tix.StringVar(  value='Ariel'       )
        self._sizeString   = Tix.StringVar(  value='12'          )
        self._weight       = Tix.StringVar(  value=tkFont.NORMAL )
        self._slant        = Tix.StringVar(  value=tkFont.ROMAN  )
        self._isUnderline  = Tix.BooleanVar( value=False         )
        self._isOverstrike = Tix.BooleanVar( value=False         )
       
        if defaultfont:
            self._initialize( defaultfont )
        
        self._currentFont  = tkFont.Font( font=self.getFontTuple()  )
        
        self._showStyles   = showstyles
        
        self.sampleText      = None
        
        tkSimpleDialog.Dialog.__init__( self, parent, 'Font Chooser' )
    
    def _initialize( self, aFont ):
        if not isinstance( aFont, tkFont.Font ):
            aFont = tkFont.Font( font=aFont )
        
        fontOpts = aFont.actual( )
        
        self._family.set(       fontOpts[ 'family'     ] )
        self._sizeString.set(   fontOpts[ 'size'       ] )
        self._weight.set(       fontOpts[ 'weight'     ] )
        self._slant.set(        fontOpts[ 'slant'      ] )
        self._isUnderline.set(  fontOpts[ 'underline'  ] )
        self._isOverstrike.set( fontOpts[ 'overstrike' ] )
    
    def body( self, master ):
        theRow = 0
        
        Tix.Label( master, text="Font Family" ).grid( row=theRow, column=0 )
        Tix.Label( master, text="Font Size" ).grid( row=theRow, column=2 )
        
        theRow += 1
        
        # Font Families
        fontList = Tix.ComboBox( master, command=self.selectionChanged, dropdown=False, editable=False, selectmode=Tix.IMMEDIATE, variable=self._family )

        fontList.grid( row=theRow, column=0, columnspan=2, sticky=Tix.N+Tix.S+Tix.E+Tix.W, padx=10 )
        first = self._family.get()       
        familyList = list(tkFont.families( ))
        familyList.sort()
        pick = 0
        i=0        
        for family in familyList:            
            if family[0] == '@':
                continue            
            if first is None:
                first = family
            if first == family:
                pick = i  
            fontList.insert( Tix.END, family )
            i+=1
        fontList.configure( value=first)
        fontList.pick(pick)
        # Font Sizes
        sizeList = Tix.ComboBox( master, command=self.selectionChanged, dropdown=False, editable=False, selectmode=Tix.IMMEDIATE, variable=self._sizeString )
        sizeList.grid( row=theRow, column=2, columnspan=2, sticky=Tix.N+Tix.S+Tix.E+Tix.W, padx=10 )
        for size in xrange( 6,31 ):
            sizeList.insert( Tix.END, '%d' % size )
        sizeList.pick(int(self._sizeString.get())-6)
        sizeList.configure( value=self._sizeString.get() )
        
        # Styles
        if self._showStyles is not None:
            theRow += 1
           
            if self._showStyles in ( FontChooser.ALL, FontChooser.BASIC ):
                Tix.Label( master, text='Styles', anchor=Tix.W ).grid( row=theRow, column=0, pady=10, sticky=Tix.W )
                
                theRow += 1
                
                Tix.Checkbutton( master, text="bold", command=self.selectionChanged, offvalue='normal', onvalue='bold', variable=self._weight ).grid(row=theRow, column=0)
                Tix.Checkbutton( master, text="italic", command=self.selectionChanged, offvalue='roman', onvalue='italic', variable=self._slant ).grid(row=theRow, column=1)
           
            if self._showStyles == FontChooser.ALL:
                Tix.Checkbutton( master, text="underline", command=self.selectionChanged, offvalue=False, onvalue=True, variable=self._isUnderline ).grid(row=theRow, column=2)
                Tix.Checkbutton( master, text="overstrike", command=self.selectionChanged, offvalue=False, onvalue=True, variable=self._isOverstrike ).grid(row=theRow, column=3)
        
        # Sample Text
        theRow += 1
        
        Tix.Label( master, text='Sample Text', anchor=Tix.W ).grid( row=theRow, column=0, pady=10, sticky=Tix.W )
        
        theRow += 1
        
        self.sampleText = Tix.Text( master, height=11, width=70 )
        self.sampleText.insert( Tix.INSERT,
                                'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz', 'fontStyle' )
        self.sampleText.config( state=Tix.DISABLED )
        self.sampleText.tag_config( 'fontStyle', font=self._currentFont )
        self.sampleText.grid( row=theRow, column=0, columnspan=4, padx=10 )

    def apply( self ):
        self.result = self.getFontTuple( )
    
    def selectionChanged( self, something=None ):        
        self._currentFont.configure( family=self._family.get(), size=self._sizeString.get(),
                                    weight=self._weight.get(), slant=self._slant.get(),
                                    underline=self._isUnderline.get(),
                                    overstrike=self._isOverstrike.get() )
    
        if self.sampleText:
            self.sampleText.tag_config( 'fontStyle', font=self._currentFont )
    def getFontTuple( self ):
        family = self._family.get()
        size   = int(self._sizeString.get())
        
        styleList = [ ]
        if self._weight.get() == tkFont.BOLD:
            styleList.append( 'bold' )
        if self._slant.get() == tkFont.ITALIC:
            styleList.append( 'italic' )
        if self._isUnderline.get():
            styleList.append( 'underline' )
        if self._isOverstrike.get():
            styleList.append( 'overstrike' )
        
        if len(styleList) == 0:
            return family, size
        else:
            return family, size, ' '.join( styleList )
        
    def getFontTuple2( self ):
        family = self._family.get()
        size   = int(self._sizeString.get())       
        styleList = {"weight":"normal","slant":"normal","underline":False,"overstrike":False}
        if self._weight.get() == tkFont.BOLD:
            styleList["weight"]='bold' 
        if self._slant.get() == tkFont.ITALIC:
            styleList["slant"]='italic'
        if self._isUnderline.get():
            styleList["underline"]=True
        if self._isOverstrike.get():
            styleList["overstrike"]=True          

        return family, size,styleList

def askChooseFont( parent, defaultfont=None, showstyles=FontChooser.ALL ):
    return FontChooser( parent, defaultfont=defaultfont, showstyles=showstyles ).result
    
if __name__ == '__main__':
    root = Tix.Tk( )
    font = askChooseFont( root )    
    if font:
        print font