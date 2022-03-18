#!/usr/bin/python
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import os, sys, math
import youtube_dl
from youtube_dl import YoutubeDL

def SetConsoleText(text_widget, stext, clear=True):
    try: 
        if clear:
            text_widget.delete('1.0', END)
        text_widget.insert('end', stext)
        text_widget.see('end')
        text_widget.update()
    except:
        sys.exit(0)

class MyLogger(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def debug(self, msg):
        if '[youtube]' in msg:
            return
        msg += "\n"
        SetConsoleText(self.text_widget, msg, False)

    def warning(self, msg):
        SetConsoleText(self.text_widget, msg)

    def error(self, msg):
        SetConsoleText(self.text_widget, msg)

class FormatData():
    def __init__(self, format):
        # : A short description of the format
        self.format_id = format.get('format_id', None)
        #  File extension
        self.ext = format.get('ext', None)
        # The number of bytes
        self.filesize = format.get('filesize', None)
        # Width of the video
        self.width = format.get('width', None)
        # Height of the video
        self.height = format.get('height', None)
        # Average bitrate of audio and video in KBit/s
        self.tbr =  format.get('tbr')
        # Average audio bitrate in KBit/s
        self.abr = format.get('abr', None)
        # Average video bitrate in KBit/s
        self.vbr = format.get('vbr', None)
        # Audio sampling rate in Hertz
        self.asr = format.get('asr', None)
        # Frame rate
        self.fps = format.get('fps', None)
        # Name of the audio codec in use
        self.acodec = format.get('acodec', None)
        # Name of the video codec in use
        self.vcodec = format.get('vcodec', None)

        if self.filesize is None:
            self.filesize = "unknown(%s)" %self.format_id
        else:
            self.filesize = self.format_bytes(self.filesize)

        self.resolution = ''
        if self.width is not None and self.height is not None:
            self.resolution = '%dx%d' % (self.width, self.height)

        self.isAudioOnly = False
        self.isVideoOnly = False
        self.isAudioVideo = False

        if self.acodec != 'none' and self.vcodec != 'none':
            self.isAudioVideo = True
        elif self.acodec != 'none':
            self.isAudioOnly = True
        elif self.vcodec != 'none':
            self.isVideoOnly = True

    def format_bytes(self, bytes):
        if bytes is None:
            return 'N/A'
        if type(bytes) is str:
            bytes = float(bytes)
        if bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(bytes, 1024.0))
        suffix = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'][exponent]
        converted = float(bytes) / float(1024 ** exponent)
        return '%.2f %s' % (converted, suffix)

    def __str__(self):
        text = ""
        if self.ext is not None:
            text += self.ext
            text += " - "
        if self.filesize is not None:
            text += str(self.filesize)
            text += " - "
        if self.width is not None and self.height is not None:
            text += '%dx%d' % (self.width, self.height)
            text += " - "
        else:
            text += "N/A"
            text += " - "

        if self.acodec != 'none' and self.vcodec != 'none':
            text += 'audio+video'
        elif self.acodec != 'none':
            text += 'audio only'
        elif self.vcodec != 'none':
            text += 'video only'

        return text

