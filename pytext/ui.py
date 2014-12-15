__author__ = 'Allan'

from text import *
from math import *

class UIImage(DisplayObject):

    COLOR_DEFAULT = (255,255,255)
    TYPE_NORMAL = 0
    TYPE_NINESLICE = 1
    TYPE_REPEAT = 2

    def __init__(self, imageAddress, name="", bounds=None, autoAdjust=True, visible=True, imageType=TYPE_NORMAL, color=COLOR_DEFAULT, nineRect=None, fillCenter=False):
        super(UIImage, self).__init__(name, bounds, visible, color)

        self.__imageAddress = None

        self.fillCenter = fillCenter
        self.type = imageType
        self.imageAddress = imageAddress

        self.__nineRect = self.checkBounds(nineRect)
        if autoAdjust:
            clip = self.__currentSurface.get_clip()
            self._bounds.width, self._bounds.height = clip.width, clip.height

    @property
    def nineRect(self):
        return self.__nineRect

    @nineRect.setter
    def nineRect(self, value):
        self.__nineRect = self.checkBounds(value)

    @property
    def imageAddress(self):
        return self.__imageAddress

    @imageAddress.setter
    def imageAddress(self, value):
        if value == self.__imageAddress: return
        self.__imageAddress = value
        self.__normalSurface = SurfaceManager.getSurface(value) if value else None
        self.__currentSurface = self.__normalSurface
        self.__currentColor = UIImage.COLOR_DEFAULT

    def draw(self, screen, events=None):
        if not self.visible or not self.__normalSurface: return

        if self.color != self.__currentColor:
            self.__currentColor = self.color
            self.__currentSurface = self.__normalSurface.convert_alpha()
            if self.color and self.color != UIImage.COLOR_DEFAULT:
                self.__currentSurface.fill(self.color, special_flags=pygame.BLEND_RGB_MULT)

        if self.type == UIImage.TYPE_NORMAL:
            screen.blit(self.__currentSurface, (self.worldX, self.worldY), (0,0,self._bounds.width, self._bounds.height))
        elif self.type == UIImage.TYPE_REPEAT:
            if not self.__nineRect: self.__nineRect = self.__currentSurface.get_clip().copy()
            self.drawRepeat(screen, (self.worldX, self.worldY), (self.worldX+self.width, self.worldY+self.height), self.__nineRect)
        elif self.type == UIImage.TYPE_NINESLICE:
            if not self.__nineRect: self.__nineRect = self.__currentSurface.get_clip().copy()
            clip = self.__currentSurface.get_clip()
            b = self._bounds
            r9 = self.__nineRect
            l, r = r9.x, clip.width-r9.right
            u, d = r9.y, clip.height-r9.bottom

            self.drawRepeat(screen, (b.x+l, b.y), (b.x+b.width-r, b.y+u), (l,0,r9.width,u))#up left TO up right
            self.drawRepeat(screen, (b.x, b.y+u), (b.x+l, b.y+b.height-d), (0,u, l, r9.height))#up left TO down left
            self.drawRepeat(screen, (b.x+b.width-r, b.y+u), (b.x+b.width, b.y+b.height-d), (r9.right,u,r,r9.height))#up right TO down right
            self.drawRepeat(screen, (b.x+l, b.y+b.height-d), (b.x+b.width-r, b.y+b.height), (l,r9.bottom,r9.width,d))#down left TO down right

            if self.fillCenter: self.drawRepeat(screen, (b.x+l, b.y+u), (b.x+b.width-r, b.y+b.height-d), self.__nineRect)

            screen.blit(self.__currentSurface, (b.x,b.y), (0,0,l,u))#top left
            screen.blit(self.__currentSurface, (b.x+b.width-r, b.y), (r9.right,0,r,u))#top right
            screen.blit(self.__currentSurface, (b.x+b.width-r, b.y+b.height-d), (r9.right, r9.bottom, r, d))#bottom right
            screen.blit(self.__currentSurface, (b.x, b.y+b.height-d), (0,r9.bottom,l,d))#bottom left

    def drawRepeat(self, screen, init, end, copyArea=None):
        if not copyArea: copyArea = self.__currentSurface.get_clip()
        if copyArea[3] == 0 or copyArea[2] == 0: return
        rows = ceil((end[1]-init[1])/float(copyArea[3]))
        columns = ceil((end[0]-init[0])/float(copyArea[2]))
        for li in range(int(rows)):
            for co in range(int(columns)):
                x = init[0] + co*copyArea[2]
                y = init[1] + li*copyArea[3]
                screen.blit(self.__currentSurface, (x, y), (
                    copyArea[0],
                    copyArea[1],
                    copyArea[2] if x+copyArea[2] < end[0] else end[0] - x,
                    copyArea[3] if y+copyArea[3] < end[1] else end[1] - y
                ))


