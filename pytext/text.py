# coding=UTF-8
#
# Copyright (C) 2014 Allan Oliveira. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#



__author__  = "Allan Oliveira <allanolivei@gmail.com>"


import os
import re
import pyperclip
import time
from display import *

#Function util
def clamp(value, minValue, maxValue): return min( maxValue , max( minValue, value ) )

class Font(object):

    DEFAULT_KEY = "(255, 255, 255)"

    def __init__(self, fileName=None, letterSpaceScale=1):
        self.__isComplete = False
        self.lineHeight = 0
        self.size = 0
        self.images = []
        self.char = {}
        if fileName: self.load(fileName, letterSpaceScale)

    def load(self, filename, letterSpaceScale=1):
        filename = filename
        basedir = os.path.dirname(filename)
        self.char.clear()
        del self.images[:]

        f = open(filename)

        #char id=81 x=4 y=4 width=10 height=22 xoffset=0 yoffset=6 xadvance=12 page=0 chnl=0 letter="Q"
        for line in f:
            line_type = line[:line.index(" ")]
            vars = dict( re.findall('(\w+) *= *\"*([^ \n\"]*)\"*', line) )
            if line_type == "char":
                for k,v in vars.iteritems() :
                    if self.isIntNumber(v):#v.isdigit():
                        vars[k] = int(vars[k])
                vars["xadvance"] *= letterSpaceScale

                if( vars["id"] <= 256 ):
                    #key = chr(vars["id"])
                    self.char[vars["id"]] = vars
                pass
            elif line_type == "info":
                self.size = int(vars.get("size"))
                pass
            elif line_type == "common":
                self.lineHeight = int(vars.get("lineHeight"))
                pass
            elif line_type == "page":
                image_path = os.path.join(basedir, vars["file"])
                self.images.append( {Font.DEFAULT_KEY:pygame.image.load(image_path)} )
                pass
            elif line_type == "chars":
                pass

        space = self.char.get(ord(' '))
        tabSpace = space['xadvance'] if space else 5
        #tab
        self.char[9] = {"xadvance":tabSpace*5, "x":0, "y":0, "width":0, "height":0, "page":0, "xoffset":0, "yoffset":0}

    def drawChar(self, surface, char, position, color=None ):
        data = self.char.get(ord(char))
        xadvance = 0
        if data :
            index = int(data["page"])
            pos =  (position[0]+data["xoffset"], position[1]+data["yoffset"])
            xadvance = data["xadvance"]
            surface.blit( self.getImage(index, color), pos, (data["x"], data["y"], data["width"], data["height"]) )
        return xadvance

    def getImage(self, index, color=None):
        c = str(color) if color else Font.DEFAULT_KEY
        result = self.images[index].get(c)
        if not result:
            result = self.images[index][Font.DEFAULT_KEY].copy()
            result.fill(color, None, special_flags=pygame.BLEND_RGB_MULT)
            self.images[index][c] = result

        return result

    def isIntNumber(self, value):
        if len(value)>0 and value[0] in ('-', '+'):
            return value[1:].isdigit()
        return value.isdigit()



