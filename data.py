# -*- coding: utf-8 -*-
# author: liuxu

import os
import commands
import platform
import shutil
import httplib
import urllib
import hashlib
import string
import json
import config
import log


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


# ===================================================================

class GlobalData():
    run_path = None
    
# ===================================================================

class SearchQuest():

    def requestSearch(self, keyword):
        log.d("search keyword: " + getDecodedString(keyword))
        self.origin_search = keyword
        self.search = getUtf8String(keyword)
        count = config.getSearchCount()
        request_string = "/v2/movie/search?count=" + str(count) + "&q=" + self.search
        log.d("req: http://api.douban.com" + request_string)
        conn = httplib.HTTPConnection("api.douban.com")
        conn.request("GET", request_string)
        res = conn.getresponse()
        ret = res.read()
        if (res.status == 200):
            log.d("res: " + str(res.status) + ", " + str(res.reason) + ", " + ret)
            return ret
        else:
            log.e("res: " + str(res.status) + ", " + str(res.reason) + ", " + ret)
    
    def getMovieList(self, search_result_json):
        movie_list = []  
        if (search_result_json):
            json_dic = json.loads(search_result_json)
            for data in json_dic["subjects"]:
                movie_list.append(MovieSummary(data))
            if (movie_list):
                movie_list.sort(cmp = MovieSummary.compare)
        return movie_list
    
    def getMovieListByKeyword(self, keyword):
        log.d("getMovieListByKeyword: " + keyword)
        if (not keyword):
            log.w("search request with empty keyword")
            return []
        else:
            json_str = self.requestSearch(keyword)
            return self.getMovieList(json_str)


# ===================================================================


class MovieCache():
    
    def __init__(self, movie_dir):
        self.cache_path = movie_dir + os.sep + "info.json"
        self.movie = False
        
    def get(self):
        if (not self.movie and os.path.exists(self.cache_path)):
            try:
                cache_file = open(self.cache_path)
                json_str = cache_file.read()
            finally:
                if (cache_file):
                    cache_file.close()
            if (json_str):
                log.i("json from file: " + json_str)
                data = json.loads(json_str)
                if (data):
                    self.movie = MovieSummary(data, True)
        return self.movie

    def getList(self):
        ret = []
        movie = self.get()
        if (movie):
            ret.append(movie)
        return ret
        
    def save(self, movie):
        json_string = json.dumps(movie.data)
        cache_file = open(self.cache_path, 'w')
        print >> cache_file, json_string

    def update(self, movie):
        if (movie.isSelected()):
            self.save(movie)
        else:
            os.remove(self.cache_path)

    def getCachePath(self):
        return self.cache_path
    

# ===================================================================


class DeployCache():
    
    @staticmethod
    def getPathList():
        path_list = []
        cache_path = config.getDeployCachePath()
        if (cache_path and os.path.exists(cache_path)):
            try:
                for line in open(cache_path):
                    deploy_path = getDecodedString(line).strip('\n')
                    deploy_path = string.replace(deploy_path, "%/%", os.sep)
                    if (deploy_path and os.path.exists(deploy_path)):
                        path_list.append(deploy_path)
            except Exception, e:
                log.logger.error(e, exc = True)
        return path_list

    @staticmethod
    def savePathList(path_list):
        if (path_list and len(path_list) > 0):
            output_str = ""
            for p in path_list:
                path_str = string.replace(p, os.sep, "%/%")
                output_str = output_str + path_str + "\n"
            output_str = getDecodedString(output_str)
            cache_path = config.getDeployCachePath()
            cache_file = open(cache_path, 'w')
            print >> cache_file, output_str
    
    @staticmethod
    def createBatFile():
        relative_path = DeployCache.getWindowsRelativePath()
        output_str = "set relative_path=" + relative_path + "\n"
        output_str = output_str + '''
set disk=%~d0
set program_path=%disk%\%relative_path%\main.exe
start "" "%program_path%" "%cd%"
        '''
        cache_path = config.getDeployBatPath()
        cache_file = open(cache_path, 'w')
        print >> cache_file, output_str
        return cache_path
    
    @staticmethod
    def createBashFile():
        relative_path = DeployCache.getLinuxRelativePath()
        output_str = "#!/bin/bash \n relative_path=" + relative_path + "\n"
        output_str = output_str + '''
mount_point=$(df . | sed -n '2p' | awk '{print $NF}')
program_path=$mount_point/$relative_path/main.py
current_dir=$(pwd)
python "$program_path" "$current_dir"
        '''
        cache_path = config.getDeployBashPath()
        cache_file = open(cache_path, 'w')
        print >> cache_file, output_str
        return cache_path

    @staticmethod
    def getRelativePath():
        system = platform.system()
        if (system == "Windows"):
            return DeployCache.getWindowsRelativePath()
        elif (system == "Darwin"):
            return DeployCache.getLinuxRelativePath()
        elif (system == "Linux"):
            return DeployCache.getLinuxRelativePath()
        else:
            return None

    @staticmethod
    def getWindowsRelativePath():
        return os.path.realpath(os.curdir)[3:]
    
    @staticmethod
    def getLinuxRelativePath():
        cmd = "d=$(df . | sed -n '2p' | awk '{print $NF}'); pwd | awk -F \"$d\" '{print $2}'"
        return commands.getoutput(cmd)
    

