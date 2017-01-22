# -*- coding: utf-8 -*-
# author: liuxu

import sys
import log
import MainFrame
import argparser

if __name__ == '__main__':
    try :
        if (hasattr(sys, "argv") and len(sys.argv) > 1):
            path = sys.argv[1]
            log.i("douban movie rating, start up ! argv[1]: " + path)
            path_parser = argparser.PathParser(path)
            MainFrame.Main(path_parser.getCacheKey(), path_parser.getSearchString())
        else:
            log.i("douban movie rating, start up ! no args")
            MainFrame.Main("", "")
    except:
        log.logger.exception("Shit Happens")

        