class UIGrid( DisplayObject ):

    def __init__(self, distanceHorizontal, distanceVertical, numberOfColumns=1,
                 name="", bounds=None, visible=True, color=(100,100,100,100)):
        super(UIGrid, self).__init__( name, bounds, visible, color )
        self.distanceVertical = distanceVertical
        self.distanceHorizontal = distanceHorizontal
        self.numberOfColumns = max(numberOfColumns, 1)

    def updateGrid(self):
        total = len(self.children)
        if self.visible:
            for index in range(total):
                co = index%self.numberOfColumns
                li = floor(index/float(self.numberOfColumns))
                self.children[index].localX = co * self.distanceHorizontal
                self.children[index].localY = li * self.distanceVertical

        self._bounds.width = self.distanceHorizontal * min(total, self.numberOfColumns)
        self._bounds.height = self.distanceVertical * floor(total/float(self.numberOfColumns))

    def update(self, screen, events=None):
        self.updateGrid()
        super(UIGrid, self).update(screen, events)

    def draw(self, screen, events=None):
        pass


class UIButton( InteractiveObject ):

    ALIGN_LEFT = 0
    ALIGN_RIGHT = 1
    ALIGN_CENTER = 0.5

    def __init__( self, name="", bounds=None, visible=True, color=(100,100,100,100), selectable=True,
                  label="", font=None, normalBackground=None, autoAdjust=True, padding=(14,4,14,4), onClickHandler=None, align=ALIGN_CENTER, data=None ):
        super(UIButton, self).__init__( name, bounds, visible, color, selectable )

        self.onClick = EventHook()
        self.textfield = None
        self.background = None
        self.padding = padding
        self.autoAdjust = autoAdjust
        self.align = align
        self.data = data

        if isinstance(font, str): font = Font.getFont(font)
        if not font: font = Font.getFirstFont()

        self.textfield = UITextField( label, font, color=color, align=UITextField.ALIGN_LEFT, wordwrap=False, autoAdjust=True )
        self.textfield.selectable = False
        self.addChild( self.textfield )

        if normalBackground:
            self.background = normalBackground
            self.addChild( self.background )

        if onClickHandler:
            self.onClick += onClickHandler

    @property
    def label(self):
        return self.textfield.text

    @label.setter
    def label(self, value):
        self.textfield.clear()
        self.textfield.insertHtml(value, 0)

    def click(self):
        self.onClick.fire( self )

    def mouseUp(self, pos):
        super(UIButton, self).mouseUp(pos)
        if self._bounds.collidepoint(pos):
            self.click()

    def draw(self, screen, events=None):
        if self.autoAdjust:
            self.width = self.textfield.width + self.padding[0] + self.padding[2]
            self.height = self.textfield.height + self.padding[1] + self.padding[3]

        if self.background:
            self.background.move(0,0,relativeToWorld=False)
            self.background.resize( self.width, self.height )

        if not self.autoAdjust:
            self.textfield.resize( self.width - self.padding[0] - self.padding[2], self.height - self.padding[1] - self.padding[2] )

        self.textfield.move( (self.width-self.textfield.contentWidth) * ( self.align if not self.autoAdjust else 0.5 ),
                             (self.height-self.textfield.contentHeight) * 0.5 )

        if self.isFocus:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.click()
                        events.remove(event)
                        break


