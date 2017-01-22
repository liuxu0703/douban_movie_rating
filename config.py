# -*- coding: utf-8 -*-
# author: liuxu

import os
import sys
import string
import codecs
import ConfigParser

# ===================================================================

class Config():        
    config = None

# ===================================================================

def debug():
    debug = getConfig().get("app", "debug")
    return debug == "True" or debug == "true" or debug == 1

def getLogPath():
    return getAndMakePath("log_file")

def getImageCachePath():
    return getAndMakePath("cache_image_path")

def getJsonCachePath():
    return getAndMakePath("cache_json_path")

def getDeployCachePath():
    return getAndMakePath("cache_deploy_file")

def getDeployBatPath():
    return getAndMakePath("cache_deploy_bat_file")

def getDeployBashPath():
    return getAndMakePath("cache_deploy_bash_file")

def getBatCachePath():
    return getAndMakePath("cache_bat_file")

def getWordFilterConfPath():
    return getAndMakePath("word_filter_file")

def getReadMeConfPath():
    return getAndMakePath("read_me_file")

def getReadMeContent():
    return readString(getReadMeConfPath())

# ===================================================================

def readString(file_path):
    if (os.path.exists(file_path)):
        try:
            f = open(file_path)
            ret = f.read()
        finally:
            if (f):
                f.close()
        return ret
    else:
        return ""

def getAndMakePath(attr_name):
    p = getConfig().get("path", attr_name)
    if (not p):
        return False
    p = string.replace(p, "%/%", os.sep)
    p = os.path.dirname(sys.argv[0]) + os.sep + p.encode("utf-8")
    if (attr_name.endswith("_path")):
        d = p
    else:
        d = os.path.dirname(p)
    if (not os.path.exists(d)):
        os.makedirs(d);
    return p

def getWindowSize(attr_name):
    return int(getConfig().get("window", attr_name))

def getConfig():
    return Config.config

def init(ini_path):
    print "try parse " + ini_path
    if (not os.path.exists(ini_path)):
        print "ini file not exists: " + ini_path
        raise IOError
    try:
        Config.config = ConfigParser.ConfigParser()
        Config.config.readfp(codecs.open(ini_path, "r", "utf-8"))
    except:
        print "read config file fail"


# ===================================================================


ini_path = os.path.dirname(sys.argv[0]) + os.sep + "config" + os.sep + "config.ini"
init(ini_path)
print "start up, argv[0]: " + sys.argv[0]


if __name__ == '__main__':       
    print getLogPath()
    print getReadMeContent()
    
    
    
