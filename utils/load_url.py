# -*- coding: utf-8 -*-
# Load_url

import sys
import urllib
from urllib2 import Request, urlopen, URLError, HTTPError

DEBUG = False
#BOT_SIGNATURE = "Tax26.com bot"
BOT_SIGNATURE = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13"
def load_url(url, post_data=None, return_charset=False):
    user_agent = BOT_SIGNATURE
    headers = { 'User-Agent' : user_agent }
    url = url.replace('`', urllib.quote('`'))
    req = Request(url, post_data, headers) # POST data
    try:
        urlh = urlopen(req, data=post_data, timeout=180)
        charset = urlh.headers.getparam('charset')
    except HTTPError, e:
        if DEBUG:
            print url, ' failed, code : ', e
        return False, False, "Can't download page:" + str(e)
    except URLError, e:
        if DEBUG:
            print 'We failed to reach a server - ' + url
            print 'Reason: ', e.reason
        return False, False, "Can't download page:" + str(e)
    info = urlh.info()
    #if "text/html" in info['content-type']:
    #    pass
    #else:
        #if "text/plain" in info['content-type']:
        #    pass
        #else:
        #    if DEBUG:
        #        print "Content-Type: ", info['content-type']
        #    return False, False, "Strange content type: " +info['content-type']

    not_readed = True
    i = 0
    real_url = url
    while not_readed:
        try:
            data = urlh.read()
        except:
            i = i + 1
            if i>5:
                not_readed = False
        else:
            not_readed = False
            real_url = urlh.geturl()
            urlh.close()

    if return_charset:
        return data, real_url, urlh.info(), charset
    else:
        return data, real_url, urlh.info()
