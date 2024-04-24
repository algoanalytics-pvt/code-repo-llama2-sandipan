#!/usr/bin/python3

# importing required libraries
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys
 
# creating main window class
class MainWindow(QMainWindow):
 
    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
 
 
        # creating a QWebEngineView
        self.browser = QWebEngineView()
 
        # setting default browser url as google
        self.browser.setUrl(QUrl("http://localhost:3050/"))

        self.setWindowIcon(QIcon(QPixmap("aksha_desktop_logo.png")))
 
        # adding action when url get changed
        self.browser.urlChanged.connect(self.update_urlbar)
 
        # adding action when loading is finished
        self.browser.loadFinished.connect(self.update_title)
 
        # set this browser as central widget or main window
        self.setCentralWidget(self.browser)
 
        # creating a status bar object
        self.status = QStatusBar()
 
        # adding status bar to the main window
        self.setStatusBar(self.status)

        # showing all the components
        self.showMaximized()
 
 
    # method for updating the title of the window
    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle("AKSHA(अक्ष)-Powered by AlgoAnalytics Pvt.Ltd") #% title
 
 
    # method called by the home action
    def navigate_home(self):
 
        # open the google
        self.browser.setUrl(QUrl("http://localhost:3050/"))
 
    # method called by the line edit when return key is pressed
    def navigate_to_url(self):
 
        # getting url and converting it to QUrl object
        q = QUrl(self.urlbar.text())
 
        # if url is scheme is blank
        if q.scheme() == "":
            # set url scheme to html
            q.setScheme("http")
 
        # set the url to the browser
        self.browser.setUrl(q)
 
    # method for updating url
    # this method is called by the QWebEngineView object
    def update_urlbar(self, q):
 
        # setting text to the url bar
        self.urlbar.setText(q.toString())
 
        # setting cursor position of the url bar
        self.urlbar.setCursorPosition(0)
 
 
# creating a pyQt5 application
app = QApplication(sys.argv)
 
# setting name to the application
app.setApplicationName("AKSHA")
# app.setWindowIcon("/home/aapl19/Aksha/Aksha_browser/aksha_desktop_logo.png")
 
# creating a main window object
window = MainWindow()
 
# loop
app.exec_()