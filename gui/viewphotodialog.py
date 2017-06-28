# -*- coding: utf-8 -*-

"""
***************************************************************************
    viewphotodialog.py
    ---------------------
    begin                : 2017-02-08
    git sha              : $Format:%H$
    copyright            : Copyright (c)  2017 MATSUE REKISHIKAN
    email                : pica.hayashi@gmail.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Hirofumi Hayashi(osgeo.jp)'
__date__ = 'January 2017'
__copyright__ = 'Copyright (c)  2017 MATSUE REKISHIKAN'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import QEvent,Qt
from PyQt4.QtGui import QDialog, QPixmap,QPrinter,QPainter,QPrintDialog, QAction, QMenu

from GkukanMusiumdb.ui.ui_viewphotodialogbase import Ui_Dialog

import GkukanMusiumdb.resources_rc


class ViewPhotoDialog(QDialog, Ui_Dialog):
    def __init__(self, path, parent=None):
        super(ViewPhotoDialog, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)

        self.printer = QPrinter()
        self.scaleFactor = 1.0

        self.createActions()
        self.createMenus()

        photo = QPixmap(path)
        self.lblPhoto.setPixmap(photo)
        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)

        self.updateActions()

        if not self.fitToWindowAct.isChecked():
            self.lblPhoto.adjustSize()
        
        self.fitToWindowAct.setChecked(True)
        self.fitToWindow()


    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.lblPhoto.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.lblPhoto.pixmap().rect())
            painter.drawPixmap(0, 0, self.lblPhoto.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.lblPhoto.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def createActions(self):
        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)


    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.viewMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())


    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.lblPhoto.resize(self.scaleFactor * self.lblPhoto.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))

