# coding=UTF-8
"""
"""

__author__ = 'Allan'

from pytext.ui import *

pygame.init()
screen = pygame.display.set_mode((480, 320))
isDone = False

Font.addFonts( {
    "sys_8": Font("pytext/assets/fonts/sys_8.fnt"),
    "sys_8_border": Font("pytext/assets/fonts/sys_8_border.fnt"),
    "sys_16": Font("pytext/assets/fonts/sys_16.fnt"),
    "sys_16_border": Font("pytext/assets/fonts/sys_16_border.fnt"),
    "sys_24": Font("pytext/assets/fonts/sys_24.fnt"),
    "sys_24_border": Font("pytext/assets/fonts/sys_24_border.fnt"),
    "sys2_16": Font("pytext/assets/fonts/sys2_16.fnt"),
    "sys2_16_border": Font("pytext/assets/fonts/sys2_16_border.fnt")
} )

view = DisplayManager()

"""
view.selectorView = UIImage( "pytext/assets/ui/selected.gif",
                             imageType=UIImage.TYPE_NINESLICE,
                             nineRect=(6,6,32-12,32-12) )

view.addChild( UIImage("pytext/assets/ui/bg01.gif") )
view.addChild( UIImage("pytext/assets/ui/box.gif",
                     bounds=((480-360)/2, 40, 360, 240),
                     color=(0,0,255),
                     imageType=UIImage.TYPE_NINESLICE,
                     nineRect=(10,10,380-20,63-20),
                     fillCenter=True,
                     autoAdjust=False),
               True )



t = TextField( text=__doc__*2,
               font="sys_8",
               bounds=((480-330)/2, 40, 330, 240),
               selectable=True,
               wordwrap=True,
               color=(255,255,255),
               align=TextField.ALIGN_CENTER )

view.addChild(t, changePositionToRelative=True)


button = UIButton( bounds=(20,20),
                   label="Button",
                   font=fonts["sys_8_border"],
                   color=(255,255,0,255))"""

view.selectorView = UIImage( "pytext/assets/ui/selected.gif",
                             imageType=UIImage.TYPE_NINESLICE,
                             nineRect=(6,6,32-12,32-12) )

#view.addChild( UIDeserialize.getContent("xml/menu.xml") )

#view.addChild(button)

"""options = ["TEXTAREA", "INPUTEXT", "SCROLLBAR", "LIST", "EXIT"]

view.addChild( UIImage("pytext/assets/ui/bg02.gif") )
view.addChild( UITextField(bounds=( 133, 24, 215, 48 ), font="sys_24_border", text="PYTEXT", color=(70,215,237), selectable=False, align=UITextField.ALIGN_CENTER) )
grid = UIGrid( name="grid", bounds=( (screen.get_width()-240)/2, 100 ), distanceHorizontal=0, distanceVertical=40, numberOfColumns=0 )
for i in range(len(options)):
    button = UIButton( name="bt"+str(i), label=options[i], font="sys_16_border", bounds=(0,0,240,40), autoAdjust=False, color=(51,255,0), padding=(0,0,0,0) )
    grid.addChild(button)
view.addChild(grid)

"""


menu = UIDeserialize.getContent("xml/menu.xml")
textArea = UIDeserialize.getContent("xml/text_view.xml")
inputText = UIDeserialize.getContent("xml/text_view.xml")
scrollBar = UIDeserialize.getContent("xml/text_view.xml")
list = UIDeserialize.getContent("xml/text_view.xml")

view.addChild( menu )

def menuHandler( bt ):
    if bt.name == "b0":
        view.removeAllChildren()
        view.addChild( textArea )
    if bt.name == "b1":
        view.removeAllChildren()
        view.addChild( inputText )
    if bt.name == "b2":
        view.removeAllChildren()
        view.addChild( scrollBar )
    if bt.name == "b3":
        view.removeAllChildren()
        view.addChild( list )
    if bt.name == "b4":
        global isDone
        isDone = True

for i in range(5):
    view.findChildByName("b"+str(i), True).onClick += menuHandler

#def __init__(self, distanceHorizontal, distanceVertical, numberOfColumns=999,
#                 name="", bounds=None, visible=True, color=(100,100,100,100)):


#list = UIList(bounds=(100,30,300,32*3+10*2), font=fonts["sys_8"], options=["Allan Oliveira", "Diego Camargo", "Igor Avelar", "Fernando Simon", "Santiago Lemos"])
#view.addChild(list)

#pygame loop normal
while not isDone:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            isDone = True

    screen.fill((0,0,0))

    view.update(screen, events)

    pygame.display.update()

pygame.quit()