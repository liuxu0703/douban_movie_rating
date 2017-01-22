# -*- coding: utf-8 -*-
# author: liuxu

import os
import threading
import hashlib
import urllib
import webbrowser
import Tkinter
import tkFont
from Tkinter import Label
from Tkinter import Entry
from Tkinter import Button
from Tkinter import Frame
from Tkinter import LabelFrame
from Tkinter import Menu
from PIL import Image, ImageTk

import config
import data
import log
import AboutFrame
import DeployFrame


# ===================================================================
# display url image

class ImageView(Label):

    def __init__(self, master, url, w, h):
        path = self.getImagePath(url)
        image_tk = ImageTk.PhotoImage(Image.open(path).resize((w, h), Image.ANTIALIAS))
        Label.__init__(self, master, image = image_tk)
        self.image = image_tk # keep a reference!

    def size(self, width, height):
        self.image_width = width
        self.image_height = height
        return self

    def display(self, image_url):
        self.image_url = image_url
        self.image_path = self.getImagePath(image_url)
        image_tk = ImageTk.PhotoImage(
                Image.open(self.image_path).resize((self.image_width, self.image_height),
                Image.ANTIALIAS))
        self.image = image_tk # keep a reference!
        return self
        
    # ========================================================

    def getImagePath(self, image_url):
        image_path = self.getImageCachePath(image_url);
        if (os.path.exists(image_path)):
            log.d("getImagePath from cache: " + image_url)
            return image_path
        image_path = self.downloadImage(image_url, image_path)
        if (image_path):
            log.d("getImagePath from net: " + image_url)
            return image_path
        else:
            log.d("getImagePath fail: " + image_url)
        
    def getImageCachePath(self, image_url):
        file_name = hashlib.md5(image_url).hexdigest() + ".jpg"
        return config.getImageCachePath() + os.sep + file_name
        
    def downloadImage(self, image_url, image_path):
        byte = urllib.urlopen(image_url).read()
        write_file = open(image_path, 'wb')
        write_file.write(byte)
        write_file.close()
        return image_path


# ===================================================================
# display text information

class InfoTextView(Frame):
        
    def __init__(self, win):
        Frame.__init__(self, win)
        self["width"] = config.getWindowSize("movie_info_width")
        self.selected = False
        
        self.title = Tkinter.StringVar()
        self.title_view = Label(self,
                fg = "blue",
                font = tkFont.Font(size=16, weight='bold'),
                justify = Tkinter.LEFT,
                anchor = "w",
                textvariable = self.title
            )
        self.title_view.pack(side = "top", fill = Tkinter.X)

        self.content = Tkinter.StringVar()
        self.content_view = Label(self,
                font = tkFont.Font(size=12),
                justify = Tkinter.LEFT,
                anchor = "w",
                textvariable = self.content
            )
        self.content_view.pack(side = "top", fill = Tkinter.X)
            
        self.browser_button = Label(self,
                fg = "blue",
                font = tkFont.Font(size=12),
                justify = Tkinter.LEFT,
                anchor = "w",
                text = u"跳转到豆瓣详情页面"
            )
        self.browser_button.bind("<Button-1>", self.toWebBrowser)
        self.browser_button.pack(side = "top", fill = Tkinter.X)
        
        self.selected_label = Label(self,
                fg = "green",
                font = tkFont.Font(size=12),
                justify = Tkinter.LEFT,
                anchor = "w",
                text = u"[选为默认]"
            )
        self.selected_label.pack(side = "top", fill = Tkinter.X)

    def setTitle(self, title):
        self.title.set(title)
        return self
        
    def setContent(self, content):
        self.content.set(content)
        return self
    
    def addContent(self, line):
        if (line):
            s = self.content.get()
            if (s):
                s = s + '\n' + line
            else:
                s = line
            self.content.set(s)
        return self
    
    def setWebUrl(self, url):
        self.web_url = url
        return self
    
    def toWebBrowser(self, event):
        if (self.web_url):
            log.d("open web browser for: " + self.web_url)
            webbrowser.open_new_tab(self.web_url)


