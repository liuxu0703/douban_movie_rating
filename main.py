# -*- coding: utf-8 -*-
# author: liuxu

import sys
import log
import data
import MainFrame
import argparser

if __name__ == '__main__':
    try :
        if (hasattr(sys, "argv") and len(sys.argv) > 1):
            path = sys.argv[1]
            log.i("douban movie rating, start up ! argv[1]: " + path)
            data.GlobalData.run_path = path
            path_parser = argparser.PathParser(path)
            movie_cache = data.MovieCache(path)
            MainFrame.Main(path_parser.getSearchString(), movie_cache)
        else:
            log.i("douban movie rating, start up ! no args")
            MainFrame.Main("")
    except:
        log.logger.exception("Shit Happens")

        

