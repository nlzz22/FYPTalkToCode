import os
import wx
import wx.lib.agw.peakmeter as PM
import threading
from threading import Thread
from CodeFormatter import CodeFormatter
from CodingByDictationLogic import CodingByDictationLogic as ProgramLogic
import Queue

class CustomColor:
    DARK_GRAY = (111,111,116)
    LIGHT_GRAY = (213, 213, 214)
    PALE_GRAY = (235, 235, 236)
    WHITE = (255,255,255)
    RED = (255, 10, 10)
    GREEN = (0, 100, 0)

class CodingByDictRecognition(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui

    def run(self):
        self.programLogic = ProgramLogic(self.ui)
        self.programLogic.main(self)

    def undo(self):
        self.programLogic.undo()

    def startRecording(self):
        self.programLogic.unlock_voice(self)

    def UpdateFeedbackOne(self, feedback):
        wx.CallAfter(self.ui.UpdateFeedbackOne, feedback)

    def UpdateFeedbackTwo(self, feedback):
        wx.CallAfter(self.ui.UpdateFeedbackTwo, feedback)

    def UpdateFeedbackThree(self, feedback):
        wx.CallAfter(self.ui.UpdateFeedbackThree, feedback)

    def UpdateFeedbackFour(self, feedback):
        wx.CallAfter(self.ui.UpdateFeedbackFour, feedback)

    def UpdateFeedbackFive(self, feedback):
        wx.CallAfter(self.ui.UpdateFeedbackFive, feedback)

    def UpdateCodeBody(self, feedback):
        wx.CallAfter(self.ui.UpdateCodeBody, feedback)

    def UpdateHistoryBody(self, feedback):
        wx.CallAfter(self.ui.UpdateHistoryBody, feedback)

    def OnRecordingMode(self):
        wx.CallAfter(self.ui.OnRecordingMode)

    def OffRecordingMode(self):
        wx.CallAfter(self.ui.OffRecordingMode)

    def PassSoundEnergyValues(self, value):
        wx.CallAfter(self.ui.PassSoundEnergyValue, value)

    def ShowVisualizer(self, to_show):
        wx.CallAfter(self.ui.ShowVisualizer, to_show)


''' We derive a new class of Frame. '''
class CodeByDictUI(wx.Frame):
    SPACE_BETWEEN_BUTTONS = 50
    SPACE_SIDE_OF_BUTTONS = 10
    SPACE_VERTICAL_BUTTONS = 7
    FONT_SIZE_FEEDBACK = 12
    FONT_SIZE_CODE = 10
    FONT_FAMILY_CODE = wx.FONTFAMILY_MODERN # a fixed pitch font
    VISUALIZER_NUM_BAND = 2
    VISUALIZER_LED_PER_BAND = 15
    VISUALIZER_FRAME_PER_SECOND = 18
    VISUALIZER_TIMER_UPDATE_PER_SECOND = 50
    STRING_ON_RECORD = "\n\n\nRecording mode is ON"
    STRING_OFF_RECORD = "\n\n\nRecording mode is OFF"
    
    def __init__(self, parent, title):
        self.queue_buffer = Queue.Queue()
        self.show_visualizer = False
        
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
        self.SetFont(self.bodyCode, CodeByDictUI.FONT_SIZE_CODE, CodeByDictUI.FONT_FAMILY_CODE)

        self.bodyHistory = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.bodyHistory.AppendText("There is no history.")
        self.bodyHistory.SetBackgroundColour(CustomColor.LIGHT_GRAY)

        # Body Sizer
        self.bodySizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bodySizer.Add(self.bodyCode, 1, wx.EXPAND)
        self.bodySizer.Add(self.bodyHistory, 1, wx.EXPAND)

        # Create the lines of feedback
        self.feedbackOne = wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.feedbackOne.SetBackgroundColour(CustomColor.PALE_GRAY)
        self.feedbackOne.SetForegroundColour(CustomColor.RED)
        self.SetFont(self.feedbackOne, CodeByDictUI.FONT_SIZE_FEEDBACK)
        
        self.feedbackTwo = wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.feedbackTwo.SetBackgroundColour(CustomColor.LIGHT_GRAY)
        self.SetFont(self.feedbackTwo, CodeByDictUI.FONT_SIZE_FEEDBACK)
        
        self.feedbackThree = wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.feedbackThree.SetBackgroundColour(CustomColor.LIGHT_GRAY)
        self.SetFont(self.feedbackThree, CodeByDictUI.FONT_SIZE_FEEDBACK)
        
        self.feedbackFour = wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.feedbackFour.SetBackgroundColour(CustomColor.DARK_GRAY)
        self.SetFont(self.feedbackFour, CodeByDictUI.FONT_SIZE_FEEDBACK)
        
        self.feedbackFive = wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER | wx.BORDER)
        self.feedbackFive.SetBackgroundColour(CustomColor.LIGHT_GRAY)
        self.SetFont(self.feedbackFive, CodeByDictUI.FONT_SIZE_FEEDBACK)

        # Feedback Sizer
        self.feedbackSizer = wx.BoxSizer(wx.VERTICAL)
        self.midFeedbackSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.midFeedbackSizer.Add(self.feedbackTwo, 1, wx.FIXED_MINSIZE)
        self.midFeedbackSizer.Add(self.feedbackThree, 1, wx.FIXED_MINSIZE)
        
        self.feedbackSizer.Add(self.feedbackOne, 1, wx.EXPAND)
        self.feedbackSizer.Add(self.midFeedbackSizer, 1, wx.EXPAND)
        self.feedbackSizer.Add(self.feedbackFour, 1, wx.EXPAND)
        self.feedbackSizer.Add(self.feedbackFive, 1, wx.EXPAND)

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

        # Recording Bar
        self.recordStatus = wx.StaticText(self, label=CodeByDictUI.STRING_ON_RECORD, style=wx.ALIGN_CENTER)
        self.recordStatus.SetBackgroundColour(CustomColor.LIGHT_GRAY)
        self.recordStatus.SetForegroundColour(CustomColor.GREEN)
        self.SetFont(self.recordStatus, CodeByDictUI.FONT_SIZE_FEEDBACK)

        # Recording Visualizer
        self.vertPeak = PM.PeakMeterCtrl(self, -1, style=wx.SIMPLE_BORDER, agwStyle=PM.PM_VERTICAL)   
        self.vertPeak.SetMeterBands(CodeByDictUI.VISUALIZER_NUM_BAND, CodeByDictUI.VISUALIZER_LED_PER_BAND)
        self.vertPeak.SetRangeValue(800, 3500, 8000)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.ShowVisualizer(False)
        wx.CallLater(500, self.visualizer_start)

        # Recording Bar sizer
        self.recordSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.recordSizer.Add(self.recordStatus, 2, wx.EXPAND)
        self.recordSizer.Add(self.vertPeak, 1, wx.EXPAND|wx.ALL)
                                       
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
        self.sizer.Add(self.recordSizer, 0, wx.EXPAND)

        # Layout sizers
        self.SetSizer(self.sizer) # tell frame to use which sizer.
        self.SetAutoLayout(True)
        self.sizer.Fit(self)
        self.Show()

        # run the recognition
        self.recognition = CodingByDictRecognition(ui=self)
        self.recognition.start()

        self.dirname = ''
        self.code_formatter = CodeFormatter()

    def OnTimer(self, event):
        # Retrieve data for the meter
        temp_num_elem = min(self.queue_buffer.qsize(), 5)
        if temp_num_elem > 0:
            energy_values = []

            for i in xrange(temp_num_elem):
                data = self.queue_buffer.get()
                energy_values.append(data)
                energy_values.append(data + 100) # populate more data to create smoother effect

            if self.show_visualizer:
                self.vertPeak.SetData(energy_values, 0, len(energy_values))
            else:
                self.vertPeak.SetData([0, 0, 0], 0, 3)
            

    def visualizer_start(self):
        self.timer.Start(1000 / CodeByDictUI.VISUALIZER_TIMER_UPDATE_PER_SECOND)
        self.vertPeak.Start(1000 / CodeByDictUI.VISUALIZER_FRAME_PER_SECOND)

    def PassSoundEnergyValue(self, energy):
        self.queue_buffer.put(energy)

    def SetFont(self, textControl, fontSize, family=wx.DEFAULT, style=wx.NORMAL, weight=wx.NORMAL):
        font = wx.Font(fontSize, family, style, weight)
        textControl.SetFont(font)

    def UpdateFeedbackOne(self, feedback):
        self.feedbackOne.SetLabel(feedback)
        self.RefreshSizer()

    def UpdateFeedbackTwo(self, feedback):
        self.feedbackTwo.SetLabel(feedback)
        self.RefreshSizer()

    def UpdateFeedbackThree(self, feedback):
        self.feedbackThree.SetLabel(feedback)
        self.RefreshSizer()

    def UpdateFeedbackFour(self, feedback):
        self.feedbackFour.SetLabel(feedback)
        self.RefreshSizer()

    def UpdateFeedbackFive(self, feedback):
        self.feedbackFive.SetLabel(feedback)
        self.RefreshSizer()

    def OnRecordingMode(self):
        self.recordStatus.SetLabel(CodeByDictUI.STRING_ON_RECORD)
        self.recordStatus.SetForegroundColour(CustomColor.GREEN)
        self.RefreshSizer()

    def OffRecordingMode(self):
        self.recordStatus.SetLabel(CodeByDictUI.STRING_OFF_RECORD)
        self.recordStatus.SetForegroundColour(CustomColor.RED)
        self.RefreshSizer()

    def ShowVisualizer(self, to_show):
        self.show_visualizer = to_show

    def UpdateCodeBody(self, code):
        if code.strip() == "":
            code = "No code has been generated yet."

        formatted_code = self.code_formatter.format_code(code)
        self.bodyCode.SetValue(formatted_code)
        self.RefreshSizer()

    def UpdateHistoryBody(self, hist):
        if hist.strip() == "":
            hist = "There is no history."
        self.bodyHistory.SetValue(hist)
        self.RefreshSizer()

    def RefreshSizer(self):
        self.sizer.Layout() # reupdate the layout of sizer.

    def OnUndo(self, event):
        self.recognition.undo()
        
    def OnExport(self, event):
        # Save away the edited text
        # Open the file, do an RU sure check for an overwrite!
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", \
                wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            # Grab the content to be saved
            itcontains = self.bodyCode.GetValue()

            # Open the file for write, write, close
            self.filename=self.process_file_name(dlg.GetFilename())
            self.dirname=dlg.GetDirectory()
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()

            self.UpdateFeedbackOne("Your code has been saved to " + self.filename)
        # Get rid of the dialog to keep things tidy
        dlg.Destroy()
    
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

    def process_file_name(self, file_name):
        if len(file_name) < 2 or file_name[-2:] != ".c":
            return file_name + ".c"
        else:
            return file_name
        

app = wx.App(False) # create a new app, don't redirect stdout to window.
frame = CodeByDictUI(None, "Coding by Dictation") # Top-level window
app.MainLoop() # handle events
