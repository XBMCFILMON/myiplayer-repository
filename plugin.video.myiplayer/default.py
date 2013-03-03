import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,os
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon


net = Net()
local = xbmcaddon.Addon(id='plugin.video.myiplayer')
addon = Addon('plugin.video.myiplayer', sys.argv)
BASE_URL = 'http://myiplayer.eu/'
datapath = addon.get_profile()
cookie_path = os.path.join(datapath, 'cookies')                 
cookie_jar = os.path.join(cookie_path, "cookiejar.lwp")
if os.path.exists(cookie_path) == False:                        
    os.makedirs(cookie_path)

#DEBUG INFORMATION BELOW
print 'DATAPATH: '+datapath
print 'COOKIE JAR: '+cookie_jar

def make_http_get_request(url, track_cookie=False):
    if (track_cookie):
        net.set_cookies(cookie_jar)
    try:
        html = net.http_GET(url).content
        if (track_cookie):
            net.save_cookies(cookie_jar)
        return html
    except urllib2.URLError, e:
        xbmcgui.Dialog().ok(addon.get_name(), 'Unable to connect to website', '', '') 
        return ""

# Taken from desitvforum xbmc plugin.
def get_domain_name(url):
    tmp = re.compile('//(.+?)/').findall(url)
    domain = 'Unknown'
    if len(tmp) > 0:
        domain = tmp[0].replace('www.', '')
    return domain


#xbmc.executebuiltin("Container.SetViewMode(500)")
def MAIN():
    addDir('UK','http://myiplayer.eu/UKmenu/menu/index.html',10,'%s/resources/art/uk.png'%local.getAddonInfo("path"))
    addDir('US','http://myiplayer.eu/USmenu/menu/index.html',10,'%s/resources/art/usa.png'%local.getAddonInfo("path"))
    addDir('FRANCE','http://myiplayer.eu/Francemenu/menu/index.html',10,'%s/resources/art/france.png'%local.getAddonInfo("path"))
    addDir('GERMANY','http://myiplayer.eu/Germanymenu/menu/index.html',10,'%s/resources/art/germany.png'%local.getAddonInfo("path"))
    addDir('ITALY','http://myiplayer.eu/Italymenu/menu/index.html',10,'%s/resources/art/italy.png'%local.getAddonInfo("path"))
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def INDEX(url):
    html = make_http_get_request(url)
    #net.save_cookies(cookie_jar)
    print html
    #r = re.compile(r'div data-image="(.+?)" data-link="../../(.+?)"></div>',re.I).findall(html)
    # Not sure what is going on for the re.findall parts a few lines down, but my re.compile will get
    # you the link, image and title of the channel from the uk, us, france, germany or italy page :)
    # LINK, IMG, TITLE
    r = re.compile(r'div data-image="(.+?)" data-link="../../(.+?)"></div>',re.I).findall(html)
    for image, link in r:
            name = re.findall('(.+?).jp',image)
            if len(name) == 0:
                name = re.findall(r'(.+?).pn',image)
            name = ''.join(name)
            print 'Name is: '+str(name)
            print 'IMAGE IS: '+str(image)
            print 'LINK IS: '+link
            if 'UK/' in link:
                IMAGE_URL = 'http://myiplayer.eu/UKmenu/menu/'
            if 'USA/' in link:
                IMAGE_URL = 'http://myiplayer.eu/USmenu/menu/'
            if 'France/' in link:
                IMAGE_URL = 'http://myiplayer.eu/Francemenu/menu/'
            if 'Germany/' in link:
                IMAGE_URL = 'http://myiplayer.eu/Germanymenu/menu/'
            if 'Italy/' in link:
                IMAGE_URL = 'http://myiplayer.eu/Italymenu/menu/'
        
            addDir(name,BASE_URL+link,20,IMAGE_URL+image)
    #xbmc.executebuiltin("Container.SetViewMode(501)")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
##
# When given a channel url, it adds links to watch that channel
## 
def VIDEOLINKS(url, name):
    html = make_http_get_request(url)

    matches = re.compile('<iframe src="(http://www.myiplayer.eu.+?)".+?></iframe>').findall(html)

    if (len(matches) > 0):
        first_link = matches[0]

        print "The first stream is: " + first_link

        first_link_html = make_http_get_request(first_link)
        
        add_stream_url(first_link_html)
        add_alternate_links(first_link, first_link_html)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

##
# When given the url to the first source and the html representation of that page, it
# does the following:
# 
# * Look at if the current channel have other sources
# * If they have other sources, it calls add_stream_url to add them
##
def add_alternate_links(url, first_link_html):
    streams = re.compile('<a href="(.+?)" target="_self">').findall(first_link_html) 

    if (len (streams) < 2):
        return

    for stream in streams[1:]:
        stream_url =  url + "/../" + stream

        stream_html = make_http_get_request(stream_url)

        add_stream_url(stream_html)

##
# This method takes in the html of a source and it finds, resolves and adds the playable link
# to it.
##
def add_stream_url(html):
    source_matches = re.compile('src="(.+?)"').findall(html)
    for source in source_matches:
        source_domain = get_domain_name(source)

        if (source_domain == "futuboxhd.com"):

            rtmpProp = re.compile('(.+?)\?.+?streamer=(.+?)(&amp)?;file=(.+?)$').findall(source)
            for swfUrl, tcUrl, _, playPath in rtmpProp:
                rtmpUrl = tcUrl + playPath + " swfUrl=" + swfUrl + " pageUrl="+ swfUrl
                print rtmpUrl
                addLink(source_domain,  rtmpUrl, "")
        elif (source_domain != "Unknown"):
            print "%s not resolved yet!" % source_domain

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
 




def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


       
              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


## Mode meanings:
# None: The main category
# 10: Show the different channels in a particular language
# 20: Display a list of links for a particular TV channel

if mode==None or url==None or len(url)<1:
    MAIN()
       
elif mode==10:
    INDEX(url)
        
elif mode==20:
    VIDEOLINKS(url,name)

#xbmc.executebuiltin("Container.SetViewMode(50)")
