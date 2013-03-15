import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,os
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
import datetime
import time

net = Net()
ADDON = xbmcaddon.Addon(id='plugin.video.myiplayer')
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
    print "Getting Http Request for "+url
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
    addDir('UK','http://myiplayer.eu/UKmenu/menu/index.html',10,'%s/resources/art/uk.png'%ADDON.getAddonInfo("path"))
    addDir('US','http://myiplayer.eu/USmenu/menu/index.html',10,'%s/resources/art/usa.png'%ADDON.getAddonInfo("path"))
    addDir('FRANCE','http://myiplayer.eu/Francemenu/menu/index.html',10,'%s/resources/art/france.png'%ADDON.getAddonInfo("path"))
    addDir('GERMANY','http://myiplayer.eu/Germanymenu/menu/index.html',10,'%s/resources/art/germany.png'%ADDON.getAddonInfo("path"))
    addDir('ITALY','http://myiplayer.eu/Italymenu/menu/index.html',10,'%s/resources/art/italy.png'%ADDON.getAddonInfo("path"))
    addDir('SPORTS','http://myiplayer.eu/Sportsmenu/menu/index.html',10,'%s/resources/art/rr.png'%ADDON.getAddonInfo("path"))

def INDEX(url):
    html = make_http_get_request(url)
    #net.save_cookies(cookie_jar)
    #r = re.compile(r'div data-image="(.+?)" data-link="../../(.+?)"></div>',re.I).findall(html)
    # Not sure what is going on for the re.findall parts a few lines down, but my re.compile will get
    # you the link, image and title of the channel from the uk, us, france, germany or italy page :)
    # LINK, IMG, TITLE
    r = re.compile(r'div data-image="(.+?)" data-link="../../(.+?)"></div>',re.I).findall(html)
    for image, link in r:
            print 'http://myiplayer.eu/'+link
            name = re.findall('(.+?).jp',image,re.IGNORECASE)
            if len(name) == 0:
                name = re.findall(r'(.+?).pn',image,re.IGNORECASE)
            name = ''.join(name)
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
            if 'sportstoday.php' in link:
                IMAGE_URL = 'http://myiplayer.eu/Sportsmenu/menu/'
            try:
                name = name.split('/menu/')[1]
            except:
                pass
            addDir(name.upper(),BASE_URL+link,20,IMAGE_URL+image)
    #xbmc.executebuiltin("Container.SetViewMode(501)")
        
##
# When given a channel url, it adds links to watch that channel
## 
def VIDEOLINKS(url, name,iconimage):
    html = make_http_get_request(url)

    matches = re.compile('<iframe src="(http://www.myiplayer.eu.+?)".+?></iframe>').findall(html)
    matches2 = re.compile('<iframe src="(http://www.watchtelevision.eu.+?)".+?><br />\n      </iframe>').findall(html)#sports domain is different uses watchtelevision.eu
    if (len(matches) > 0):
        first_link = matches[0]

        print "The first stream is: " + first_link

        first_link_html = make_http_get_request(first_link)
        
        add_stream_url(iconimage,first_link_html)
        add_alternate_links(first_link, first_link_html)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif (len(matches2) > 0):
        first_link = matches2[0]

        print "The first stream is: " + first_link

        first_link_html = make_http_get_request(first_link)
        
        add_stream_url(iconimage,first_link_html)
        add_alternate_links(first_link, first_link_html)

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

        add_stream_url(iconimage,stream_html)

