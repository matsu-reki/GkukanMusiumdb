# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/viewphotodialogbase.ui'
#
# Created: Mon Mar  9 18:56:53 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(500, 400)

        self.menuBar=QtGui.QMenuBar()
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))

        self.verticalLayout.addWidget(self.menuBar)

        self.lblPhoto = QtGui.QLabel()
        self.lblPhoto.setBackgroundRole(QtGui.QPalette.Base)
        self.lblPhoto.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.lblPhoto.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.lblPhoto)
#        self.setCentralWidget(self.scrollArea)

        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
#     def setupUi2(self, Dialog):
#         Dialog.setObjectName(_fromUtf8("Dialog"))
#         Dialog.resize(400, 300)
#         self.verticalLayout = QtGui.QVBoxLayout(Dialog)
#         self.verticalLayout.setSpacing(2)
#         self.verticalLayout.setMargin(0)
#         self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
# 
#         self.menuBar=QtGui.QMenuBar()
#         self.menuBar.setObjectName(_fromUtf8("menuBar"))
#         self.verticalLayout.addWidget(self.menuBar)
# 
#         self.scrollArea = QtGui.QScrollArea(Dialog)
#         self.scrollArea.setWidgetResizable(True)
#         self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
#         self.scrollAreaWidgetContents = QtGui.QWidget()
#         self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 396, 296))
#         self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
#         self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
#         
#         self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
#         self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
#         self.lblPhoto = QtGui.QLabel(self.scrollAreaWidgetContents)
#         self.lblPhoto.setText(_fromUtf8(""))
#         self.lblPhoto.setObjectName(_fromUtf8("lblPhoto"))
#         self.lblPhoto = QtGui.QLabel()
#         self.lblPhoto.setBackgroundRole(QtGui.QPalette.Base)
#         self.lblPhoto.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
#         self.lblPhoto.setScaledContents(True)
#         self.verticalLayout_2.addWidget(self.lblPhoto)
# 
#         self.scrollArea.setWidget(self.scrollAreaWidgetContents)
#         self.verticalLayout.addWidget(self.scrollArea)
# 
#         self.retranslateUi(Dialog)
#         QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "View photo", None))