# ===================================================================
# display single movie information

class InfoFrame(LabelFrame):
        
    def __init__(self, win, movie):
        LabelFrame.__init__(self, win)
        self["bd"] = 2
        self.movie = movie
        self.image_view = ImageView(self,
            self.movie.getImage(),
            config.getWindowSize("movie_poster_width"),
            config.getWindowSize("movie_poster_height"))
        self.image_view.pack(side = Tkinter.LEFT, ipadx = 6, ipady = 6)
        self.info_view = InfoTextView(self)\
                .setTitle(self.movie.getTitle())\
                .addContent(self.movie.getOriginalTitle())\
                .addContent(self.movie.getRating())\
                .addContent(self.movie.getGenres())\
                .addContent(self.movie.getYear())\
                .setWebUrl(self.movie.getWebUrl())
        self.info_view.pack(side = Tkinter.LEFT, ipadx = 6)
        
        self.info_view.selected_label.bind("<Button-1>", self.doSelectClick)
        self.refreshSelected()

    def isSelected(self):
        return self.movie.isSelected()

    def setSelected(self, selected):
        self.movie.setSelected(selected)

    def setSelectCommand(self, command):
        self.select_command = command
        return self
    
    def refreshSelected(self):
        if (self.isSelected()):
            self.info_view.selected_label["text"] = u"[已选为默认. 不是这个电影? 重新选择.]"
        else:
            self.info_view.selected_label["text"] = u"[选为默认]"

    def doSelectClick(self, event):
        self.movie.setSelected(not self.movie.isSelected())
        if (hasattr(self, "select_command")):
            self.select_command(self, self.movie)

# ===================================================================
# search box and search button

class SearchFrame(Frame):
    
    def __init__(self, win, search = ""):
        Frame.__init__(self, win)
        self["bg"] = "white"
        self.entry_view = Entry(self, width = config.getWindowSize("search_box_width"))
        self.entry_view.insert(10, search)
        self.entry_view.pack(side = Tkinter.LEFT, ipadx = 10, ipady = 2)
        
        self.button = Button(self, text = u"搜索")
        self.button.pack(side = Tkinter.LEFT, padx = 10)
        
    def setSearchCommand(self, search_command):
        self.button["command"] = search_command
        return self
    
    def getSearchString(self):
        return self.entry_view.get()


# ===================================================================
# scroll container frame