class TextField(InteractiveObject):

    ALIGN_LEFT = 0
    ALIGN_RIGHT = 1
    ALIGN_CENTER = 0.5

    def __init__( self, text, font,
                  bounds=None, visible=True, color=(0,0,0), selectable=True,
                  wordwrap=False, letterSpacing=1, lineSpacing=1, inputText=False,
                  autoAdjust=False, align=ALIGN_LEFT, htmlFontDict=None ):
        super(TextField, self).__init__(bounds, visible, color, selectable)
        self._scrollV = 0
        self._scrollH = 0
        self.autoAdjust = autoAdjust
        self.wordwrap = wordwrap
        self.inputText = inputText
        self.text = u""
        self.lineSpacing = lineSpacing
        self.letterSpacing = letterSpacing
        self.markerColor = [color[0], color[1], color[2], 90]
        self.selectArea = [0, 0]
        self.align = align
        self.fonts = [ {"end":len(self.text), "font":font, "color":color} ]
        self.lineData = []
        self.contentHeight = 0
        self.contentWidth = self.width
        self.invalidate = False
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        #a = 97,
        #á = 225, â = 226, ã = 227
        #´=180,^=94,~=126
        #self.sinals = {180:{97:225}, 94:{}, 126:{}}
        #self.history = []

        self.insertHtml(text, 0, font_dict=htmlFontDict)

    @property
    def width(self): return self._bounds.width

    @property
    def height(self):  return self._bounds.height

    @width.setter
    def width(self, value):
        if value == self._bounds.width: return
        super(TextField, self).width(value)
        self.updateLineData()

    @height.setter
    def height(self, value):
        if value == self._bounds.height: return
        super(TextField, self).height(value)
        self.updateLineData()

    @property
    def lineLength(self):
        return len(self.lineData)

    def append(self, content, color=None, font=None):
        self.insert(content, len(self.text), 0, color, font)

    def insert(self, content, index, removeLength=0, color=None, font=None):
        index = clamp(index, 0, len(self.text))

        if removeLength > 0:
            init, end = index, index + removeLength
            i = 0

            while i < len(self.fonts):
                if self.fonts[i]["end"] > index:
                    if self.fonts[i]["end"] < end:
                        self.fonts[i]["end"] = index
                    else:
                        self.fonts[i]["end"] -= removeLength
                    if i > 0 and self.fonts[i]["end"] == self.fonts[i-1]["end"]:
                        del self.fonts[i]
                        continue

                i += 1

        initTextLen = len(self.text)
        self.text = self.text[:index]+content+self.text[index+removeLength:]
        fontIndex = self.getFontByIndex(index-1)

        if len(self.fonts) == 0:
            self.fonts.append({"end":len(self.text), "font":font, "color":color})
        elif (not font or self.fonts[fontIndex]["font"] == font) and (not color or color == self.fonts[fontIndex]["color"]):
            self.fonts[fontIndex]["end"] += len(content)
        else:

            previousEnd = self.fonts[fontIndex]["end"]
            self.fonts[fontIndex]["end"] = index
            self.fonts.insert(fontIndex+1, {"end":index, "font":font if font else self.fonts[fontIndex]["font"], "color":color})
            if previousEnd > index:
                self.fonts.insert(fontIndex+2, {"end":previousEnd, "font":self.fonts[fontIndex]["font"], "color":self.fonts[fontIndex]["color"] })

        for i in range(fontIndex+1, len(self.fonts)):
            self.fonts[i]["end"] += len(content)

        if index >= initTextLen-1:
            self.updateLineData( len(self.lineData)-2 )
        else:
            for i in range(0, len(self.lineData)):
                if( self.lineData[i]["end"] > index ):
                    self.updateLineData( i )
                    break

    def insertHtml(self, content, index=99999999, font_dict=None):
        index = clamp(index, 0, len(self.text))
        content = content if isinstance(content, unicode) else content.decode('utf-8')
        reg = r"\<(?P<is_closed>\/?)(?P<tag_type>\w+)\s?(?P<parameters>[^>]*)\>"
        fontIndex = self.getFontByIndex(index-1)
        pos = 0

        tagProperties = [ { "font": self.fonts[fontIndex]["font"], "color": self.fonts[fontIndex]["color"] } ]

        for m in re.finditer(reg, content):
            prop = tagProperties[len(tagProperties)-1]
            self.insert( content[pos:m.start()], index, 0, prop["color"], prop["font"] )
            index += m.start()-pos
            pos = m.end()
            if m.group("is_closed"):
                if len(tagProperties) > 1: tagProperties.pop()
            else:
                vars = dict( re.findall('(\w+) *= *[\"\']+([^ \n\"\']*)[\"\']+', m.group("parameters")) )
                tagProperties.append(
                    { "font": font_dict[ vars["face"] ] if vars.has_key("face") else None,
                      "color": self.hexToRgb(vars["color"]) if vars.has_key("color") else None }
                )
        prop = tagProperties[len(tagProperties)-1]

        self.insert( content[pos:len(content)], index, 0, prop["color"], prop["font"] )

    def addInSelection(self, content):
        if self.selectArea[0] != self.selectArea[1]:
            self.remove( min(self.selectArea[0], self.selectArea[1]), abs(self.selectArea[1] - self.selectArea[0]) )
            self.select( min(self.selectArea[0], self.selectArea[1]) )
        self.insert(content, self.selectArea[0])
        self.select(self.selectArea[0]+1)

    def setFont(self, init, end, font, color=None):
        fontIndex = self.getFontByIndex(init-1)
        if len(self.fonts) == 0:
            self.fonts.append({"end":len(self.text), "font":font, "color":color})
        elif font and font != self.fonts[fontIndex]["font"] or color and color != self.fonts[fontIndex]["color"]:
            previousEnd = self.fonts[fontIndex]["end"]
            self.fonts[fontIndex]["end"] = init
            self.fonts.insert(fontIndex+1, {"end":end, "font":font if font else self.fonts[fontIndex]["font"], "color":color})
            if previousEnd > init:
                self.fonts.insert(fontIndex+2, {"end":previousEnd, "font":self.fonts[fontIndex]["font"], "color":self.fonts[fontIndex]["color"] })

        for i in range(0, len(self.lineData)):
            if( self.lineData[i]["end"] > init ):
                self.updateLineData( i )
                break

    def remove(self, init, removeLenght=1):
        self.insert("", init, removeLenght)

    def clear(self):
        self.remove(0, len(self.text))

    #get charIndex by position(x,y)
    def getCharIndexByPosition(self, x, y):
        line = self.getLineByPosition(y)
        return self.getCharIndexInLineByPos(x, line)

    #get charIndex by (xPos, line)
    def getCharIndexInLineByPos(self, xPosition, line):
        if line >= len(self.lineData): return 0

        #x = (max(self.width, self.contentWidth) - self.lineData[line]["lineWidth"]) / self.align if self.align > 0 else 0
        x = (max(self.width, self.contentWidth) - self.lineData[line]["lineWidth"]) * self.align
        fontIndex = self.getFontByIndex(self.lineData[line]["init"])

        for char in range(self.lineData[line]["init"], self.lineData[line]["end"]):
            while( char >= self.fonts[fontIndex]["end"] ): fontIndex += 1
            charData = self.fonts[fontIndex]["font"].char.get(ord(self.text[char]))
            if charData:
                x += charData["xadvance"]*self.letterSpacing
                if x > xPosition+charData["xadvance"]*self.letterSpacing*0.5: return char

        if self.lineData[line]["init"] == self.lineData[line]["end"]:
            return self.lineData[line]["end"]
        return self.lineData[line]["end"]-1

    #get line by position(y)
    def getLineByPosition(self, yPosition):
        y = 0
        for index in range(0, len(self.lineData)):
            y += self.lineData[index]["lineHeight"]
            if y > yPosition: return index
        return len(self.lineData)

    #get line by charIndex
    def getLineByCharIndex(self, charIndex):
        for i in range(0, len(self.lineData)):
            if self.lineData[i]["end"] > charIndex :
                return  i
        return len(self.lineData)-1

    #get position(x,y) by charIndex
    def getPositionByCharIndex(self, index, sideRight=False):
        if len(self.lineData) == 0: return self.width/self.align if self.align>0 else 0,0
        index = min(index, len(self.text))

        line = self.getLineByCharIndex(index)
        #x, y = (max(self.width, self.contentWidth) - self.lineData[line]["lineWidth"]) / self.align if self.align > 0 else 0, 0
        x, y = (max(self.width, self.contentWidth) - self.lineData[line]["lineWidth"]) * self.align if self.align > 0 else 0, 0
        fontIndex = self.getFontByIndex(index)

        for char in range(self.lineData[line]["init"], index+1 if sideRight else index):
            while( char >= self.fonts[fontIndex]["end"] ): fontIndex += 1
            charData = self.fonts[fontIndex]["font"].char.get(ord(self.text[char]))
            if charData: x += charData["xadvance"]*self.letterSpacing


        for index in range(0, line):
            y += self.lineData[index]["lineHeight"]

        return x, y

    def getFontByIndex(self, index):
        for i in range(len(self.fonts)):
            if self.fonts[i]["end"] > index:
                return i
        return 0

    def addScroll(self, x, y):
        self.setScroll(self._scrollH+x, self._scrollV+y)

    def setScroll(self, x, y):
        h, v = clamp(x, 0, max(0,self.contentWidth-self.width)), clamp(y, 0, max(0,self.contentHeight-self.height))
        if self._scrollH != h or self._scrollV != v:
            self._scrollH, self._scrollV = h, v
            self.invalidate = True

    def setScrollToLine(self, line):
        line = min(line, len(self.lineData))
        y = 0
        for i in range(line): y += self.lineData[i]["lineHeight"]
        self.setScroll(self._scrollH, y)

    def setScrollToSelected(self):
        if len(self.lineData) == 0:
            self.setScroll(0,0)
            return

        cursorPos = self.getPositionByCharIndex( self.selectArea[1] )
        line = self.getLineByCharIndex(self.selectArea[1])
        h, v = self._scrollH, self._scrollV

        if cursorPos[1] < self._scrollV:
            v = cursorPos[1]
        elif cursorPos[1]+self.lineData[line]["lineHeight"]-self._scrollV > self.height:
            v = cursorPos[1]+self.lineData[line]["lineHeight"]-self.height

        if cursorPos[0] < self._scrollH:
            h = cursorPos[0]
        elif cursorPos[0]+1-self._scrollH > self.width:
            h = cursorPos[0]+1-self.width

        self.setScroll(h, v)

    def isInMaxScrollV(self): return self._scrollV >= max(0,self.contentHeight-self.height)

    def isInMaxScrollH(self): return self._scrollH >= max(0,self.contentWidth-self.width)

    def getMinLineInView(self):
        y = 0
        for line in range(len(self.lineData)):
            if y > self._scrollV: return max(0,line-1)
            y += self.lineData[line]["lineHeight"]
        return max(0,line-1)

    def select(self, init, end=-1):
        init = clamp(init, 0, len(self.text))
        if end <= -1 :
            end = init
        end = clamp(end, 0, len(self.text))

        self.selectArea[0] = init
        self.selectArea[1] = end

        self.setScrollToSelected()

    def selectUp(self, addForSelection=False):
        line = self.getLineByCharIndex(self.selectArea[1])
        if line <= 0: return
        x,y = self.getPositionByCharIndex(self.selectArea[1])
        if addForSelection:
            self.select( self.selectArea[0], self.getCharIndexInLineByPos(x, line-1) )
        else:
            self.select( self.getCharIndexInLineByPos(x, line-1) )

    def selectDown(self, addForSelection=False):
        line = self.getLineByCharIndex(self.selectArea[1])
        if line > len(self.lineData)-2: return
        x,y = self.getPositionByCharIndex(self.selectArea[1])
        if addForSelection:
            self.select( self.selectArea[0], self.getCharIndexInLineByPos(x, line+1) )
        else:
            self.select( self.getCharIndexInLineByPos(x, line+1) )

    def selectNext(self, addForSelection=False, searchSpace=False):
        if addForSelection:
            self.select(self.selectArea[0], min(len(self.text), self.selectArea[1]+1))
        else:
            self.select(self.selectArea[1]+1)

    def selectPrev(self, addForSelection=False, searchSpace=False):
        if addForSelection:
            self.select(self.selectArea[0], max(0, self.selectArea[1]-1))
        else:
            self.select(self.selectArea[1]-1)

    def mouseDown(self, pos):
        super(TextField, self).mouseDown(pos)
        if ( pygame.key.get_mods() & pygame.KMOD_SHIFT ):
            self.select( self.selectArea[0], self.getCharIndexByPosition( pos[0]-self.worldX+self._scrollH, pos[1]-self.worldY+self._scrollV ) )
        else:
            self.select( self.getCharIndexByPosition( pos[0]-self.worldX+self._scrollH, pos[1]-self.worldY+self._scrollV ) )

    def mouseDrag(self, pos, delta):
        super(TextField, self).mouseDrag(pos, delta)
        self.select( self.selectArea[0], self.getCharIndexByPosition( pos[0]-self.worldX+self._scrollH, pos[1]-self.worldY+self._scrollV ) )

    def mouseWheel(self, scroll):
        self.addScroll(0, scroll * 20)

    def update(self, screen, events=None):
        super(TextField, self).update(screen, events)
        self.__checkEvents(events)

    def draw(self, screen, events):
        if self.invalidate:
            lines = self.__getDrawArea()
            self.image.fill((0,0,0,0))
            imageSize = self.image.get_clip()
            if imageSize.width != self.width or imageSize.height != self.height:
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for line in range(lines[0], lines[1]):
                self.drawLine(self.image, line)
            self.invalidate = False

        self.__drawSelectArea(screen)
        screen.blit( self.image, self._bounds )
        self.__drawMarker(screen)

    def drawLine(self, destination, line):
        if line >= len(self.lineData) : return

        pos = [0, 0]
        lineD = self.lineData[line]
        fontIndex = self.getFontByIndex(lineD["init"])
        for i in range(0, line):
            pos[1] += self.lineData[i]["lineHeight"]

        pos[0] -= self._scrollH
        pos[1] -= self._scrollV
        #pos[0] += (max(self.width,self.contentWidth) - lineD["lineWidth"]) / self.align if self.align > 0 else 0
        pos[0] += (max(self.width,self.contentWidth) - lineD["lineWidth"]) * self.align

        for character in range(lineD["init"], lineD["end"]):
            while( character >= self.fonts[fontIndex]["end"] ): fontIndex += 1
            pos[0] += self.fonts[fontIndex]["font"].drawChar(destination, self.text[character], pos, self.fonts[fontIndex]["color"]) * self.letterSpacing

    def updateLineData(self, initLine = 0):
        total = len(self.text)

        if( initLine <= 0 ):
            line, i = 0, 0
        elif( initLine-1 < len(self.lineData) ):
            line, i = initLine, self.lineData[initLine]["init"]
        else:
            return

        while i < total:
            lineInf = { "init":i, "end":self.__getIndexEndLine(i) }
            lineInf["lineHeight"] = self.__checkLineHeight(lineInf)
            lineInf["lineWidth"] = self.__checkLineWidth(lineInf)
            self.__addLineData(line, lineInf)

            i = self.lineData[line]["end"]
            line += 1

        if( len(self.text) > 0 and self.text[len(self.text)-1] == '\n' ):
            lineInf = { "init":i, "end":i, "lineWidth":0 }
            lineInf["lineHeight"] = self.__checkLineHeight(lineInf)
            self.__addLineData( line, lineInf )

            line += 1

        if len(self.lineData) > line:
            del self.lineData[line:]
            self.invalidate = True

        self.contentHeight = 0
        self.contentWidth = 0
        for line in self.lineData:
            self.contentHeight += line["lineHeight"]
            self.contentWidth = max(self.contentWidth, line["lineWidth"])

        if self.autoAdjust:
            self._bounds.width, self._bounds.height = self.contentWidth, self.contentHeight

        self._scrollH = clamp(self._scrollH, 0, max(0,self.contentWidth-self.width))
        self._scrollV = clamp(self._scrollV, 0, max(0,self.contentHeight-self.height))

    def searchSpecialChar(self, init, forward=True):
        for init in range(init, len(self.text)):
            if self.text[init] != ' ' and self.text[init] != '\n':
                break

        return  init + re.search("([\s.:(),])", self.text[init:]).start()

    def hexToRgb(self, hex) :
        reg = "#?([A-F\d]{2})([A-F\d]{2})([A-F\d]{2})"
        result = re.match(reg, hex, re.IGNORECASE)
        return (int(result.group(1), 16),
                int(result.group(2), 16),
                int(result.group(3), 16)) if result else None

    def enterFocus(self):
        super(TextField, self).enterFocus()
        self.previous_pygame_repeat = pygame.key.get_repeat()
        pygame.key.set_repeat(300,100)

    def exitFocus(self):
        super(TextField, self).exitFocus()
        pygame.key.set_repeat( self.previous_pygame_repeat[0], self.previous_pygame_repeat[1] )

    def __drawSelectArea(self, destination):
        if not self._isFocus: return

        init, end = min(self.selectArea[0], self.selectArea[1]), max(self.selectArea[0], self.selectArea[1])

        if init != end:
            endLine = self.getLineByCharIndex(end)
            currentLine = self.getLineByCharIndex(init)
            self.markerColor[3] = 70
            for currentLine in range(currentLine, endLine+1):
                a = clamp(self.lineData[currentLine]["init"],init, end)
                b = clamp(  self.lineData[currentLine]["end"] - (1 if currentLine < len(self.lineData)-1 else 0)  , init, end)

                posA = self.getPositionByCharIndex(a)
                posB = self.getPositionByCharIndex(b)
                self.__drawBox(destination, [self.worldX+posA[0]-self._scrollH, self.worldY+posA[1]-self._scrollV, posB[0]-posA[0]+1, self.lineData[currentLine]["lineHeight"]], self.markerColor)

    def __drawMarker(self, destination):
        if not self._isFocus or time.clock()%0.8 > 0.4: return

        init, end = min(self.selectArea[0], self.selectArea[1]), max(self.selectArea[0], self.selectArea[1])
        endLine = self.getLineByCharIndex(end)

        cursorPos = self.getPositionByCharIndex( self.selectArea[1] )
        self.markerColor[3] = 255

        lineHeight = 16
        if len(self.lineData) > 0: lineHeight = self.lineData[endLine]["lineHeight"]
        elif len(self.fonts) > 0:
            char = self.fonts[0]["font"].char.get(ord("A"))
            if char: lineHeight = char["height"] + char["yoffset"]

        offset = 0 if len(self.lineData) == 0 or self.selectArea[1]-self._scrollH < self.width else -1
        if cursorPos[0] > self._bounds.width-self._scrollH: offset -= 3

        self.__drawBox(destination, [self._bounds.x+cursorPos[0]-self._scrollH+offset, self._bounds.y+cursorPos[1]-self._scrollV, 1, lineHeight], self.markerColor)

    def __drawBox(self, destination, area, color):
        if self._bounds.colliderect(area):
            if area[1] < self._bounds.y:
                area[3] += area[1] - self._bounds.y
                area[1] = self._bounds.y
            if area[0] < self._bounds.x:
                area[2] += area[0] - self._bounds.x
                area[0] = self._bounds.x
            if area[0]+area[2] > self._bounds.right: area[2] = self._bounds.right-area[0]
            if area[1]+area[3] > self._bounds.bottom: area[3] = self._bounds.bottom-area[1]
            pygame.gfxdraw.box(destination, area, color)

    def __getIndexEndLine(self, init=0):
        previousWord = init
        wordSize = 0
        lineSize = 0
        total = len(self.text)
        fontIndex = self.getFontByIndex(init)

        for i in range(init, total):
            while( i >= self.fonts[fontIndex]["end"] ): fontIndex += 1
            char = self.text[i]

            if not self.wordwrap:
                if char == '\n': return i+1
                continue

            data = self.fonts[fontIndex]["font"].char.get(ord(char))
            charSize = data["xadvance"]*self.letterSpacing if data else 0

            if char == '\n':
                if lineSize+wordSize >= self._bounds.width:
                    return previousWord+1
                else:
                    return i+1
            #Em cada espaco verifica se a palavra montada ainda esta contida na linha, caso nao, retorna o fim da palavra anterior
            if char == ' ':
                if lineSize+wordSize >= self._bounds.width:
                    #+1 do caracter espaco : +1 pois e o primeiro item depois do final
                    return previousWord+1
                lineSize += wordSize
                wordSize, previousWord = 0, i

            #Uma palavra maior que o tamanho da linha
            if lineSize == 0 and wordSize+charSize > self._bounds.width:
                if i - init == 0 :
                    self.width = wordSize+charSize
                    return  i+1
                else : return i

            wordSize += charSize


        if self.wordwrap and lineSize+wordSize >= self._bounds.width:
            #+1 do caracter espaco : +1 pois e o primeiro item depois do final
            if( lineSize == 0 ): return total-1
            else: return previousWord+1

        return len(self.text)

    def __checkLineHeight(self, lineInf):
        init = lineInf["init"]
        end = lineInf["end"]
        fontIndex = self.getFontByIndex(init)
        lineHeight = self.fonts[fontIndex]["font"].lineHeight
        for i in range(init, end):#self.getEndLine(i)):
            #recupera fonte atual
            while( i >= self.fonts[fontIndex]["end"] ):
                fontIndex += 1
                lh = self.fonts[fontIndex]["font"].lineHeight
                if lh > lineHeight : lineHeight = lh
        return lineHeight

    def __checkLineWidth(self, lineInf):
        fontIndex = self.getFontByIndex(lineInf["init"])
        lineWidth = 0
        for i in range(lineInf["init"], lineInf["end"]):
            while( i >= self.fonts[fontIndex]["end"] ): fontIndex += 1
            char = self.text[i]
            data = self.fonts[fontIndex]["font"].char.get(ord(char))
            lineWidth += data["xadvance"]*self.letterSpacing if data else 0

        if data: lineWidth += data["width"]-data["xadvance"]
        return lineWidth

    def __addLineData(self, index, lineInf):
        if index >= len(self.lineData):
            self.lineData.append(lineInf)
            self.invalidate = True
        elif self.lineData[index]["init"] != lineInf["init"] or self.lineData[index]["end"] != lineInf["end"] or self.lineData[index]["lineHeight"] != lineInf["lineHeight"]:
            self.lineData[index] = lineInf
            self.invalidate = True

    def __getDrawArea(self):
        y = 0
        init, end = 0, len(self.lineData)
        bottom = self._scrollV + self._bounds.height
        for i in range(0, len(self.lineData)):
            if y <= self._scrollV: init = i
            if y >= bottom: return (init, i)
            y += self.lineData[i]["lineHeight"]
        return (init, end)

    def __checkEvents( self, events ):
        if not self._isFocus or not events: return

        mods = pygame.key.get_mods()
        shift = mods & pygame.KMOD_SHIFT
        ctrl = mods & pygame.KMOD_CTRL

        for i in range(len(events)-1, -1, -1):
            event = events[i]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selectPrev(shift, ctrl)
                elif event.key == pygame.K_RIGHT:
                    self.selectNext(shift, ctrl)
                elif event.key == pygame.K_UP:
                    self.selectUp(shift)
                elif event.key == pygame.K_DOWN:
                    self.selectDown(shift)
                elif event.key == pygame.K_a and ctrl:
                    self.select(0, len(self.text))
                elif (event.key == pygame.K_c or (event.key == pygame.K_x and self.inputText)) and ctrl:
                    init = min(self.selectArea[0], self.selectArea[1])
                    end = max(self.selectArea[0], self.selectArea[1])
                    try:
                        #pygame.scrap.put (pygame.SCRAP_TEXT, self.text[init:end])
                        pyperclip.copy(self.text[init:end])
                    except:
                        print "O modulo scrap deve ser inicializado para liberar esta funcao."
                    if event.key == pygame.K_x:
                        self.remove( min(self.selectArea[0], self.selectArea[1]), abs(self.selectArea[1] - self.selectArea[0]) )
                        self.select( min(self.selectArea[0], self.selectArea[1]) )
                elif event.key == pygame.K_HOME:
                    line = self.getLineByCharIndex(self.selectArea[1])
                    if shift:
                        self.select( self.selectArea[0], self.lineData[line]["init"] )
                    else:
                        self.select( self.lineData[line]["init"] )
                elif event.key == pygame.K_END:
                    line = self.getLineByCharIndex(self.selectArea[1])
                    if shift:
                        self.select( self.selectArea[0], self.lineData[line]["end"]-1 if line < len(self.lineData)-1 else self.lineData[line]["end"] )
                    else:
                        self.select( self.lineData[line]["end"]-1 if line < len(self.lineData)-1 else self.lineData[line]["end"] )
                    pass
                elif self.inputText:
                    if event.key == pygame.K_BACKSPACE:
                        if self.selectArea[0] != self.selectArea[1]:
                            self.remove( min(self.selectArea[0], self.selectArea[1]), abs(self.selectArea[1] - self.selectArea[0]) )
                            self.select( min(self.selectArea[0], self.selectArea[1]) )
                        else:
                            self.remove( self.selectArea[0]-1 )
                            self.select( self.selectArea[0]-1 )
                    elif event.key == pygame.K_DELETE:
                        if self.selectArea[0] != self.selectArea[1]:
                            self.remove( min(self.selectArea[0], self.selectArea[1]), abs(self.selectArea[1] - self.selectArea[0]) )
                            self.select( min(self.selectArea[0], self.selectArea[1]) )
                        else:
                            self.remove(self.selectArea[0])
                    elif event.key == pygame.K_v and ctrl:
                        try:
                            pasteContent = pyperclip.paste()
                            self.addInSelection( pasteContent )
                            self.select(self.selectArea[1]+len(pasteContent)-1)
                        except:
                            print "Nao foi possivel colar a selecao."
                    elif event.key == pygame.K_z and ctrl:
                        #self.backHistory()
                        pass
                    elif event.key == pygame.K_TAB:
                        if shift and self.selectArea[0] == self.selectArea[1]:
                            if self.text[self.selectArea[0]-1] == '\t':
                                self.remove(self.selectArea[0]-1)
                                self.select(self.selectArea[0]-1)
                        else:
                            self.addInSelection('\t')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.addInSelection('\n')
                    elif event.key <= 265:
                        if event.key == 27: return #27 = esc key
                        character = event.unicode if event.unicode else chr(event.key)
                        if len(character) == 0: return
                        self.addInSelection( event.unicode )
                    else:
                        continue
                else:
                    continue

                del events[i]




if __name__ == "__main__":
    screen = pygame.display.set_mode((480, 320))

    t = TextField("Teste editor de texto",
                  Font("assets/fonts/sys2_16.fnt"),
                  bounds=(0,0,480,320),
                  wordwrap=True,
                  autoAdjust=False,
                  color=(0,0,0),
                  selectable=True,
                  inputText=True)
    view = DisplayManager((0,0,0,0))
    view.addChild(t)

    while 1:
        screen.fill((255,255,255))
        view.update(screen, pygame.event.get())
        pygame.display.update()