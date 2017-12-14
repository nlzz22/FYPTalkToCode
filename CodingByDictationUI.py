import os
import wx
import threading
from threading import Thread
import time
import CodingByDictationLogic as programLogic

class CustomColor:
    DARK_GRAY = (111,111,116)
    LIGHT_GRAY = (213, 213, 214)
    PALE_GRAY = (235, 235, 236)
    WHITE = (255,255,255)

class CodingByDictRecognition(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui

    def run(self):
        programLogic.main(self)

    def UpdateDisplayFeedback(self, feedback):
        wx.CallAfter(self.ui.UpdateDisplayFeedback, feedback)

    def UpdateRecognitionFeedback(self, feedback):
        wx.CallAfter(self.ui.UpdateRecognitionFeedback, feedback)

    def UpdateCodeBody(self, feedback):
        wx.CallAfter(self.ui.UpdateCodeBody, feedback)

    def UpdateHistoryBody(self, feedback):
        wx.CallAfter(self.ui.UpdateHistoryBody, feedback)


''' We derive a new class of Frame. '''
class CodeByDictUI(wx.Frame):
    SPACE_BETWEEN_BUTTONS = 50
    SPACE_SIDE_OF_BUTTONS = 10
    SPACE_VERTICAL_BUTTONS = 7
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        # Create the titles.
        self.titleCode = wx.StaticText(self, label="Program Code", style=wx.ALIGN_CENTER | wx.BORDER)
        self.titleCode.SetBackgroundColour(CustomColor.DARK_GRAY)
        self.titleCode.SetForegroundColour(CustomColor.WHITE)

        self.titleHistory = wx.StaticText(self, label="History", style=wx.ALIGN_CENTER | wx.BORDER)
        self.titleHistory.SetBackgroundColour(CustomColor.DARK_GRAY)
        self.titleHistory.SetForegroundColour(CustomColor.WHITE)

        # Title Sizer
        self.titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.titleSizer.Add(self.titleCode, 1, wx.EXPAND) # arg 1: control to include, arg 2: size weight factor, arg 3: wx.EXPAND
                                                        # means control will be resized when necessary
        self.titleSizer.Add(self.titleHistory, 1, wx.EXPAND)

        # Create the body
        self.bodyCode = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE) # add text box widget , style= (wx.TE_MULTILINE) for with multiple lines text.
        self.bodyCode.AppendText("No code has been generated yet.")
        self.bodyCode.SetBackgroundColour(CustomColor.LIGHT_GRAY)

        self.bodyHistory = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.bodyHistory.AppendText("There is no history.")
        self.bodyHistory.SetBackgroundColour(CustomColor.LIGHT_GRAY)

        # Body Sizer
        self.bodySizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bodySizer.Add(self.bodyCode, 1, wx.EXPAND)
        self.bodySizer.Add(self.bodyHistory, 1, wx.EXPAND)

        # Create the 2 lines of feedback
        self.recognitionFeedback = wx.StaticText(self, label="Feedback: ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.recognitionFeedback.SetBackgroundColour(CustomColor.PALE_GRAY)
        self.displayFeedback = wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.displayFeedback.SetBackgroundColour(CustomColor.LIGHT_GRAY)

        # Feedback Sizer
        self.feedbackSizer = wx.BoxSizer(wx.VERTICAL)
        self.feedbackSizer.Add(self.recognitionFeedback, 1, wx.EXPAND)
        self.feedbackSizer.Add(self.displayFeedback, 1, wx.EXPAND)

        # Create the buttons
        self.buttonUndo = wx.Button(self, -1, "Undo")
        self.buttonExport = wx.Button(self, -1, "Export")
        self.buttonCheatsheet = wx.Button(self, -1, "Cheatsheet")

        self.Bind(wx.EVT_BUTTON, self.OnUndo, self.buttonUndo)
        self.Bind(wx.EVT_BUTTON, self.OnExport, self.buttonExport)
        self.Bind(wx.EVT_BUTTON, self.OnCheatsheet, self.buttonCheatsheet)   

        # Button Sizer
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.AddSpacer(CodeByDictUI.SPACE_SIDE_OF_BUTTONS)
        self.buttonSizer.Add(self.buttonUndo, 1, wx.EXPAND)
        self.buttonSizer.AddSpacer(CodeByDictUI.SPACE_BETWEEN_BUTTONS)
        self.buttonSizer.Add(self.buttonExport, 1, wx.EXPAND)
        self.buttonSizer.AddSpacer(CodeByDictUI.SPACE_BETWEEN_BUTTONS)
        self.buttonSizer.Add(self.buttonCheatsheet, 1, wx.EXPAND)
        self.buttonSizer.AddSpacer(CodeByDictUI.SPACE_SIDE_OF_BUTTONS)
                                       
        # Status Bar
        self.CreateStatusBar() # A status bar in the bottom of the window

        # Setting up the menu
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit"," Terminate the program")

        # Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # add "filemenu" to the MenuBar
        self.SetMenuBar(menuBar) # add MenuBar to the Frame Content.

        # Set events
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout) # bind a menu item "about" to event "OnAbout"
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        # The main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.SetMinSize(800, 300) # sets the default sizer size.
        self.sizer.Add(self.titleSizer, 0, wx.EXPAND)
        self.sizer.Add(self.bodySizer, 5, wx.EXPAND)
        self.sizer.Add(self.feedbackSizer, 0, wx.EXPAND) # 0 means will not resize.
        self.sizer.AddSpacer(CodeByDictUI.SPACE_VERTICAL_BUTTONS)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND)
        self.sizer.AddSpacer(CodeByDictUI.SPACE_VERTICAL_BUTTONS)

        # Layout sizers
        self.SetSizer(self.sizer) # tell frame to use which sizer.
        self.SetAutoLayout(True)
        self.sizer.Fit(self)
        self.Show()

        # run the recognition
        self.recognition = CodingByDictRecognition(ui=self)
        self.recognition.start()

    def UpdateDisplayFeedback(self, feedback):
        self.displayFeedback.SetLabel(feedback)
        self.RefreshSizer()

    def UpdateRecognitionFeedback(self, feedback):
        self.recognitionFeedback.SetLabel(feedback)
        self.RefreshSizer()

    def UpdateCodeBody(self, code):
        self.bodyCode.SetValue(code)
        self.RefreshSizer()

    def UpdateHistoryBody(self, hist):
        self.bodyHistory.SetValue(hist)
        self.RefreshSizer()

    def RefreshSizer(self):
        self.sizer.Layout() # reupdate the layout of sizer.

    def OnUndo(self, event):
        print "undo"
        
    def OnExport(self, event):
        print "export"
    
    def OnCheatsheet(self, event):
        cheatsheetContents = "Structured Language\n\n" + \
            "Declare variable: declare integer first equal one end declare\n\n" + \
            "To be continued..."
        cheatsheet = wx.MessageDialog(self, cheatsheetContents, "Cheatsheet")
        cheatsheet.ShowModal()
        cheatsheet.Destroy()

    def OnAbout(self, event):
        # A message dialog box with an OK button. wx.OK is standard ID in wxWidgets.
        aboutMessage = "An app which allows you to code with your voice instead of the keyboard!" + "\n\nby: Nicholas Lam" + "\n\nSupervised by: Prof. Ooi"
        dlg = wx.MessageDialog(self, aboutMessage, "About Coding by Dictation", wx.OK) # we can omit the id (last param)
        dlg.ShowModal()
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, event):
        self.Close(True) # close the frame
        

app = wx.App(False) # create a new app, don't redirect stdout to window.
frame = CodeByDictUI(None, "Coding by Dictation") # Top-level window
app.MainLoop() # handle events