class VideoInfo():
    def __init__(self, video_info):
        self.title = video_info['title']
        self.formats = []
        for format in video_info['formats']:
            self.formats.append(FormatData(format))

    def getAvailableFormats(self):
        format_ids = []
        format_strs = []
        for format in self.formats:
            format_strs.append(str(format))
            format_ids.append(format.format_id)
        return format_ids, format_strs
    
    def getExtenisons(self, format_type="video+audio"):
        exts = []
        for format in self.formats:
            if format_type == "audio" and format.isAudioOnly == True:
                if format.ext not in exts:
                    exts.append(format.ext)
            if format_type == "video" and format.isVideoOnly == True:
                if format.ext not in exts:
                    exts.append(format.ext)
            if format_type == "video+audio" and format.isAudioVideo == True:
                if format.ext not in exts:
                    exts.append(format.ext)
        return exts

    def getVideoResolutions(self, format_type="video+audio", ext=""):
        resolutions = []
        for format in self.formats:
            if format_type == "video" and format.isVideoOnly == True:
                if format.ext == ext:
                    if format.resolution not in resolutions:
                        resolutions.append(format.resolution)
            if format_type == "video+audio" and format.isAudioVideo == True:
                if format.ext == ext:
                    if format.resolution not in resolutions:
                        resolutions.append(format.resolution)
        return resolutions

    def getFileSizes(self, format_type="video+audio", ext="" , resolution=""):
        file_sizes = []
        for format in self.formats:
            if format_type == "audio" and format.isAudioOnly == True:
                if format.ext == ext:
                    file_sizes.append(format.filesize)
            if format_type == "video" and format.isVideoOnly == True:
                if format.ext == ext and resolution == format.resolution:
                    file_sizes.append(format.filesize)
            if format_type == "video+audio" and format.isAudioVideo == True:
                if format.ext == ext and resolution == format.resolution:
                    file_sizes.append(format.filesize)
        return file_sizes

    def getFileFormatId(self, format_type="video+audio", ext="" , file_size=""):
        for format in self.formats:
            if format_type == "audio" and format.isAudioOnly == True:
                if format.ext == ext and format.filesize == file_size:
                    return format.format_id
            if format_type == "video" and format.isVideoOnly == True:
                if format.ext == ext and format.filesize == file_size:
                    return format.format_id
            if format_type == "video+audio" and format.isAudioVideo == True:
                if format.ext == ext and format.filesize == file_size:
                    return format.format_id
        return None