class ScrollFrame(Frame):
        
    def __init__(self, root, movie_list, message, search_command, pick_command):
        Frame.__init__(self, root)
        self.canvas = Tkinter.Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = Tkinter.Frame(self.canvas, background="#ffffff")
        self.vsb = Tkinter.Scrollbar(root, orient="vertical", width = 16, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window = self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.populate(movie_list, search_command, pick_command, message)

    def populate(self, movie_list, search_command, pick_command, load_message = ""):
        # add search view on top
        self.search_frame = SearchFrame(self.frame)\
            .setSearchCommand(search_command);
        self.search_frame.pack(side = Tkinter.TOP, fill = Tkinter.X, padx = 10, pady = 5)
        
        # display movie list
        if (movie_list and len(movie_list) != 0):
            self.info_frame_list = []
            for summary in movie_list:
                info_frame = InfoFrame(self.frame, summary).setSelectCommand(pick_command)
                info_frame.pack(side = Tkinter.TOP, fill = Tkinter.X, padx = 10, pady = 5)
                self.info_frame_list.append(info_frame)
        else:
            self.load_info_view = Label(self.frame,
                    fg = "blue",
                    font = tkFont.Font(size=12, weight='bold'),
                    height = 10,
                )
            self.load_info_view["text"] = load_message
            self.load_info_view.pack(side = Tkinter.TOP, fill = Tkinter.X, padx = 10, pady = 5)

    def clearAllView(self):
        if (hasattr(self, "instruction_label")):
            self.instruction_label.pack_forget()
        if (hasattr(self, "search_frame")):
            self.search_frame.pack_forget()
        if (hasattr(self, "info_frame_list")):
            for info_frame in self.info_frame_list:
                info_frame.pack_forget()
        if (hasattr(self, "load_info_view")):
            self.load_info_view.pack_forget()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def getSearchString(self):
        return self.search_frame.getSearchString()

    def setLoadingInfo(self, text):
        self.load_info_view["text"] = text


# ===================================================================
# menu

class MainMenu(Menu):
    
    def __init__(self, root):
        Menu.__init__(self, root)
        menu_about = Menu(self, tearoff = 0)
        menu_about.add_command(label = u"说明", command = self.showIntro)
        menu_about.add_command(label = u"关于", command = self.showAbout)
        self.add_command(label = u"部署", command = self.showDeploy)
        self.add_cascade(label = u"帮助", menu = menu_about)
        
    def showAbout(self):
        AboutFrame.About()
    
    def showIntro(self):
        AboutFrame.Introduction()
    
    def showDeploy(self):
        DeployFrame.Main()


# ===================================================================


class Main():
    
    def __init__(self, cache_key, search_string):
        log.d("MainFrame, start up. key=" + cache_key + ", search=" + search_string)
        self.movie_cache = data.MovieCache(cache_key)
        self.movie_list = self.movie_cache.getList()
        self.cache_key = cache_key
        self.origin_search_string = search_string
        self.search_string = search_string
        self.provider = data.SearchQuest()
        self.root = Tkinter.Tk()
        self.root.title(u"电影信息摘要")
        self.root.config(menu = MainMenu(self.root))
        #self.refreshView(self.movie_list)
        if (len(self.movie_list) == 0 and self.search_string):
            #threading.Thread(target = self.searchFromThread).start()
            self.movie_list = self.provider.getMovieListByKeyword(self.origin_search_string)
        self.refreshView(self.movie_list)
        self.center_window()
        self.root.mainloop()

    def refreshView(self, movie_list):
        if (not self.cache_key and not self.search_string):
            message = u'''
首次加载?
点击菜单中的 部署, 将程序部署到各电影目录.
点击菜单中的 帮助->说明 查看程序说明.
'''
        elif (not movie_list or len(movie_list) == 0):
            message = u'''
未搜索到相关电影条目. 搜索关键词是否正确?
请查看电影目录命名是否正确(根据电影名称命名).
点击菜单中的 帮助->说明 查看程序说明.
'''
        else:
            message = ""
            
        if (hasattr(self, "main_frame")):
            self.main_frame.clearAllView()
            self.main_frame.populate(movie_list, self.doSearch, self.doPick, message)
        else:
            self.main_frame = ScrollFrame(self.root, movie_list, message, self.doSearch, self.doPick)
            self.main_frame.pack(side = "top", fill = Tkinter.Y)
            
    def doSearch(self):
        self.search_string = self.main_frame.getSearchString()
        if (self.search_string):
            self.movie_list = self.provider.getMovieListByKeyword(self.search_string)
            log.d("search result, movie count: " + str(len(self.movie_list)))
            self.refreshView(self.movie_list)
        
    def doPick(self, frame, movie):
        for info_frame in self.main_frame.info_frame_list:
            if (info_frame.movie.getMovieId() != movie.getMovieId()):
                info_frame.setSelected(False)
            info_frame.refreshSelected()
        self.movie_cache.update(movie)
        if (not movie.isSelected() and len(self.movie_list) <= 1):
            self.movie_list = self.provider.getMovieListByKeyword(self.origin_search_string)
            self.refreshView(self.movie_list)

    def center_window(self):
        w = config.getWindowSize("window_width")
        h = config.getWindowSize("window_height")
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        geometry = '%dx%d+%d+%d' % (w, h, x, y)
        log.d("window size: " + geometry)
        self.root.geometry(geometry)
        
    def searchFromThread(self):
        self.movie_list = self.provider.getMovieListByKeyword(self.origin_search_string)
        self.refreshView(self.movie_list)


# ===================================================================


if __name__ == '__main__':
    search_string = u"功夫熊猫"
    cache_key = search_string

    #Main(cache_key, search_string)
    Main("", "")
        
