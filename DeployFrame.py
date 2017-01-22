# -*- coding: utf-8 -*-
# author: liuxu

import os
import shutil
import urllib
import threading
import platform
import Tkinter
import tkFileDialog
import config
import data
import log
from Tkinter import LabelFrame
from Tkinter import Frame
from Tkinter import Label
from Tkinter import Button
import AboutFrame


# ===================================================================


class TextLabelFrame(LabelFrame):

    def __init__(self, win, title):
        LabelFrame.__init__(self, win)
        self["text"] = title
        self.content_view = Label(self,
                justify = Tkinter.LEFT,
                anchor = "nw",
            )
        self.content_view.pack(side = "top", padx = 15, pady = 15)

    def setSize(self, width, height):
        self.content_view["width"] = width
        self.content_view["height"] = height
        return self

    def setContent(self, content):
        self.content_view["text"] = content
        

# ===================================================================


class DeployWorker():
    
    def __init__(self, target_path):
        self.target_path = target_path
        system = platform.system()
        if (system == "Windows"):
            self.deploy_script = data.DeployCache.createBatFile()
        elif (system == "Darwin"):
            self.deploy_script = data.DeployCache.createBashFile()
        elif (system == "Linux"):
            self.deploy_script = data.DeployCache.createBashFile()
        else:
            raise
    
    def deploy(self):
        log.i("deploy script: " + self.deploy_script + ", to path:" + self.target_path)
        for dirpath, dirnames, filenames in os.walk(self.target_path):
            log.d("deploy to " + dirpath)
            shutil.copy(self.deploy_script, dirpath)


# ===================================================================


class Main():
    
    def __init__(self):
        self.path_list = data.DeployCache.getPathList()
        self.root = Tkinter.Tk()
        self.root.title(u"部署程序到电影目录")
        self.path_view = TextLabelFrame(self.root, u"部署位置(可多选)").setSize(
                width = config.getWindowSize("deploy_path_width"),
                height = config.getWindowSize("deploy_path_height"))
        self.path_view.pack(side = Tkinter.LEFT, padx = 10, pady = 10)
        self.displayPathList()
        self.displayButton()
        center(self.root)
        self.root.mainloop()
        
    def displayButton(self):
        button_frame = Frame(self.root)
        Button(button_frame, text = u"选择目录", command = self.showSelectDirectory, fg = "blue")\
                .pack(side = Tkinter.TOP, pady = 8)
        Button(button_frame, text = u"重新选择", command = self.clearPathList, fg = "blue")\
                .pack(side = Tkinter.TOP, pady = 8)
        Button(button_frame, text = u"帮助说明", command = self.showHelp, fg = "blue")\
                .pack(side = Tkinter.TOP, pady = 8)
        Button(button_frame, text = u"开始部署", command = self.doDeploy, fg = "blue")\
                .pack(side = Tkinter.BOTTOM)
        button_frame.pack(side = Tkinter.LEFT, fill = Tkinter.Y, padx = 8, pady = 10)
        
    def displayPathList(self):
        if (self.path_list and len(self.path_list) > 0):
            display_str = ""
            for p in self.path_list:
                display_str = display_str + p + "\n"
            self.path_view.setContent(display_str)
        else:
            self.path_view.setContent(u"尚未设置部署目录")
    
    def showSelectDirectory(self):
        options = {}
        options['initialdir'] = os.pardir
        options['parent'] = self.root
        options['title'] = u"选择部署目录"
        deploy_path = tkFileDialog.askdirectory(**options)
        if (deploy_path and os.path.exists(deploy_path)):
            self.path_list.append(deploy_path)
            self.displayPathList()

    def showDeployDoneDialog(self):
        message = "\n"
        for p in self.path_list:
            message = message + p + "   Done\n"
        dialog = Tkinter.Tk()
        dialog.title(u"部署完成")
        message_view = Label(dialog,
                justify = Tkinter.LEFT,
                anchor = "nw",
                width = config.getWindowSize("deploy_path_width"),
                text = message,
            )
        message_view.pack(side = Tkinter.LEFT, fill = Tkinter.X, padx = 20, pady = 10)
        center(dialog)
        dialog.mainloop()

    def clearPathList(self):
        self.path_list = []
        self.displayPathList()

    def showHelp(self):
        AboutFrame.Introduction()

    def doDeploy(self):
        if (not self.path_list or len(self.path_list) == 0):
            return
        data.DeployCache.savePathList(self.path_list)
        for p in self.path_list:
            DeployWorker(p).deploy()
        self.showDeployDoneDialog()



# ===================================================================


def getUtf8String(string):
    '''return a utf-8 encoded str'''
    if (isinstance(string, str)):
        return urllib.quote(string)
    elif (isinstance(string, unicode)):
        return urllib.quote(string.encode("utf-8"))

def getDecodedString(string):
    '''return a str'''
    if (isinstance(string, str)):
        return string
    elif (isinstance(string, unicode)):
        return string.encode("utf-8")

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

# ===================================================================

if __name__ == '__main__':
    Main()


'''
set relative_path=Python27\python.exe
set disk=%~d0
set program_path=%disk%\%relative_path%
start "" %program_path% %cd%
'''

