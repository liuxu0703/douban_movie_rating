# -*- coding: utf-8 -*-
# author: liuxu

import os
import sys
import platform
import codecs
import urllib
import string
import log
import config


# ===================================================================


def getUtf8(string):
    '''return a utf-8 encoded str'''
    if (isinstance(string, str)):
        return urllib.quote(string)
    elif (isinstance(string, unicode)):
        return urllib.quote(string.encode("utf-8"))

def getString(string):
    '''return a str'''
    if (isinstance(string, str)):
        return string
    elif (isinstance(string, unicode)):
        try:
            return string.encode("utf-8")
        except:
            return string.encode("gbk")


# ===================================================================


class PathParser():

    def __init__(self, path):
        try:
            path_utf8 = path.decode('gbk').encode('utf-8', 'ignore')
        except:
            path_utf8 = path
        self.cache_key = self.getRelativePath(path_utf8).replace(os.sep, "%/%")
        path_name = getString(os.path.basename(path_utf8))

        if (path_name):
            self.loadFilterWords()
            self.search_string = self.filter(path_name)
            log.d("filter word result: " + self.search_string)

    def getCacheKey(self):
        return self.cache_key
    
    def getSearchString(self):
        return self.search_string

    @staticmethod
    def getRelativePath(origin_path):
        system = platform.system()
        if (system == "Windows"):
            return PathParser.getWindowsRelativePath(origin_path)
        elif (system == "Darwin"):
            return PathParser.getLinuxRelativePath(origin_path)
        elif (system == "Linux"):
            return PathParser.getLinuxRelativePath(origin_path)
        else:
            return None

    @staticmethod
    def getWindowsRelativePath(origin_path):
        return os.path.realpath(origin_path)[3:]
    
    @staticmethod
    def getLinuxRelativePath(origin_path):
        cmd = "d=$(df . | sed -n '2p' | awk '{print $NF}'); echo " + origin_path + " | awk -F \"$d\" '{print $2}'"
        return commands.getoutput(cmd)

    def loadFilterWords(self):
        self.filter_list = []
        try:
            filter_file = config.getWordFilterConfPath()
            for line in codecs.open(filter_file, "r", "utf-8"):
                word = getString(line)
                if (word):
                    word = word.strip('\n')
                    self.filter_list.append(word)
        except Exception, e:
            log.logger.exception("load filter words fail")

    def filter(self, search_string):
        if (not search_string):
            return ""
        if (len(self.filter_list) > 0):
            for wf in self.filter_list:
                result = search_string.replace(wf, "")
                log.d("filter word " + search_string + " against " + wf + " : " + result)
                search_string = result
            return search_string
        else:
            return search_string


# ===================================================================


if __name__ == '__main__':
    print "default encoding", sys.getdefaultencoding()
    path = u"/home/liuxu/video/movie/[A]碟中谍5.720p.国英双语"
    path_parser = PathParser(path)
    print "111", path_parser.getSearchString()
    


