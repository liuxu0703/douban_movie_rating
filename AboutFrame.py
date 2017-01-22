# -*- coding: utf-8 -*-
# author: liuxu

from Tkinter import Label
from Tkinter import LabelFrame
import Tkinter
import config


# ===================================================================


class TextLabelFrame(LabelFrame):

    def __init__(self, win, title, content):
        LabelFrame.__init__(self, win)
        self["text"] = title
        self.content_view = Label(self,
                justify = Tkinter.LEFT,
                anchor = "w",
                text = content
            )
        self.content_view.pack(side = "top", fill = Tkinter.X, padx = 15, pady = 2)
        self.pack(side = "top", fill = Tkinter.X, padx = 10, pady = 12)


# ===================================================================


class Introduction():
    
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.title(u"说明")
        TextLabelFrame(self.root, "Read Me", config.getReadMeContent())
        center(self.root)
        self.root.mainloop()


# ===================================================================


class About():
    
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.title("About")
        
        TextLabelFrame(self.root, "About Author", '''
author\t:   liuxu-0703@163.com
github\t:   https://github.com/liuxu0703/douban_movie_rating
blog\t:   http://blog.csdn.net/liuxu0703/
        ''')
        TextLabelFrame(self.root, "Powered By", '''
douban\t:   https://developers.douban.com/wiki/
Python\t:   https://www.python.org/
Tkinter\t:   https://wiki.python.org/moin/TkInter
        ''')
        
        center(self.root)
        self.root.mainloop()


# ===================================================================

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


if __name__ == '__main__':
    About()
    
    
    