class MainGUI(Frame):
    def __init__(self, master= None):
        #call frame constructor
        Frame.__init__(self, master, style='MainFrame.TFrame');

        #stretch frame at all directions
        self.grid(sticky=NSEW);

        # widgets control
        self.frameTop = None
        self.labelOutputDir = None
        self.entryOutputDir = None
        self.btnOutputDirBrowse = None
        self.labelURL = None
        self.entryURL = None
        self.btnURLVideoInfo = None

        self.frameBottom = None
        self.labelVideoTitle = None
        self.frameVideoAudio = None
        self.labelVideoAudioTitle = None
        self.labelVideoAudioExts = None
        self.comboVideoAudioExts = None
        self.labelVideoAudioResolution = None
        self.comboVideoAudioResolution = None
        self.labelVideoAudioFilesizes = None
        self.comboVideoAudioFilesizes = None
        self.btnAudioExtract = None
        self.comboAudioExtractExts = None
        self.btnVideoAudioDownload = None

        self.frameVideoAndAudio = None
        self.frameVideo = None
        self.labelVideoHeading = None
        self.labelVideoExts = None
        self.comboVideoExts = None
        self.labelVideoResolution = None
        self.comboVideoResolution = None
        self.labelVideoFilesizes = None
        self.comboVideoFilesizes = None
        self.btnVideoDownload = None

        self.frameAudio = None
        self.labelAudioHeading = None
        self.labelAudioExts = None
        self.comboAudioExts = None
        self.labelAudioFilesizes = None
        self.comboAudioFilesizes = None
        self.btnAudioDownload = None
        
        self.frameMergeVideoAudio = None
        self.labelMergeHeading = None
        self.labelMergeExts = None
        self.comboMergeExts = None
        self.btnMergeKeepVideo = None
        self.btnMergeDownload = None

        self.textConsole = None
        self.video_info = None

        #variables
        self.varOutputDir = StringVar()
        self.varURL = StringVar()
        self.varVideoTitle = StringVar()
        self.varExtractAudio = BooleanVar()
        self.varMergeKeepVideo = BooleanVar()
   
        self.ini_values = {}
        #create widgets
        self.createWidgets();

        # configure style
        self.style = ttk.Style(master)
        self.style.configure('MainFrame.TFrame', background="white")
        self.style.configure('TopFrame.TFrame', background="white", relief=RIDGE)
        self.style.configure('BottomFrame.TFrame', background="white", relief=RIDGE, borderwidth=10, highlightbackground="blue", highlightthickness=10 )

        self.style.configure('TEntry', relief = SUNKEN, width=100)
        self.style.configure('TComboBox', width=50)
        self.style.configure('TLabel', background="white")
        self.style.configure('Status.TLabel', relief=SUNKEN, background="white")

        self.ResetCombos()
        SetConsoleText(self.textConsole, 'Paste youtube url and click "Get Video Info" button')
        self.ReadINIFile()

    def ReadINIFile(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        ini_file = os.path.join(cur_dir, "youtube_downloader.ini")
        self.ini_values = {}
        try:
            with open(ini_file, 'rt') as fp:
                lines = fp.readlines()
                for line in lines:
                    vals = line.split('=',1)
                    if(len(vals)):
                        self.ini_values[vals[0]] = vals[1].strip()
        except:
            pass

        if('OUTPUT_DIRECTORY' in self.ini_values):
            if(os.path.isdir(self.ini_values['OUTPUT_DIRECTORY'])):
                outputDirPath = os.path.normpath(self.ini_values['OUTPUT_DIRECTORY'])
                self.varOutputDir.set(outputDirPath);
        
        if('LAST_YOUTUBE_URL' in self.ini_values):
            self.varURL.set(self.ini_values['LAST_YOUTUBE_URL']);

    def WriteINIFile(self):
        self.textConsole = None
        outputDirPath = self.varOutputDir.get().strip()
        self.ini_values['OUTPUT_DIRECTORY'] = outputDirPath

        urlText = self.varURL.get().strip()
        self.ini_values['LAST_YOUTUBE_URL'] = urlText

        cur_dir = os.path.dirname(os.path.realpath(__file__))
        ini_file = os.path.join(cur_dir, "youtube_downloader.ini")
        with open(ini_file, 'w') as fp:
            for key in self.ini_values.keys():
                fp.write(key+"="+self.ini_values[key]+"\n")

    def createWidgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create top and bottom frame inside main frame
        self.frameTop = self.createTopFrameWidgets()
        self.frameBottom = self.createBottomFrameWidgets()

        self.frameTop.grid(row = 0, column = 0, sticky=N+E+W, pady=5, padx=5);
        self.frameBottom.grid(row = 1, column = 0, sticky=N+S+E+W, ipadx=5, ipady=5, pady=5, padx=5);

        self.textConsole = ScrolledText(root, width=50,  height=5)
        self.textConsole.grid(row = 2, column = 0, sticky=S+W+E)

    def createTopFrameWidgets(self):
        topFrame = Frame(master=self, style="TopFrame.TFrame");
        topFrame.rowconfigure(0, weight=1)
        topFrame.rowconfigure(1, weight=1)
        topFrame.columnconfigure(1, weight=1)

        self.labelOutputDir = Label(master=topFrame, text="Output directory:");
        self.entryOutputDir = Entry (master=topFrame, style="TEntry", textvariable=self.varOutputDir)
        self.btnOutputDirBrowse = Button(master=topFrame, text="Browse", command=self.onClickOutputDirBrowseBtn)

        self.labelURL = Label(master=topFrame, text="Youtube URL:")
        self.entryURL = Entry (master=topFrame, style="TEntry", textvariable=self.varURL)
        self.btnURLVideoInfo = Button(master=topFrame, text="Get Video Info", command = self.OnURLGetVideoInfoBtn)

        # pack - add widgets to window
        self.labelOutputDir.grid(row = 0, column = 0, ipadx=5, ipady=5, sticky=W, pady=10, padx=10)
        self.entryOutputDir.grid(row = 0, column = 1, sticky=N+S+W+E, pady=10, padx=10)
        self.btnOutputDirBrowse.grid(row = 0, column = 2, pady=10, padx=10, sticky=E+W)

        self.labelURL.grid(row = 1, column = 0, ipadx=5, ipady=5, sticky=W, pady=10, padx=10)
        self.entryURL.grid(row = 1, column = 1, sticky=N+S+W+E, pady=10, padx=10)
        self.btnURLVideoInfo.grid(row = 1, column = 2, ipadx=20, pady=10, padx=10, sticky=E)

        return topFrame

    def createBottomFrameWidgets(self):
        bottomFrame = Frame(master=self, style="BottomFrame.TFrame")
        bottomFrame.rowconfigure(0, weight=1)
        bottomFrame.rowconfigure(1, weight=1)
        bottomFrame.columnconfigure(0, weight=1)
        bottomFrame.columnconfigure(1, weight=1)
 
        self.labelVideoTitle = Label(master=bottomFrame, textvariable=self.varVideoTitle);

        self.frameVideoAudio = self.createVideoAudioOnlyFrame(bottomFrame)
        self.frameVideoAndAudio = self.createVideoAndAudioFrame(bottomFrame)

        self.labelVideoTitle.grid(row = 0, column = 0, columnspan=3, sticky=N+S+E+W, pady=10, padx=10)

        self.frameVideoAudio.grid(row = 1, column = 0, sticky=N+S+E+W, pady=10, padx=10)
        self.frameVideoAndAudio.grid(row = 1, column = 1, sticky=N+S+E+W, pady=10, padx=10)

        return bottomFrame
    
    def createVideoAudioOnlyFrame(self, parent):
        frameVideoAudio = Frame(master=parent, style="BottomFrame.TFrame");
        frameVideoAudio.columnconfigure(1, weight=1)

        self.labelVideoAudioTitle = Label(master=frameVideoAudio, text="Video Audio")
        self.labelVideoAudioExts = Label(master=frameVideoAudio, text="Extensions : ");
        self.comboVideoAudioExts = ttk.Combobox(master=frameVideoAudio)
        self.comboVideoAudioExts['state'] = 'readonly'
        self.comboVideoAudioExts.bind('<<ComboboxSelected>>', self.onVideoAudioExtsComboSelected)

        self.labelVideoAudioResolution = Label(master=frameVideoAudio, text="Resolutions : ")
        self.comboVideoAudioResolution = ttk.Combobox(master=frameVideoAudio)
        self.comboVideoAudioResolution['state'] = 'readonly'
        self.comboVideoAudioResolution.bind('<<ComboboxSelected>>', self.onVideoAudioResolutionComboSelected)

        self.labelVideoAudioFilesizes = Label(master=frameVideoAudio, text="File sizes : ")
        self.comboVideoAudioFilesizes = ttk.Combobox(master=frameVideoAudio)
        self.comboVideoAudioFilesizes['state'] = 'readonly'
        self.comboVideoAudioFilesizes.bind('<<ComboboxSelected>>', self.onVideoAudioFilesizesComboSelected)
        
        self.btnAudioExtract = Checkbutton (master=frameVideoAudio, text = "Extract Audio", variable = self.varExtractAudio, onvalue = True, offvalue = False, command=self.onCheckExtractAudio)
        self.varExtractAudio.set(False)
        
        self.comboAudioExtractExts = ttk.Combobox(master=frameVideoAudio)
        self.comboAudioExtractExts['state'] = 'readonly'
        self.comboAudioExtractExts['values'] = ['aac', 'flac', 'mp3', 'm4a', 'wav']
        self.comboAudioExtractExts.current(0)
        self.comboAudioExtractExts.bind('<<ComboboxSelected>>', self.onAudioExtractExtsComboSelected)
        self.comboAudioExtractExts['state'] = 'disabled'

        self.btnVideoAudioDownload = Button(master=frameVideoAudio, text="Download", command=self.onClickVideoAudioDownload)

        self.labelVideoAudioTitle.grid(row = 0, column = 0, columnspan=2, pady=10, padx=10)

        self.labelVideoAudioExts.grid(row = 1, column = 0, sticky=W, padx=10)
        self.comboVideoAudioExts.grid(row = 1, column = 1, sticky=E+W, pady=2, padx=10)

        self.labelVideoAudioResolution.grid(row = 2, column = 0, sticky=W, padx=10)
        self.comboVideoAudioResolution.grid(row = 2, column = 1, sticky=E+W, pady=2, padx=10)

        self.labelVideoAudioFilesizes.grid(row = 3, column = 0, sticky=W, padx=10)
        self.comboVideoAudioFilesizes.grid(row = 3, column = 1, sticky=E+W, pady=2, padx=10)

        self.btnAudioExtract.grid(row = 4, column = 0, sticky=W, padx=10)
        self.comboAudioExtractExts.grid(row = 4, column = 1, sticky=E+W, pady=2, padx=10)

        self.btnVideoAudioDownload.grid(row = 5, column = 1, sticky=E, pady=10, padx=10)

        return frameVideoAudio

    def createVideoAndAudioFrame(self, parent):
        frameVideoAndAudio = Frame(master=parent, style="BottomFrame.TFrame");  
        frameVideoAndAudio.rowconfigure(0, weight=1)
        frameVideoAndAudio.columnconfigure(0, weight=1)
        frameVideoAndAudio.columnconfigure(1, weight=1)
 
        self.frameVideo = self.createVideoOnlyFrame(frameVideoAndAudio)
        self.frameAudio = self.createAudioOnlyFrame(frameVideoAndAudio)
        self.frameMergeVideoAudio = self.createMergeVideoAudioFrame(frameVideoAndAudio)

        self.frameVideo.grid(row = 1, column = 0, sticky=N+S+E+W, pady=10, padx=10)
        self.frameAudio.grid(row = 1, column = 1, sticky=N+S+E+W, pady=10, padx=10)
        self.frameMergeVideoAudio.grid(row = 2, column = 0, columnspan=2, sticky=N+S+E+W, pady=10, padx=10)

        return frameVideoAndAudio

    def createVideoOnlyFrame(self, parent):
        frameVideo = Frame(master=parent, style="BottomFrame.TFrame");  
        frameVideo.columnconfigure(1, weight=1)

        self.labelVideoHeading = Label(master=frameVideo, text="Video Only");
        self.labelVideoExts = Label(master=frameVideo, text="Extensions : ");
        self.comboVideoExts = ttk.Combobox(master=frameVideo)
        self.comboVideoExts['state'] = 'readonly'
        self.comboVideoExts.bind('<<ComboboxSelected>>', self.onVideoExtsComboSelected)

        self.labelVideoResolution = Label(master=frameVideo, text="Resolutions : ");
        self.comboVideoResolution = ttk.Combobox(master=frameVideo)
        self.comboVideoResolution['state'] = 'readonly'
        self.comboVideoResolution.bind('<<ComboboxSelected>>', self.onVideoResolutionComboSelected)

        self.labelVideoFilesizes = Label(master=frameVideo, text="File sizes : ");
        self.comboVideoFilesizes = ttk.Combobox(master=frameVideo)
        self.comboVideoFilesizes['state'] = 'readonly'
        self.comboVideoFilesizes.bind('<<ComboboxSelected>>', self.onVideoFilesizesComboSelected)
        
        self.btnVideoDownload = Button(master=frameVideo, text="Download", command=self.onClickVideoDownload)

        self.labelVideoHeading.grid(row = 0, column = 0, columnspan=2, pady=10, padx=10)
        self.labelVideoExts.grid(row = 1, column = 0, sticky=W, padx=10)
        self.comboVideoExts.grid(row = 1, column = 1, sticky=E+W, pady=2, padx=10)
        self.labelVideoResolution.grid(row = 2, column = 0, sticky=W,  padx=10)
        self.comboVideoResolution.grid(row = 2, column = 1, sticky=E+W, pady=2, padx=10)
        self.labelVideoFilesizes.grid(row = 3, column = 0, sticky=W, padx=10)
        self.comboVideoFilesizes.grid(row = 3, column = 1, sticky=E+W, pady=2, padx=10)
        self.btnVideoDownload.grid(row = 4, column = 1, sticky=E, pady=10, padx=10)

        return frameVideo

    def createAudioOnlyFrame(self, parent):
        frameAudio = Frame(master=parent, style="BottomFrame.TFrame"); 
        frameAudio.rowconfigure(3, minsize=25)
        frameAudio.columnconfigure(1, weight=1)

        self.labelAudioHeading = Label(master=frameAudio, text="Audio Only");
        self.labelAudioExts = Label(master=frameAudio, text="Extensions : ");
        self.comboAudioExts = ttk.Combobox(master=frameAudio)
        self.comboAudioExts['state'] = 'readonly'
        self.comboAudioExts.bind('<<ComboboxSelected>>', self.onAudioExtsComboSelected)

        self.labelAudioFilesizes = Label(master=frameAudio, text="File sizes : ");
        self.comboAudioFilesizes = ttk.Combobox(master=frameAudio)
        self.comboAudioFilesizes['state'] = 'readonly'
        self.comboAudioFilesizes.bind('<<ComboboxSelected>>', self.onAudioFilesizesComboSelected)

        self.btnAudioDownload = Button(master=frameAudio, text="Download", command=self.onClickAudioDownload)

        self.labelAudioHeading.grid(row = 0, column = 0, columnspan=2, pady=10, padx=10)
        self.labelAudioExts.grid(row = 1, column = 0, sticky=W, padx=10)
        self.comboAudioExts.grid(row = 1, column = 1, sticky=E+W, pady=2, padx=10)
        self.labelAudioFilesizes.grid(row = 2, column = 0, sticky=W, padx=10)
        self.comboAudioFilesizes.grid(row = 2, column = 1, sticky=E+W, pady=2, padx=10)
        self.btnAudioDownload.grid(row = 4, column = 1, sticky=E, pady=10, padx=10)

        return frameAudio

    def createMergeVideoAudioFrame(self, parent):
        frameMergeVideoAudio = Frame(master=parent, style="BottomFrame.TFrame");  
        frameMergeVideoAudio.rowconfigure(0, weight=1)
        frameMergeVideoAudio.rowconfigure(1, weight=1)
        frameMergeVideoAudio.columnconfigure(3, weight=1)

        self.labelMergeHeading = Label(master=frameMergeVideoAudio, text="Download selected Video and Audio separately and Merge:");

        self.labelMergeExts = Label(master=frameMergeVideoAudio, text="Merge Exts : ");
        self.comboMergeExts = ttk.Combobox(master=frameMergeVideoAudio)
        self.comboMergeExts['state'] = 'readonly'
        self.comboMergeExts['values'] = ['mkv', 'mp4', 'ogg', 'webm', 'flv']
        self.comboMergeExts.current(0)
        self.comboMergeExts.bind('<<ComboboxSelected>>', self.onMergeExtsComboSelected)

        self.btnMergeKeepVideo = Checkbutton (master=frameMergeVideoAudio, text = "Keep each file", variable = self.varMergeKeepVideo, onvalue = True, offvalue = False)
        self.varMergeKeepVideo.set(True)
        self.btnMergeDownload = Button(master=frameMergeVideoAudio, text="Download and Merge", command=self.onClickMergeDownload)

        self.labelMergeHeading.grid(row = 0, column = 0, columnspan=4, sticky=E+W, pady=2, padx=10)
        self.labelMergeExts.grid(row = 1, column = 0, sticky=W, padx=10)
        self.comboMergeExts.grid(row = 1, column = 1, sticky=E+W, pady=2, padx=10)
        self.btnMergeKeepVideo.grid(row = 1, column = 2, sticky=E+W, pady=2, padx=2)
        self.btnMergeDownload.grid(row = 1, column = 3, ipadx=20,sticky=E, pady=10, padx=5)

        return frameMergeVideoAudio

    def onVideoAudioExtsComboSelected(self, event):
        ext = self.comboVideoAudioExts.get()
        res = self.video_info.getVideoResolutions(format_type="video+audio", ext=ext)
        self.comboVideoAudioResolution ['values'] = res
        self.comboVideoAudioResolution.current(0)

        file_sizes = self.video_info.getFileSizes(format_type="video+audio", ext=ext, resolution=res[0])
        self.comboVideoAudioFilesizes ['values'] = file_sizes
        self.comboVideoAudioFilesizes.current(0)

    def onVideoAudioResolutionComboSelected(self, event):
        ext = self.comboVideoAudioExts.get()
        res = self.comboVideoAudioResolution.get()
        file_sizes = self.video_info.getFileSizes(format_type="video+audio", ext=ext, resolution=res)
        self.comboVideoAudioFilesizes ['values'] = file_sizes
        self.comboVideoAudioFilesizes.current(0)

    def onVideoAudioFilesizesComboSelected(self, event):
        pass

    def onCheckExtractAudio(self):
        if self.varExtractAudio.get():
            self.comboAudioExtractExts['state'] = 'enabled'
            self.comboAudioExtractExts['state'] = 'readonly'
        else:
            self.comboAudioExtractExts['state'] = 'disabled'

    def onAudioExtractExtsComboSelected(self, event):
        pass

    def onClickVideoAudioDownload(self):
        ext = self.comboVideoAudioExts.get()
        file_size = self.comboVideoAudioFilesizes.get()
        format_id = self.video_info.getFileFormatId("video+audio", ext, file_size)

        extract_audio = self.varExtractAudio.get()
        extract_audio_ext = self.comboAudioExtractExts.get()

        if format_id is not None:
            self.downloadVideo(format_id=format_id, extract_audio=extract_audio, extract_audio_ext=extract_audio_ext)

    def onVideoExtsComboSelected(self, event):
        ext = self.comboVideoExts.get()
        res = self.video_info.getVideoResolutions(format_type="video", ext=ext)
        self.comboVideoResolution ['values'] = res
        self.comboVideoResolution.current(0)

        file_sizes = self.video_info.getFileSizes(format_type="video", ext=ext, resolution=res[0])
        self.comboVideoFilesizes ['values'] = file_sizes
        self.comboVideoFilesizes.current(0)

    def onVideoResolutionComboSelected(self, event):
        ext = self.comboVideoExts.get()
        res = self.comboVideoResolution.get()
        file_sizes = self.video_info.getFileSizes(format_type="video", ext=ext, resolution=res)
        self.comboVideoFilesizes ['values'] = file_sizes
        self.comboVideoFilesizes.current(0)

    def onVideoFilesizesComboSelected(self, event):
        pass

    def onClickVideoDownload(self):
        ext = self.comboVideoExts.get()
        file_size = self.comboVideoFilesizes.get()
        format_id = self.video_info.getFileFormatId("video", ext, file_size)
        if format_id is not None:
            self.downloadVideo(format_id)

    def onAudioExtsComboSelected(self, event):
        ext = self.comboAudioExts.get()
        file_sizes = self.video_info.getFileSizes(format_type="audio", ext=ext)
        self.comboAudioFilesizes ['values'] = file_sizes
        self.comboAudioFilesizes.current(0)

    def onAudioFilesizesComboSelected(self, event):
        pass

    def onClickAudioDownload(self):
        ext = self.comboAudioExts.get()
        file_size = self.comboAudioFilesizes.get()
        format_id = self.video_info.getFileFormatId("audio", ext, file_size)
        if format_id is not None:
            self.downloadVideo(format_id=format_id, subtitles=False)

    def onMergeExtsComboSelected(self, event):
        pass

    def onClickMergeDownload(self):
        merge_ext = self.comboMergeExts.get()
        keep_video = self.varMergeKeepVideo.get()

        video_ext = self.comboVideoExts.get()
        video_file_size = self.comboVideoFilesizes.get()
        video_format_id = self.video_info.getFileFormatId("video", video_ext, video_file_size)
        
        audio_ext = self.comboAudioExts.get()
        audio_file_size = self.comboAudioFilesizes.get()
        audio_format_id = self.video_info.getFileFormatId("audio", audio_ext, audio_file_size)

        if video_format_id is not None and audio_format_id:
            self.downloadVideo(video_format_id, audio_format_id, merge_ext, keep_video)

    def ResetCombos(self):
        self.btnVideoAudioDownload['state'] = 'disabled'
        self.btnVideoDownload['state'] = 'disabled'
        self.btnAudioDownload['state'] = 'disabled'
        self.btnMergeDownload['state'] = 'disabled'
        self.comboVideoAudioExts['values'] = []
        self.comboVideoAudioExts.set('')
        self.comboVideoAudioResolution['values'] = []
        self.comboVideoAudioResolution.set('')
        self.comboVideoAudioFilesizes['values'] = []
        self.comboVideoAudioFilesizes.set('')
        self.comboVideoExts['values'] = []
        self.comboVideoExts.set('')
        self.comboVideoResolution['values'] = []
        self.comboVideoResolution.set('')
        self.comboVideoFilesizes['values'] = []
        self.comboVideoFilesizes.set('')
        self.comboAudioExts['values'] = []
        self.comboAudioExts.set('')
        self.comboAudioFilesizes['values'] = []
        self.comboAudioFilesizes.set('')

    def FillCombos(self):
        exts = self.video_info.getExtenisons(format_type="video+audio")
        self.comboVideoAudioExts ['values'] = exts

        if(len(exts)):
            self.comboVideoAudioExts.current(0)
            res = self.video_info.getVideoResolutions(format_type="video+audio", ext=exts[0])
            self.comboVideoAudioResolution ['values'] = res
            self.comboVideoAudioResolution.current(0)

            file_sizes = self.video_info.getFileSizes(format_type="video+audio", ext=exts[0], resolution=res[0])
            self.comboVideoAudioFilesizes ['values'] = file_sizes
            self.comboVideoAudioFilesizes.current(0)

            self.btnVideoAudioDownload['state'] = 'enabled'

        exts = self.video_info.getExtenisons(format_type="video")
        self.comboVideoExts ['values'] = exts

        if(len(exts)):
            self.comboVideoExts.current(0)
            res = self.video_info.getVideoResolutions(format_type="video", ext=exts[0])
            self.comboVideoResolution ['values'] = res
            self.comboVideoResolution.current(0)

            file_sizes = self.video_info.getFileSizes(format_type="video", ext=exts[0], resolution=res[0])
            self.comboVideoFilesizes ['values'] = file_sizes
            self.comboVideoFilesizes.current(0)
            self.btnVideoDownload['state'] = 'enabled'

        exts = self.video_info.getExtenisons(format_type="audio")
        self.comboAudioExts ['values'] = exts

        if(len(exts)):
            self.comboAudioExts.current(0)
            file_sizes = self.video_info.getFileSizes(format_type="audio", ext=exts[0])
            self.comboAudioFilesizes ['values'] = file_sizes
            self.comboAudioFilesizes.current(0)
            self.btnAudioDownload['state'] = 'enabled'

        if self.btnVideoDownload['state'] == 'enabled' and  self.btnAudioDownload['state'] == 'enabled':
            self.btnMergeDownload['state'] = 'enabled'

    def onClickOutputDirBrowseBtn(self):
        oldDir = self.varOutputDir.get().strip()
        dirPath = filedialog.askdirectory(initialdir=oldDir)
        if dirPath:
            dirPath = os.path.normpath(dirPath)
            self.varOutputDir.set(dirPath);

    def getVideoInformation(self,url):
        ydl_opts = {
         'logger': MyLogger(self.textConsole)
        }        
        self.config(cursor="wait")
        SetConsoleText(self.textConsole, "")
        result = None
        try:
            with youtube_dl.YoutubeDL(params=ydl_opts) as ydl:
                result = ydl.extract_info(url, download=False) # We just want to extract the info
        except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError) as e:
                pass

        self.config(cursor="")
        return result

    def downloadVideo(self, format_id, audio_id=None, merge_ext=None, keep_video=False, extract_audio=False, extract_audio_ext=None, subtitles=True):
        out_dir = self.varOutputDir.get()
        url = self.varURL.get()
        out_file = os.path.join(out_dir, "%(title)s-%(filesize)s.%(ext)s")
        if audio_id is not None:
            format_id = '%s+%s'%(format_id,audio_id)

        ydl_opts = {
            'format': format_id,
            'outtmpl': out_file,
            'noplaylist' : True,
            'progress_hooks': [],
            'logger': MyLogger(self.textConsole)
        }

        if subtitles:
            ydl_opts['writesubtitles'] = subtitles

        if extract_audio and extract_audio_ext is not None:
            ydl_opts['postprocessors'] = [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': extract_audio_ext,
                        'preferredquality': '192',
                        'nopostoverwrites': 'True',
                    }
                ]
            ydl_opts['keepvideo'] = True

        if merge_ext is not None:
            ydl_opts['merge_output_format'] = merge_ext
            ydl_opts['keepvideo'] = keep_video

        self.config(cursor="wait")
        SetConsoleText(self.textConsole, "")
        try:
            with youtube_dl.YoutubeDL(params=ydl_opts) as ydl:
                ydl.download([url])
        except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError) as e:
            pass
        self.config(cursor="")

    def my_hook(self, progress):
        pass

    def OnURLGetVideoInfoBtn(self):
        v_info = None
        url = self.varURL.get().strip()
        if url != "":
            v_info = self.getVideoInformation(url)
        else:
            SetConsoleText(self.textConsole, 'Paste youtube url and click "Get Video Info" button')

        if v_info is not None:
            self.video_info = VideoInfo(v_info)
            self.varVideoTitle.set("Video Title : " + self.video_info.title)
            '''
            format_ids, format_strs = self.video_info.getAvailableFormats();
            for i in range(len(format_ids)):
                print(format_ids[i], format_strs[i])
            '''
            self.FillCombos()
            SetConsoleText(self.textConsole, 'Select file extension, resolution, file size and download')
        else:
            self.ResetCombos()

def OnQuit(top):
    top.WriteINIFile()
    root.destroy()

if (__name__ == "__main__"):
    root = Tk();
    #Set Window Title
    root.wm_title("Youtube Downloader");
    #Set Window Size
    root.geometry('500x300+100+100')

    #Disable resizing of window
    #root.resizable(width=FALSE, height=FALSE);
    root.minsize(800, 530);
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # create a frame
    top = MainGUI(root);
    top.update();

    #Run and listen for events
    # make the top right close button minimize (iconify) the main window
    cmd = lambda t = top : OnQuit(t);  
    root.protocol("WM_DELETE_WINDOW", cmd) #master.iconify

    root.mainloop();
