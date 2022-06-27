import wx

class DemodataAssoc(wx.Frame):

    def __init__(self, parent, title):
        super(DemodataAssoc, self).__init__(parent, title=title, size=(500, 500))
        self.InitUI()
        self.Centre()
        self.Show()

    from .loading import OnOpen, OnPause, St


    def InitUI(self):
        # setting the menu bar
        menubar = wx.MenuBar()

        #setting items in the menu bar ie File and Playback
        fileMenu = wx.Menu()
        fitem1 = fileMenu.Append(wx.ID_OPEN, 'Open', 'Choose a recording')
        fitem2 = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')

        playBackMenu=wx.Menu()
        pitem1 = playBackMenu.Append(wx.ID_ANY, 'Play', 'Choose a recording')
        pitem2 = playBackMenu.Append(wx.ID_ANY, 'Pause', 'Choose a recording')
        pitem3 = playBackMenu.Append(wx.ID_ANY, 'Stop', 'Choose a recording')
        menubar.Append(playBackMenu, '&PlayBack')

        self.SetMenuBar(menubar)

        #binding the objects fititem1, fititem2 and pititem1 to the menu object
        self.Bind(wx.EVT_MENU, self.OnOpen, fitem1)
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem2)
        self.Bind(wx.EVT_MENU, self.OnPlay, pitem1)
        self.Bind(wx.EVT_MENU, self.OnPause, pitem2)
        self.Bind(wx.EVT_MENU, self.OnStop, pitem3)

        self.panel=wx.Panel(self)#setting the panel
        self.Stop=0 # flag for Stoping the video
        self.Pause=0 # flag for Pauseing the video
        self.itrn1 = 0 # used to hold the count of the frame during pause
        self.another_flag = 0 # used for pause function