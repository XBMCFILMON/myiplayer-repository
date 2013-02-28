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

#xbmc.executebuiltin("Container.SetViewMode(500)")
def MAIN():
        addDir('UK','http://myiplayer.eu/UKmenu/menu/index.html',10,'%s/resources/art/uk.png'%local.getAddonInfo("path"))
        addDir('US','http://myiplayer.eu/USmenu/menu/index.html',10,'%s/resources/art/usa.png'%local.getAddonInfo("path"))
        addDir('FRANCE','http://myiplayer.eu/Francemenu/menu/index.html',10,'%s/resources/art/france.png'%local.getAddonInfo("path"))
        addDir('GERMANY','http://myiplayer.eu/Germanymenu/menu/index.html',10,'%s/resources/art/germany.png'%local.getAddonInfo("path"))
        addDir('ITALY','http://myiplayer.eu/Italymenu/menu/index.html',10,'%s/resources/art/italy.png'%local.getAddonInfo("path"))

def INDEX(url):
        html = net.http_GET(url).content
        #net.save_cookies(cookie_jar)
        print html
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

if mode==None or url==None or len(url)<1:
        print ""
        MAIN()
       
elif mode==1:
        print ""+url
        INDEX(url)

elif mode==10:
        INDEX(url)
        
        
elif mode==2:
        print ""+url
        VIDEOLINKS(url,name)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
#xbmc.executebuiltin("Container.SetViewMode(50)")
