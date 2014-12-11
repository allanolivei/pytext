"""This is a Title
===============
That has a paragraph about a main subject and is set when the '='
is at least the same length of the title itself.

Subject Subtitle
----------------"""

__author__ = 'Allan'

import pygame
import pygame.gfxdraw
from math import ceil, floor

from EventHook import *

pygame.init()

class DisplayObject(object):

    def __init__(self, bounds=None, visible=True, color=(100,100,100,100)):

        self._bounds = self.checkBounds(bounds)
        self._visible = visible

        self.color = color
        self.children = []
        self.parent = None
        self.onVisible = EventHook()
        self.offVisible = EventHook()

    @property
    def worldX(self):
        return self._bounds.x

    @worldX.setter
    def worldX(self, value):
        diff = value - self._bounds.x
        self._bounds.x = value
        for child in self.children: child.worldX += diff

    @property
    def worldY(self):
        return self._bounds.y

    @worldY.setter
    def worldY(self, value):
        diff = value - self._bounds.y
        self._bounds.y = value
        for child in self.children: child.worldY += diff

    @property
    def localX(self):
        if self.parent: return self._bounds.x - self.parent._bounds.x
        else: return self._bounds.x

    @localX.setter
    def localX(self, value):
        if not self.parent:
            self.worldX = value
            return
        diff = self.parent.worldX + value - self._bounds.x
        self._bounds.x = self.parent.worldX + value
        for child in self.children: child.worldX += diff

    @property
    def localY(self):
        if self.parent: return self._bounds.y - self.parent._bounds.y
        else: return self._bounds.y

    @localY.setter
    def localY(self, value):
        if not self.parent:
            self.worldY = value
            return
        diff = self.parent.worldY + value - self._bounds.y
        self._bounds.y = self.parent.worldY + value
        for child in self.children: child.worldY += diff

    @property
    def visible(self):
        display = self.parent
        while display:
            if not display._visible: return False
            display = display.parent

        return self._visible

    @visible.setter
    def visible(self, value):
        if self._visible == value: return
        self._visible = value
        if value: self.onVisible.fire()
        else: self.offVisible.fire()

    @property
    def width(self): return self._bounds.width

    @width.setter
    def width(self, value): self._bounds.width = max(0,value)

    @property
    def height(self): return self._bounds.height

    @height.setter
    def height(self, value): self._bounds.height = max(0,value)

    def update(self, screen, events=None):
        if self.visible:
            self.draw(screen, events)
            self.updateChildren(screen, events)

    def draw(self, screen, events=None):
        """
        This is a Title
        ===============
        That has a paragraph about a main subject and is set when the '='
        is at least the same length of the title itself.

        Subject Subtitle
        ----------------
        Subtitles are set with '-' and are required to have the same length
        of the subtitle itself, just like titles.

        Lists can be unnumbered like:

         * Item Foo
         * Item Bar

        Or automatically numbered:

         #. Item 1
         #. Item 2

        Inline Markup
        -------------
        Words can have *emphasis in italics* or be **bold** and you can define
        code samples with back quotes, like when you talk about a command: ``sudo``
        gives you super user powers!
        Send a message to a recipient
        :param Surface screen: The person sending the message.
        :param List events: This list of Event.
        :return: None return.
        :rtype: None
        :raises ValueError: Retorna esse erro doido, if the message_body exceeds 160 characters
        :raises TypeError: if the message_body is not a basestring
        """
        pygame.gfxdraw.box(screen, (self.worldX, self.worldY, self.width, self.height), self.color )

    def updateChildren(self, screen, events=None):
        for child in self.children:
            child.update(screen, events)

    #def getContentHeight(self):
    #    h = self._bounds.height
    #    for child in self.children:
    #        newH = child.localY + child.getContentHeight()
    #        h = max(h, newH)
    #    return h

    def isChildren(self, displayObject):
        for child in self.children:
            if child == displayObject or child.isChildren(displayObject): return True
        return False

    def destroy(self):
        for child in self.children:
            child.destroy()
        del self.children[:]

    def move(self, x, y, relativeToWorld=False):
        if not relativeToWorld:
            self.localX, self.localY = x, y
        else:
            self.worldX, self.worldY = x, y

    def resize(self, w, h):
        self._bounds.size = (w, h)

    def removeChild(self, displayObject):
        index = self.children.index(displayObject)
        if index != -1:
            del self.children[index]
            displayObject.parent = None

    def addChild(self, displayObject, childDepth=99999, changePositionToRelative=False):
        if displayObject.parent: displayObject.parent.removeChild(displayObject)
        self.children.insert( min(len(self.children), childDepth), displayObject)
        displayObject.parent = self
        if changePositionToRelative: displayObject.move(displayObject.worldX, displayObject.worldY)

    def removeAllChildren(self):
        for i in range(len(self.children), -1, -1):
            self.removeChild(self.children[i])

    def checkBounds(self, bounds):
        if not bounds:
            return pygame.Rect(0,0,0,0)
        elif isinstance(bounds, pygame.Rect):
            return bounds
        elif len(bounds) == 2:
            return pygame.Rect(bounds[0], bounds[1], 0, 0)
        else:
            return pygame.Rect(bounds)