class UIScrollbar( InteractiveObject ):

    DIRECTION_VERTICAL = 0
    DIRECTION_HORIZONTAL = 1

    def __init__( self, name="", bounds=None, visible=True, color=(60,60,60,255), selectable=True,
                  background=None, drag=None, direction=DIRECTION_VERTICAL ):
        super(UIScrollbar, self).__init__(name, bounds, visible, color, selectable)
        self.background = background if background else DisplayObject( color=(color[0]*1.3, color[1]*1.3, color[2]*1.3, color[3]) )
        self.drag = drag if drag else DisplayObject( color=(color[0], color[1], color[2], color[3]) )
        self.direction = direction
        self.addChild( self.background )
        self.addChild( self.drag )
        self.background._bounds = self._bounds.copy()
        self.drag._bounds = self._bounds.copy()

        self._value = 0
        self._viewSize = 0
        self._contentSize = 0
        self._downOffset = (0,0)

        self.mouseScroll = EventHook()

    def draw(self, screen, events=None):
        pass

    @property
    def value(self): return self._value

    @value.setter
    def value(self, value):
        self._value = clamp( value, 0, 1 )

        if self.direction == UIScrollbar.DIRECTION_VERTICAL:
            self.drag.move( 0, self._value * (self.height-self.drag.height), relativeToWorld=False )
        else:
            self.drag.move( self._value * (self.width-self.drag.width), 0, relativeToWorld=False )

    def getScrollForView(self):
        return self._value * (self._contentSize - self._viewSize)

    def setValue(self, contentSize, viewSize, contentScroll):
        self.visible = contentSize > viewSize

        self.background.resize(self.width, self.height)

        if contentSize < viewSize: contentSize = viewSize

        self._viewSize = viewSize
        self._contentSize = contentSize

        if self.direction == UIScrollbar.DIRECTION_VERTICAL:
            self.drag.resize( self.width, self.height * (viewSize/float(contentSize)) )
        else:
            self.drag.resize( self.width * (viewSize/float(contentSize)), self.height )

        self.value = contentScroll/float(contentSize-viewSize) if contentSize > viewSize else 0

    def mouseDown(self, pos):
        super(UIScrollbar, self).mouseDown(pos)

        self._downOffset = ( pos[0]-self.drag.worldX, pos[1]-self.drag.worldY )

    def mouseDrag(self, pos, delta):
        super(UIScrollbar, self).mouseDrag(pos, delta)

        if self.direction == UIScrollbar.DIRECTION_VERTICAL:
            self.value = ((pos[1]-self._downOffset[1]) - self.worldY)/float(self.height-self.drag.height)
        else:
            self.value = ((pos[0]-self._downOffset[0]) - self.worldX)/float(self.width-self.drag.width)

        self.mouseScroll.fire()


