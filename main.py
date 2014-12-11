# coding=UTF-8
"""<font color=\"#ffd200\" face=\"sys_24_border\">Pygame - pytext</font>

<font color=\"#a3a3a3\" face=\"sys_8_border\">Desenvolvedor: Allan Oliveira</font>

A biblioteca <font color='#33cc99'>pytext</font> tem como foco principal a criação de um um campo de texto rico, que permita a modificação dinâmica do conteúdo, assim como a inserção de diferente fontes e efeitos gráficos.
Para criação do campo de texto, ele utiliza bitmap font, ou seja, uma arquivo xml com as informações de cada caracter e uma, ou mais, imagens com os caracteres da font.
O <font color='#33cc99'>pytext</font> foi escrito utilizando a linguagem de programação python, e como necessidade especial ele necessita também da biblioteca gráfica pygame.
"""

__author__ = 'Allan'

from pytext.display import *
from pytext.ui import *

pygame.init()
screen = pygame.display.set_mode((480, 320))
isDone = False

fonts = {
    "sys_8": Font("pytext/assets/fonts/sys_8.fnt"),
    "sys_8_border": Font("pytext/assets/fonts/sys_8_border.fnt"),
    "sys_16": Font("pytext/assets/fonts/sys_16.fnt"),
    "sys_16_border": Font("pytext/assets/fonts/sys_16_border.fnt"),
    "sys_24": Font("pytext/assets/fonts/sys_24.fnt"),
    "sys_24_border": Font("pytext/assets/fonts/sys_24_border.fnt"),

    "sys2_16": Font("pytext/assets/fonts/sys2_16.fnt"),
    "sys2_16_border": Font("pytext/assets/fonts/sys2_16_border.fnt")
}

view = DisplayManager()


view.selectorView = UIImage( "pytext/assets/ui/selected.gif",
                             imageType=UIImage.TYPE_NINESLICE,
                             nineRect=(6,6,32-12,32-12) )

view.addChild( UIImage("pytext/assets/ui/bg01.gif") )
view.addChild( UIImage("pytext/assets/ui/box.gif",
                     ((480-360)/2, 40, 360, 240),
                     color=(0,0,255),
                     imageType=UIImage.TYPE_NINESLICE,
                     nineRect=(10,10,380-20,63-20),
                     fillCenter=True,
                     autoAdjust=False),
               True )

t = TextField( __doc__*2,
               fonts["sys_8"],
               ((480-330)/2, 40, 330, 240),
               selectable=True,
               wordwrap=True,
               color=(255,255,255),
               htmlFontDict=fonts,
               align=TextField.ALIGN_CENTER )

view.addChild(t, changePositionToRelative=True)


button = UIButton( bounds=(20,20),
                   label="Button",
                   font=fonts["sys_8_border"],
                   color=(255,255,0,255))
#view.addChild(button)




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