class DisplayMask( DisplayObject ):

    @staticmethod
    def getScrollDisplayChild( display ):
        parent = display.parent
        x, y = display.worldX, display.worldY
        while parent:
            if isinstance(parent, DisplayMask):
                x -= parent._scrollH
                y -= parent._scrollV
            parent = parent.parent
        return x,y

    @staticmethod
    def getScrollParentOfChild( display ):
        parent = display.parent
        while parent:
            if isinstance(parent, DisplayMask): return parent
            parent = parent.parent
        return None

    def __init__(self, bounds=None, visible=True, color=(100,100,100,100)):
        super( DisplayMask, self ).__init__( bounds, visible, color )
        self._scrollH = 0
        self._scrollV = 0
        self.image = pygame.Surface((1000, 1000), pygame.SRCALPHA)

    @property
    def scrollH(self): return self._scrollH

    @property
    def scrollV(self): return self._scrollV

    def addScroll(self, x, y):
        self.setScroll(self._scrollH+x, self._scrollV+y)

    def setScroll(self, x, y):
        self._scrollH, self._scrollV = x, y

    def setScrollToDisplay(self, display):
        if ( self.isChildren( display ) ):
            if display.worldY-self._scrollV < self.worldY:
                self._scrollV = (display.worldY - self.worldY)
            elif display.worldY+display.height-self._scrollV > self.worldY+self.height:
                self._scrollV = display.worldY+display.height-self.worldY-self.height

    def update(self, screen, events=None):
        if self.visible:
            self.image.fill((0,0,0,0))
            self.draw(self.image, events)
            self.updateChildren(self.image, events)

            screen.blit( self.image, (self.worldX, self.worldY), (self.worldX+self._scrollH, self.worldY+self._scrollV, self.width, self.height) )



class InteractiveObject( DisplayObject ):

    def __init__(self, bounds=None, visible=True, color=(100,100,100,100), selectable=True):
        super(InteractiveObject, self).__init__(bounds, visible, color)
        self.selectable = selectable
        self.onFocus = EventHook()
        self.offFocus = EventHook()

        self._isFocus = False

    @property
    def isFocus(self): return self._isFocus

    def update(self, screen, events=None):
        super(InteractiveObject, self).update(screen, events)

    def destroy(self):
        super(InteractiveObject, self).destroy()

    def focus(self):
        m = self.getManager()
        if m: m.setFocus(self)

    def getManager(self):
        p = self
        while p:
            if isinstance(p, DisplayManager): return p
            else: p = p.parent
        return None

    def mouseDown(self, pos):
        pass

    def mouseDrag(self, pos, delta):
        pass

    def mouseUp(self, pos):
        pass

    def mouseWheel(self, scroll):
        print "MOUSE WHEEL: ", scroll

    def enterFocus(self):
        self._isFocus = True
        self.onFocus.fire()

    def exitFocus(self):
        self._isFocus = False
        self.offFocus.fire()