# ===================================================================


class ImageCache():

    @staticmethod
    def getImagePath(image_url, selected = False):
        file_name = hashlib.md5(image_url).hexdigest() + ".jpg"
        if (GlobalData.run_path):
            image_sel_path = GlobalData.run_path + os.sep + file_name
            if (os.path.exists(image_sel_path)):
                return image_sel_path
        image_tmp_path = config.getImageCachePath() + os.sep + file_name
        if (os.path.exists(image_tmp_path)):
            if (selected):
                ImageCache.update(image_url, selected)
            return image_tmp_path

        if (selected):
            image_path = image_sel_path
        else:
            image_path = image_tmp_path
        image_path = ImageCache.downloadImage(image_url, image_path)
        if (image_path):
            log.d("getImagePath from net: " + image_url)
            return image_path
        else:
            log.d("getImagePath fail: " + image_url)
        
    @staticmethod
    def update(image_url, selected):
        if (GlobalData.run_path == None):
            return
        file_name = hashlib.md5(image_url).hexdigest() + ".jpg"
        if (selected):
            image_tmp_path = config.getImageCachePath() + os.sep + file_name
            if (os.path.exists(image_tmp_path)):
                image_path = GlobalData.run_path + os.sep + file_name
                shutil.copy(image_tmp_path, image_path)
        else:
            image_path = GlobalData.run_path + os.sep + file_name
            if (os.path.exists(image_path)):
                os.remove(image_path)
        
    @staticmethod
    def downloadImage(image_url, image_path):
        byte = urllib.urlopen(image_url).read()
        write_file = open(image_path, 'wb')
        write_file.write(byte)
        write_file.close()
        return image_path


# ===================================================================


class MovieSummary():
    
    def __init__(self, data, selected = False):
        self.data = data
        self.selected = selected
    
    def getMovieId(self):
        return self.data["id"]
    
    def getTitle(self):
        return self.data["title"]
    
    def getOriginalTitle(self):
        return u"原版片名: " + self.data["original_title"]
    
    def getImage(self):
        if (self.data["images"]):
            if (self.selected):
                return self.data["images"]["large"]
            elif (config.getImageQuality() in self.data["images"]):
                return self.data["images"][config.getImageQuality()]
        return config.getImageDefault()

    def getRating(self):
        return u"豆瓣评分: " + str(self.data["rating"]["average"]) +\
            u"  (" + str(self.data["collect_count"]) + u"人评价)"

    def getCast(self):
        ret = u"主要演员:"
        for c in self.data["casts"]:
            ret = ret + " " + c["name"]
        return ret
    
    def getDirector(self):
        ret = u"影片导演:"
        if self.data["directors"]:
            for d in self.data["directors"]:
                ret = ret + " " + d["name"]
        return ret

    def getYear(self):
        return u"上映年份: " + str(self.data["year"])

    def getGenres(self):
        ret = u"影片类型:"
        for g in self.data["genres"]:
            ret = ret + " " + g
        return ret
    
    def getWebUrl(self):
        return self.data["alt"]
    
    def getCollectCount(self):
        return self.data["collect_count"]
    
    def setSelected(self, selected):
        self.selected = selected
        
    def isSelected(self):
        return self.selected
    
    @staticmethod
    def compare(m1, m2):
        return m2.getCollectCount() - m1.getCollectCount()


# ===================================================================


if __name__ == '__main__':
    #print DeployCache.createBashFile()
    #print DeployCache.createBatFile()
    print DeployCache.getWindowsRelativePath()
