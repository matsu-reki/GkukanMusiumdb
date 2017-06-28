# -*- coding: utf-8 -*-

"""
***************************************************************************
    textedit.py
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

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import QTextEdit

class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self)

        self.placeholderText = None

    def setPlaceholderText(self, text):
        self.placeholderText = text
        if self.toPlainText() == '':
            self.setHtml('<font color="#808080">%s</font>' % text)

    def focusInEvent(self, event):
        if self.placeholderText is not None:
            t = self.toPlainText()
            if t == '' or t == self.placeholderText:
                self.clear()

        QTextEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        if self.placeholderText is not None:
            if self.toPlainText() == '':
                self.setHtml('<font color="#808080">%s</font>' % self.placeholderText)

        QTextEdit.focusOutEvent(self, event)