class DisplayManager( DisplayObject ):

    @staticmethod
    def collidepoint(display, point):
        x, y = DisplayMask.getScrollDisplayChild( display )
        return point[0] >= x and point[1] >= y and point[0] < x+display.width and point[1] < y+display.height

    def __init__(self, visible=True, color=(100,100,100,100)):
        super(DisplayManager, self).__init__(None, visible, color)

        self.selectorView = DisplayObject( color=(255, 0, 0, 100) )
        self.selected = None
        self.mouseTarget = None
        self._prevMousePosition = (0,0)

    def update(self, screen, events=None):
        super(DisplayManager, self).update(screen, events)
        self.__checkEvents(events)
        self.__checkFocus()

        if self.selected:
            scrollParent = DisplayMask.getScrollParentOfChild( self.selected )
            if scrollParent: scrollParent.setScrollToDisplay(self.selected)
            self.__drawSelector(screen, self.selected)

    def setFocus(self, interactiveObject):
        if self.selected: self.selected.exitFocus()
        self.selected = interactiveObject
        if self.selected: self.selected.enterFocus()

    def distance(self, x0, y0, x1, y1):
        x, y = x0-x1, y0-y1
        return x*x+y*y

    def getDisplayByPoint(self, obj, position):
        for child in obj.children:
            target = self.getDisplayByPoint(child, position)
            if target: return target
        if isinstance(obj, InteractiveObject) and obj.selectable and DisplayManager.collidepoint(obj, position): #obj._bounds.collidepoint(position[0], position[1]):
            return obj
        return None

    def __drawSelector(self, screen, target):
        x,y = self.__getViewPosition(target)
        self.selectorView.move(x, y)
        self.selectorView.resize(target.width, target.height)
        self.selectorView.draw(screen)

    def __checkFocus(self):
        if not self.selected or not self.selected.visible:
            dist, ob = 99999999999, None
            dist, ob = self.__checkChildrenInputMinDistance(dist, ob, self.children)
            self.setFocus(ob)

    def __checkEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouseTarget = self.getDisplayByPoint(self, event.pos)
                    if self.mouseTarget:
                        self.mouseTarget.mouseDown( event.pos )
                        self._prevMousePosition = event.pos
                        self.setFocus(self.mouseTarget)
                elif event.button == 5 or event.button == 4:#mouse wheel
                    target = self.getDisplayByPoint(self, event.pos)
                    if target: target.mouseWheel( 1 if event.button == 5 else -1 )
            elif event.type == pygame.MOUSEMOTION:
                if self.mouseTarget:
                    delta = ( event.pos[0]-self._prevMousePosition[0], event.pos[1]-self._prevMousePosition[1] )
                    self.mouseTarget.mouseDrag(event.pos, delta)
                    self._prevMousePosition = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.mouseTarget:
                    self.mouseTarget.mouseUp(event.pos)
                    self.mouseTarget = None
            elif self.selected and event.type == pygame.KEYDOWN:
                ob = None
                dist = 99999
                if event.key == pygame.K_UP:
                    dist, ob = self.__getMinInputDistObjInDir(dist, ob, (0,-1), self.children)
                elif event.key == pygame.K_DOWN:
                    dist, ob = self.__getMinInputDistObjInDir(dist, ob, (0,1), self.children)
                elif event.key == pygame.K_LEFT:
                    dist, ob = self.__getMinInputDistObjInDir(dist, ob, (-1,0), self.children)
                elif event.key == pygame.K_RIGHT:
                    dist, ob = self.__getMinInputDistObjInDir(dist, ob, (1,0), self.children)

                if ob != None: self.setFocus(ob)

    def __checkChildrenInputMinDistance(self, dist, ob, children):
        for child in children:
            x, y = self.__getViewPosition(child)
            if child.visible and isinstance(child, InteractiveObject) and child.selectable and self.distance(0, 0, x, y) < dist:
                dist, ob = self.distance(0, 0, x, y), child
            dist, ob = self.__checkChildrenInputMinDistance(dist, ob, child.children)
        return dist, ob

    def __getMinInputDistObjInDir(self, dist, ob, direction, children):
        px, py = self.__getViewPosition(self.selected)
        for child in children:
            x, y = self.__getViewPosition(child)
            diffX, diffY = x - px, y - py

            if (child.visible and
                isinstance(child, InteractiveObject) and
                child.selectable and
                child != self.selected and
                (direction[0] == 0 or self.__isSameSign(diffX, direction[0])) and
                (direction[1] == 0 or self.__isSameSign(diffY, direction[1])) and
                self.distance(x, y, px, py) < dist):
                dist, ob = self.distance(x, y, px, py), child
            dist, ob = self.__getMinInputDistObjInDir(dist, ob, direction, child.children)
        return dist, ob

    def __getViewPosition(self, child):
        return DisplayMask.getScrollDisplayChild(child)

    def __isSameSign(self, x, y):
        if x==0 or y==0: return False
        return (x >= 0) ^ (y < 0)





class SurfaceManager:
    surfaces = {}
    @staticmethod
    def getSurface(imageAddress):
        if not imageAddress: return None
        if not (imageAddress in SurfaceManager.surfaces):
            SurfaceManager.surfaces[imageAddress] = pygame.image.load(imageAddress)
        return SurfaceManager.surfaces[imageAddress]
    @staticmethod
    def registerSurface(imageAddress):
        if not imageAddress: return
        if not (imageAddress in SurfaceManager.surfaces):
            SurfaceManager.surfaces[imageAddress] = pygame.image.load(imageAddress)