##
# This method takes in the html of a source and it finds, resolves and adds the playable link
# to it.
##
def add_stream_url(iconimage,html):
    source_matches = re.compile('src="(.+?)"').findall(html)
    for source in source_matches:
        print "source="+source
        source_domain = get_domain_name(source)

        if (source_domain == "futuboxhd.com"):

            rtmpProp = re.compile('(.+?)\?.+?streamer=(.+?)(&amp)?;file=(.+?)$').findall(source)
            for swfUrl, tcUrl, _, playPath in rtmpProp:
                rtmpUrl = tcUrl + playPath + " swfUrl=" + swfUrl + " pageUrl="+ swfUrl
                addLink(source_domain,  rtmpUrl, iconimage)
        elif (source_domain == "ilive.to"):
            html = make_http_get_request(source)
            pageurl = re.compile("<iframe src='(.+?)'").findall(html)
            for pageUrl in pageurl:
                continue
            html = make_http_get_request(pageUrl)
            playpath=re.compile("file\': \'(.+?).flv").findall(html)
            for playPath in playpath:
                rtmpUrl = 'rtmp://142.4.216.176/edge playpath=' + playPath + " swfUrl=http://static.ilive.to/jwplayer/player_embed.swf pageUrl="+pageUrl+"live=1"
                addLink(source_domain,  rtmpUrl, iconimage)
        elif (source_domain == "veemi.com"):
            fid = re.compile('fid="(.+?)";').findall(html)
            stream_url = 'http://live.veemi.com:1935/live/_definst_/'+fid[0]+'/playlist.m3u8'
            addLink(source_domain,  stream_url, iconimage)
        elif (source_domain == "castalba.tv"):
            fid = re.compile('> id="(.+?)";').findall(html)
            pageUrl = 'http://castalba.tv/embed.php?cid='+fid[0]+'&wh=640&ht=385&r=lsh.lshunter.tv'
            html = make_http_get_request(pageUrl)
            swfUrl=re.compile('flashplayer\': "(.+?)"').findall(html)
            playPath=re.compile("'file\': \'(.+?)\',\r\n\r\n\t\t\t\'streamer\'").findall(html)
            rtmp=re.compile("'streamer\': \'(.+?)\',").findall(html)
            rtmpUrl= rtmp[0] + ' playpath=' + playPath[0] + ' swfUrl=' + swfUrl[0] + ' live=true timeout=15 swfVfy=true pageUrl=' + pageUrl
            addLink(source_domain,  rtmpUrl, iconimage)
        elif (source_domain == "yycast.com"):
            fid = re.compile('fid="(.+?)";').findall(html)
            pageUrl = 'http://www.yycast.com/'+fid[0]
            html = make_http_get_request(pageUrl)
            swfUrl=re.compile("'plugins': '(.+?)'").findall(html)
            playPath=re.compile("'file': '(.+?)'").findall(html)
            rtmpUrl= 'rtmp://85.12.5.44:1935/live/_definst_/'+playPath[0] + ' playpath=' + playPath[0] + ' swfUrl=http://cdn.yycast.com/player' + swfUrl[0] + 'app=live/_definst_ tcUrl=rtmp://85.12.5.44:1935/live/_definst_ live=true timeout=15 swfVfy=true pageUrl=' + pageUrl
            addLink(source_domain,  rtmpUrl, iconimage)
        elif (source_domain == "cricfree.tv"):
            html = make_http_get_request(source)
            if re.search('src="http://www.yycast.com/javascript/embedPlayer.js"',html,re.IGNORECASE):
                fid = re.compile('<script type="text/javascript.+?id="(.+?)"').findall(html)
                pageUrl = 'http://www.yycast.com/'+fid[0]
                html = make_http_get_request(pageUrl)
                playPath=re.compile("'file': '(.+?)'").findall(html)
                rtmpUrl= 'rtmp://85.12.5.44:1935/live/_definst_/'+playPath[0] + ' playpath=' + playPath[0] + ' swfUrl=http://cdn.yycast.com/player/player.swf app=live/_definst_ tcUrl=rtmp://85.12.5.44:1935/live/_definst_ live=true timeout=15 swfVfy=true pageUrl=' + pageUrl
                addLink('yycast.com',  rtmpUrl, iconimage)
            else:
	            try:
	                fid = re.compile('<script type="text/javascript.+?id="(.+?)"').findall(html)
	                rtmpUrl= 'rtmp://46.249.52.100/liveedge/'+fid[0] + ' playpath=' + fid[0] + ' swfUrl=http://cast4you.tv/p1.swf app=liveedge tcUrl=rtmp://46.249.52.100/liveedge live=true timeout=15 swfVfy=true pageUrl=http://cast4you.tv/show.php?id=' + fid[0]+'&width=620&height=490'
	                addLink(source_domain,  rtmpUrl, iconimage)
	            except:
	                pass
	            try:
	                fid = re.compile("fid='(.+?)'").findall(html)
	                rtmpUrl= 'rtmp://46.249.52.100/liveedge/'+fid[0] + ' playpath=' + fid[0] + ' swfUrl=http://cast4you.tv/p1.swf app=liveedge tcUrl=rtmp://46.249.52.100/liveedge live=true timeout=15 swfVfy=true pageUrl=http://cast4you.tv/show.php?id=' + fid[0]+'&width=620&height=490'
	                addLink(source_domain,  rtmpUrl, iconimage)
	            except:
	                pass
        elif (source_domain == "cool-tv.net"):
            fid = re.compile('flashvars="file=(.+?)&amp').findall(html)
            stream_url = fid[0]
            addLink(source_domain,  stream_url, iconimage)
        #elif (source_domain == "streamtivi.com"):
            #html = make_http_get_request(source)
            #fid = re.compile('http://streamtivi.com/embedplayer.php\?id=(.+?)&amp').findall(source)
            #manifest = 'http://peer-stream.com/api/get_manifest.f4m?groupspec='+fid[0]
            #html = make_http_get_request(manifest)
            #rtmfp = re.compile('media url="(.+?)\?family=\'publishers\'" groupspec="(.+?)" multicastStreamName="(.+?)"').findall(html)
            #ip=rtmfp[0][0]
            #groupspec=rtmfp[0][1]
            #rtmpUrl=ip+groupspec+ ' swfUrl=http://clients.cdnet.tv/flashplayer/player2.swf pageUrl=http://streamtivi.com swfVfy=1 live=1 timeout=10'
            #addLink('streamtivi.com',  rtmpUrl, iconimage)
            
            
        elif (source_domain != "Unknown"):
            print "%s not resolved yet!" % source_domain
            
