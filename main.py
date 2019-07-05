import wx
from github import Github
import github
import os
import urllib
import urllib3
import threading
import subprocess
WORKDIR = os.getcwd()
global INSTALLED_VERSIONS
INSTALLED_VERSIONS = []
if(not os.path.exists("versions")):
    os.mkdir("versions")
    
os.chdir(WORKDIR + "\\versions\\")
INSTALLED_VERSIONS = os.listdir()
class Version:
    def __init__(self, release, is_installed=False):
        self.name = release.title.replace(" ","_")
        self.release = release
        self.is_installed = is_installed
    def GetDownloadLink(self):
        assets = self.release.get_assets()
        if(assets.totalCount == 0): 
            print("ASSETS <= 0")
            return ""
        desktopRelease = assets[0]
        return desktopRelease.browser_download_url
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.selectedList = 0
        self.versionData = {}
        panel = wx.Panel(self)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        versionList = wx.ListCtrl(panel,style=wx.LC_REPORT)
        versionList.SetBackgroundColour(wx.WHITE)
        self.versionList = versionList
        
        
        sizer1.Add(versionList,1,wx.EXPAND)
        controlPanel = wx.Panel(panel)
        controlPanel.SetBackgroundColour(wx.Colour(34,34,34))
        controlPanel.SetMinSize(wx.Size(-1,100))
        sizer1.Add(controlPanel,0,wx.EXPAND)
        
        controlSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.playButton = wx.Button(controlPanel)
        self.playButton.SetLabel("Play")
        #playButton.SetMaxSize(wx.Size(200,100))
        controlSizer.Add(self.playButton,1,wx.EXPAND)
        controlPanel.SetSizer(controlSizer)
        
        self.prog = wx.Gauge(panel)
        self.prog.SetRange(100)
        self.prog.SetMinSize(wx.Size(-1,20))
        sizer1.Add(self.prog,0,wx.EXPAND)
        
        self.refreshVersionList(versionList)        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.onItemSelected,versionList)
        self.Bind(wx.EVT_BUTTON, self.onPlay, self.playButton)
        
        panel.SetSizer(sizer1)
    def onPlay(self, event):
        print(self.versionData[self.selectedList].is_installed)
        if(self.versionData[self.selectedList].is_installed):
            # Play the game
            os.system(WORKDIR)
            os.system("cd jre")
            os.system("cd bin")
            os.system("java -jar " + WORKDIR +'/versions/' + self.versionData[self.selectedList].name+"/desktop_release.jar")
            #subprocess.run([WORKDIR+'\\jre\\bin\\java', '-jar' + ' ' + WORKDIR+'/versions/' + self.versionData[self.selectedList].name + '/desktop_release.jar'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        else:
            self.playButton.Disable()
            ver = self.versionData[self.selectedList]
            url = ver.GetDownloadLink()
            if(url == ""):
                print("No Assets found")
                return
            file_name = url.split('/')[-1]
            os.mkdir(WORKDIR + "/versions/" + ver.name)
            
            u = urllib.request.urlopen(url)
            
            meta = u.info()
            #meta.get
            meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
            file_size = int(meta_func("Content-Length")[0])
            def do_download(self2):
                file_size_dl = 0
                block_sz = 8192
                print("Downloading from %s", url)
                f = open(WORKDIR + "/versions/" + ver.name + "/desktop_release.jar", "wb+")  
                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break
                      
                    file_size_dl += len(buffer)
                    f.write(buffer)
                    progress = file_size_dl * 100. / file_size
                    self.prog.SetValue(progress)
                    #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                    #status = status + chr(8)*(len(status)+1)
                    #print(status) 
                    
                f.close()
                self.playButton.Enable()
                self.refreshVersionList(self.versionList)
                
                # Play the game
                os.system(WORKDIR)
                os.system("cd jre")
                os.system("cd bin")
                os.system("java -jar " + WORKDIR +'/versions/' + self.versionData[self.selectedList].name+"/desktop_release.jar")
            t = threading.Thread(target=do_download, args=(1,))
            t.start()
            print("play")
    def onItemSelected(self,event):
        ind = event.GetIndex()
        is_installed = self.versionData[ind].is_installed
        if(is_installed):
            self.playButton.SetLabel("Play\n" + self.versionList.GetItemText(ind))
        else:
            self.playButton.SetLabel("Install and Play\n" + self.versionList.GetItemText(ind))     
        self.selectedList = ind
    def refreshVersionList(self, listCtrl):
        self.versionList.ClearAll()
        self.versionList.AppendColumn("Name")
        self.versionList.AppendColumn("Status")
        g = Github("03799e90436aa1a808715498b40962f84b272359")
        repo = g.get_repo("Anuken/Mindustry")
        releases = repo.get_releases()
        
        for release in releases:
            v = Version(release)
            ind = listCtrl.GetItemCount()
            listCtrl.InsertItem(ind,release.title)
            is_installed = release.title.replace(" ", "_") in INSTALLED_VERSIONS
            if(is_installed):
                listCtrl.SetStringItem(ind,1,"Installed")
            else:
                listCtrl.SetStringItem(ind,1,"Not installed")
            v.is_installed = is_installed
            self.versionData[ind] = v
        self.playButton.SetLabel("Play\n" + listCtrl.GetItem(0).GetText())
    def main(self):
        pass
app = wx.App()

frame = MainFrame(None, title="Mindustry Launcher")
frame.Show()


app.MainLoop()