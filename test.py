# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 10:20:48 2018

Desktop GUI (wxpython based) Demo tool for displaying video alongwith frame-wise ML results

Takes images from a recording and plays video with a set frame rate (handles problems like flicker etc.)

@author: uidn1039
"""
import wx
import os
import imghdr
import timeit
import time
from natsort import natsorted
import threading
import numpy as np
from queue import Queue


class DemodataAssoc(wx.Frame):

    def __init__(self, parent, title):
        super(DemodataAssoc, self).__init__(parent, title=title, size=(500, 500))
        self.InitUI()
        self.Centre()
        self.Show()


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


    def OnQuit(self, event):
        self.Close()


    def OnPlay(self, e):
        print("Inside OnPlay")
        self.panel.Bind(wx.EVT_PAINT,self.PlayImages)
        self.panel.Refresh(eraseBackground=False)  # Add eraseBackground=False to avoid flickering when you replay video


    def OnOpen(self, event):
        currentdir= os.getcwd()
        with wx.DirDialog(None, "Choose a directory:",defaultPath = currentdir,style=wx.DD_DEFAULT_STYLE) as folderDialog:

            if folderDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

        # Proceed loading the file chosen by the user
            rootpathname = folderDialog.GetPath()
            print(rootpathname)
            listofdirs=os.listdir(rootpathname)  # returns the current directory
            self.pathofdirs=[]
            for dirname in listofdirs:
                self.pathofdirs.append(rootpathname+"\\"+dirname)
            self.listoffiles=np.array([])
            dircount=0
            maxdircount=len(listofdirs)

            for subdir in self.pathofdirs:
                dircount=dircount+1
                self.filelist=natsorted(os.listdir(subdir))  # the images from the folder is loaded
                self.interm = np.array(self.filelist)
                print(self.filelist)
                self.listoffiles = np.concatenate((self.listoffiles, self.interm))  # the images are appended to a np.array....... to buffer
                print("***********")

                if self.filelist:
                    # to check if the images loaded are ".jpeg" files
                    if imghdr.what(subdir+"\\"+self.filelist[0])!='jpeg':
                        print("Log: Invalid Image file")
                        break
                    elif dircount == maxdircount:
                        print("trying LoadImages")
                        self.panel.Bind(wx.EVT_PAINT, self.LoadImages)
                        self.panel.Refresh()
                else:
                    print("Log: No image files in directory")
                    break


    def OnStop(self, e):
        print("stop")
        self.Stop=1
        self.another_flag = 0


    def OnPause(self, e):
        print("Pause")
        self.Pause = 1


    def LoadImages(self, e):
        print("Done")
        self.bmpImgFrames=[]
        for x in self.listoffiles:
            start_time = timeit.default_timer()
            filepath = self.pathofdirs[0]+"\\"+x
            self.bmpImgFrames.append(wx.Bitmap(filepath))

        start_time = timeit.default_timer()
        self.dc = wx.PaintDC(self.panel)
        self.dc.Clear()
        self.dc.DrawBitmap(self.bmpImgFrames[0], 0, 0, True)

        # code you want to evaluate
        elapsed = timeit.default_timer() - start_time
        print(elapsed)


    def to_thread_vid(self, e):
        itrn = 0
        start_time_init = timeit.default_timer()
        listlen=len(self.listoffiles)
        itr = 0
        if self.another_flag == 1:
            itr = self.itrn1

        while True:
            itrn += 1
            itr += 1
            start_time = timeit.default_timer()
            self.dc.DrawBitmap(self.bmpImgFrames[itrn], 0, 0, True)

            elapsed = timeit.default_timer() - start_time
            framedelay = 0.06-elapsed
            time.sleep(framedelay)

            # the pause function
            if self.Stop == 1:
                self.Stop = 0
                break

            # the Pause function  defined
            elif self.Pause == 1:
                print("in pause")
                self.another_flag = 1
                self.itrn1 = itrn
                while self.Pause == 1:
                    self.dc.DrawBitmap(self.bmpImgFrames[self.itrn1], 0, 0, True)
                    if self.Stop == 1:
                        break

            elif itrn == listlen-1:
                break

        self.Pause = 0
        print(timeit.default_timer() - start_time_init)


    def PlayImages(self,event):
        if self.Pause == 1:  # to play if the video is paused
            self.Pause = 0
        else:                # main play images function
            self.Pause = 0
            print("Done")
            self.dc = wx.PaintDC(self.panel)
            self.dc.Clear()

            #to thread the playing video
            lock = threading.Lock()
            lock.acquire(True) # locking the thead
            print("after acquiring lock",lock.locked())
            t0_vid = threading.Thread(target=self.to_thread_vid, args=(event,))
            t0_vid.setDaemon(True)
            t0_vid.start()
            lock.release()  # releasing the lock for the thread
            print("after release",lock.locked())


if __name__== "__main__":
  app=wx.App()
  DemodataAssoc(None,title='Curve Entry Detection')
  app.MainLoop()