class UIList( DisplayObject ):
    def __init__( self, name="", bounds=None, visible=True, color=(100,100,100,100),
                  options=[], font=None, scrollWidth=10, padding=(10,10,10,10), buttonHeight=32, onSelectHandler=None ):
        super(UIList, self).__init__(name, bounds, visible, color)

        self.buttons = []
        self.onSelect = EventHook()
        self.font = font

        self._padding = padding
        self._scrollWidth = scrollWidth
        self._buttonHeight = buttonHeight

        self.scrollbar = UIScrollbar( "scrollbar", (self.width-padding[2]-self._scrollWidth, padding[1], self._scrollWidth, self.height - self._padding[1] - self._padding[3] ) )
        self.mask = DisplayMask( "mask", (self._padding[0], self._padding[1], self.width - self._padding[2], self.height - self._padding[1] - self._padding[3]) )
        self.grid = UIGrid( name="grid", distanceHorizontal=100, distanceVertical=32, numberOfColumns=1, bounds=(0, 0) )

        self.addChild( self.mask, changePositionToRelative=True )
        self.addChild( self.scrollbar, changePositionToRelative=True )
        self.mask.addChild( self.grid, changePositionToRelative=True )

        self.list = options
        self.scrollbar.mouseScroll += self.__scrollEventHandler
        if onSelectHandler: self.onSelect += onSelectHandler

    @property
    def list(self): return self._list

    @list.setter
    def list(self, options, data=None):
        self._list = options
        self.clear()
        while len(self.buttons) < len(options):
            button = UIButton( "button"+len(self.buttons),
                               (0,0,self.width-self._padding[0]-self._padding[2]-self._scrollWidth,self._buttonHeight),
                               font=self.font, padding=(6,0,6,0), autoAdjust=False,
                               align=UIButton.ALIGN_LEFT, onClickHandler=self.onClickButtonList )
            self.buttons.append( button )
        for i in range( len(options) ):
            self.buttons[i].label = options[i]
            self.buttons[i].data = data[i] if data else None
            self.buttons[i].visible = True
            self.grid.addChild( self.buttons[i] )

        self.grid.updateGrid()
        self.scrollbar.setValue( self.grid.height, self.mask.height, self.mask.scrollV )

    def clear(self):
        self.mask.setScroll(0,0)
        for button in self.buttons:
            if button.parent: button.parent.removeChild(button)
            button.visible = False

    def onClickButtonList(self, button):
        self.onSelect.fire( button.data if button.data else button.label )

    def update(self, screen, events=None):
        super(UIList, self).update(screen, events)
        self.scrollbar.setValue( self.grid.height, self.mask.height, self.mask.scrollV )

    def __scrollEventHandler(self):
        self.mask.setScroll( self.mask.scrollH, self.scrollbar.getScrollForView() )


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class UIDeserialize():
    @staticmethod
    def getContent( xmlAddress ):
        xml = ET.parse( xmlAddress )
        return UIDeserialize.getContentByElement( xml.getroot() )

    @staticmethod
    def getContentByElement( element ):
        container = DisplayObject("root")
        for child in element:
            container.addChild( UIDeserialize.getDisplayByElement( child ), changePositionToRelative=True )
        return container

    @staticmethod
    def getDisplayByElement( element ):
        params = {}
        for key, value in element.attrib.iteritems():
            if value[0] == "#":
                params[key] = value[1:]
            else:
                params[key] = eval(value)

        for p in element:
            if p.tag != "children":
                params[p.tag] = p.text

        display = eval(element.tag)( **params )

        children = element.find("children")
        if children:
            for child in children:
                display.addChild( UIDeserialize.getDisplayByElement( child ), changePositionToRelative=True )

        return display

    @staticmethod
    def getBoundsByString( boundsString ):
        m = re.match('\(?(?P<x>\d+)[ ,]*(?P<y>\d+)[ ,]*(?P<w>\d*)[ ,]*(?P<h>\d*)\)?', boundsString)
        return ( int(m.group("x")) if m.group("x") else 0,
                 int(m.group("y")) if m.group("y") else 0,
                 int(m.group("w")) if m.group("w") else 0,
                 int(m.group("h")) if m.group("h") else 0 )


#talk = TalkView.root.findall(".//*[@id='"+TalkView.current_talk+"']/talk["+str(self.current+1)+"]")[0]
# if talk.get("author") == "0":
#d = dict(p1=1, p2=2)
#for id in TalkView.callsIncoming:
            #element = TalkView.root.findall(".//*[@id='"+id+"']")
            #if len(element):
             #   options.append(element[0].find("title").text)
             #   ids.append(element[0].get("id"))
d = {"p1":1, "p2":2}
def f2(p1,p2):
    print p1, p2
f2(**d)

#tree = ET.parse("radio.xml")
#root = tree.getroot()