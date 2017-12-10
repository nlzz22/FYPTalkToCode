import os
import wx

class MyFrame(wx.Frame):
    ''' We derive a new class of Frame. '''
    def __init__(self, parent, title):
        self.dirname = ''
        
        wx.Frame.__init__(self, parent, title=title, size=(200,-1)) # 200px width and default height (-1)
        self.control = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE) # add text box widget , style= (wx.TE_MULTILINE) for with multiple lines text.
        self.control.AppendText("i am line one\n")
        self.control.AppendText("   i am line two")
        self.control.SetBackgroundColour((211, 211, 211))
        self.CreateStatusBar() # A status bar in the bottom of the window

        self.panel = wx.Panel(self)
        self.quote = wx.StaticText(self.panel, label="Your quote: ")
        #self.quote.SetForegroundColour((255,0,0)) # text color
        #self.quote.SetBackgroundColour((25,25,150)) # background color

        # Setting up the menu
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open a file")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit"," Terminate the program")

        # Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # add "filemenu" to the MenuBar
        self.SetMenuBar(menuBar) # add MenuBar to the Frame Content.

        # Set events
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout) # bind a menu item "about" to event "OnAbout"
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []
        for i in range(0, 6):
            self.buttons.append(wx.Button(self, -1, "Button &"+str(i)))
            self.sizer2.Add(self.buttons[i], 1, wx.EXPAND) # arg 1: control to include, arg 2: size weight factor, arg 3: wx.EXPAND
                                                        # means control will be resized when necessary
            self.Bind(wx.EVT_BUTTON, self.OnBtn, self.buttons[i])

        # use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control, 5, wx.EXPAND) # text box
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)# 0 as 2nd arg means this sizer will not resize
        self.sizer.Add(self.panel, 1, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer) # tell frame to use which sizer.
        self.SetAutoLayout(True)
        self.sizer.Fit(self)
        self.Show()

    def OnBtn(self, event):
        self.control.AppendText("wei to the he\n")

    def OnOpen(self, event):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.control.SetValue(f.read()) # write values read from file to text box.
            f.close()
        dlg.Destroy()

    def OnAbout(self, event):
        # A message dialog box with an OK button. wx.OK is standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small text editor", "About Sample Editor", wx.OK) # we can omit the id (last param)
        dlg.ShowModal()
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, event):
        self.Close(True) # close the frame
        

app = wx.App(False) # create a new app, don't redirect stdout to window.
frame = MyFrame(None, "Sample editor") # Top-level window
app.MainLoop() # handle events
