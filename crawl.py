#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Crawl BOT
# Get links from urlserver, download them and store into Stoerserver

try:
    import re2 as re
except:
    import re
import sys
import urllib
import robotparser
import traceback
from urlparse import urlparse
#from urllib2 import Request, urlopen, URLError, HTTPError

from utils.load_url import load_url
from uslaw.local_bot_settings import BASE_URL, BASE_SAVE_URL, SECRET_KEY, DEBUG


def main():
    """
    Fetching urls, parse robots.txt

    return to store server:
    url 
    plugin_id = 0
    page 
    page_type = 0
    status = 0 or 1 if error
    error_text = "" or error text if error occurred
    """
    #if test:
    #    urls=test
    #else:
    urls, r, i = load_url(BASE_URL)
    if DEBUG:
        print "Urls:", urls, r, i
    if urls == "No urls" or urls == False:
        sys.exit(0)  # No urls for downloading

    u = urls.split("|||")
    old_domain = ""
    for link_ in u:
        if link_.strip() == "":
            continue
        ll = link_.strip().split("%%%")
        link = ll[0]
        plugin_id = ll[1]
        plugin_level = ll[2]
        decode_charset = ll[3]
        category_id = ll[4]
        error, status = "", 0
        if len(link.strip()) > 0:
            uuu = urlparse(link)
            domain = uuu[0]+'://'+uuu[1]
            if DEBUG:
                print "Domain: ", domain
            can_fetch = True
            if domain == old_domain:
                if rp.can_fetch('*', link.strip()):
                    can_fetch = True
            else:
                old_domain = domain
                #robots, r, i = load_url(domain+'/robots.txt')
                can_fetch = False
                rp = robotparser.RobotFileParser()
                rp.set_url(domain+'/robots.txt')
                try:
                    rp.read()                    
                except:
                    if DEBUG:
                        print "Error loading "+domain+'/robots.txt'
                        print "Possible it is empty. continue..."
                        
                if rp.can_fetch('*', link.strip()):
                    if DEBUG:
                        print "Can fetch: ", link.strip(), ":", domain
                    can_fetch = True
            can_fetch = True    
            if can_fetch:
                page, real_url, info, charset = load_url(link.strip(), 
                                                         return_charset=True)
                
                if page == False:
                    error = info
                    status = "2"
                if DEBUG:
                    print link, info, real_url
            else:
                status = "2"
                error = "This page disallowed in robots.txt"
                if DEBUG:
                    print ">>> Cant fetch, Disallow in robots.txt: ", link
                page = False

            if page:
                if decode_charset != '':
                    if DEBUG:
                        print "Decoding from %s" % decode_charset
                    try:
                        page = page.decode(decode_charset).encode("utf-8")
                        #print "Encoding page from %s" % decode_charset
                    except UnicodeDecodeError:
                        print traceback.format_exc()
                        pass

                else:
                    if charset is not None and charset != '':
                        encodings = [charset, ]
                    else:
                        encoding_re = re.compile(r'<meta http-equiv="Content-Type" content="text/html; charset=(.*?)"')
                        encodings = encoding_re.findall(page)
                    if DEBUG:
                        print "encodings - ", encodings
                    if len(encodings) > 0:
                        try:
                            page = page.decode(encodings[0]).encode("utf-8")
                            #print "Encoding page from %s" % encodings[0]
                        except UnicodeDecodeError:
                            print traceback.format_exc()#
                            #pass

            values = {"url":link, "page":page, "plugin_id":plugin_id, 
                      "plugin_level":plugin_level, "page_type":0,
                      "category_id":category_id, "status":status, 
                      "error":error, "secret_key":SECRET_KEY}
            data = urllib.urlencode(values)
            res, url, i = load_url(BASE_SAVE_URL, data)                
            if res == False: # try once more time!
                res, url, i = load_url(BASE_SAVE_URL, data)
            if DEBUG:
                print res

    return None


if __name__ == "__main__":
    main()