class HUB( xbmcgui.WindowXMLDialog ): # The call MUST be below the xbmcplugin.endOfDirectory(int(sys.argv[1])) or the dialog box will be visible over the pop-up.
    def __init__( self, *args, **kwargs ):
        self.shut = kwargs['close_time'] 
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
                                       
    def onInit( self ):
        xbmc.Player().play('%s/resources/skins/DefaultSkin/media/xbmchub.mp3'%ADDON.getAddonInfo('path'))# Music.
        while self.shut > 0:
            xbmc.sleep(1000)
            self.shut -= 1
        xbmc.Player().stop()
        self._close_dialog()
                
    def onFocus( self, controlID ): pass
    
    def onClick( self, controlID ): 
        if controlID == 12:
            xbmc.Player().stop()
            self._close_dialog()

    def onAction( self, action ):
        if action in [ 5, 6, 7, 9, 10, 92, 117 ] or action.getButtonCode() in [ 275, 257, 261 ]:
            xbmc.Player().stop()
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .4 )
        self.close()

             
def pop():# Added Close_time for window auto-close length.....
    if xbmc.getCondVisibility('system.platform.ios'):
        if not xbmc.getCondVisibility('system.platform.atv'):
            popup = HUB('hub1.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%ADDON.getAddonInfo('path'))
    elif xbmc.getCondVisibility('system.platform.android'):
        popup = HUB('hub1.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%ADDON.getAddonInfo('path'))
    else:
        popup = HUB('hub.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%ADDON.getAddonInfo('path'))
    
    popup.doModal()
    del popup
                
def checkdate(dateString):
    try:
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
    except:
        return datetime.datetime.today() - datetime.timedelta(days = 1000) #force update


def check_popup():

    threshold  = 120

    now   = datetime.datetime.today()
    prev  = checkdate(ADDON.getSetting('pop_time'))
    delta = now - prev
    nDays = delta.days

    doUpdate = (nDays > threshold)
    if not doUpdate:
        return

    ADDON.setSetting('pop_time', str(now).split('.')[0])
    pop()

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
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
 

def PLAY_STREAM_LINK(name,url,iconimage):
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )
        liz.setProperty("IsPlayable","true")
        pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        pl.clear()
        pl.add(url, liz)
        xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(pl)


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
iconimage=None

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
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
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
    VIDEOLINKS(url,name,iconimage)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
check_popup()
