# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GkukanMusiumdbDockWidget
                                 A QGIS plugin
 Matsue G-Kukan Musium Databse edhitor
                             -------------------
    begin                : 2017-02-08
    git sha              : $Format:%H$
    copyright            : Copyright (c)  2017 MATSUE REKISHIKAN
    email                : pica.hayashi@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
__author__ = 'Hirofumi Hayashi(osgeo.jp)'
__date__ = 'January 2017'
__copyright__ = 'Copyright (c)  2017 MATSUE REKISHIKAN'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal, Qt, QSettings
from PyQt4.QtGui import QDockWidget, QMessageBox, QPixmap, QIcon, QFileDialog, QImageReader, QStandardItemModel, QStandardItem, QItemSelectionModel,QBrush, QColor,QTableWidgetItem,QTableWidget
from PyQt4.QtSql import QSqlDatabase, QSqlQuery
from qgis.core import *
from qgis.gui import *
from PhotoData import PhotoData
from GkukanMusiumdb.gui.landmarktoolbox import *
from GkukanMusiumdb.gui.viewphotodialog import ViewPhotoDialog
import binascii


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gkukanmusiumdb_dockwidget_base.ui'))


class ImgWidget(QtGui.QLabel):

    def __init__(self,imagePath,thumpath, parent=None):
        super(ImgWidget, self).__init__(parent)
        self.imagePath=imagePath
        self.picture = self.thumbnailPhoto(imagePath,thumpath)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(10, 0, self.picture)

    def thumbnailPhoto(self,imagePath,tp):

        if os.path.exists(tp) :
            return QPixmap(tp)
        else :
            if os.path.exists(os.path.dirname(tp)) == False:
                os.mkdir(os.path.dirname(tp))
            pixmap=QPixmap(imagePath).scaled(800, 600).scaled(75, 50, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            a=pixmap.save(tp, 'PNG')
            return pixmap



class GkukanMusiumdbDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    GKukanMusiumMessage = pyqtSignal(unicode, int)

    def __init__(self, iface,land, parent=None):
        """Constructor."""
        super(GkukanMusiumdbDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.loadListCount=0
        self.loadmax=self.tblPhotos.columnCount()
        self.tblPhotos.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.iface = iface
        self.land=land #Landmark toolbox
        self.canvas = self.iface.mapCanvas()
        self.geoCrs = QgsCoordinateReferenceSystem(4326)

        self.db = QSqlDatabase.addDatabase('QPSQL')
        self.photolist=[]

        self.filtermode=False
        self.btnReloadphoto.clicked.connect(self.FilterMode)
        self.btnLoadMorePhoto.clicked.connect(self.AddMorePhotosToList)
        self.btnSetLandmark.clicked.connect(self.AddSelectiontoLandmark)
        self.btnClearSelection.clicked.connect(self.ClearSelection)
        self.btnSetToPoint.clicked.connect(self.SetPointToSelection)

        self.tblPhotos.cellDoubleClicked.connect(self.clickPhoto)
        

        self.btnLoadMorePhoto.setEnabled(False)
        self.btnSetLandmark.setEnabled(False)
        self.btnSetToPoint.setEnabled(False)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
        
    def clickPhoto(self,r,c):
        tbl =self.tblPhotos
        p=tbl.item(1,c)
        
        if hasattr(p, 'data')==False:
            return

        
        a=p.data(32)
        
        if not a :
            return

        if r==0 or (a.lon == 0 and a.lat == 0):
            dlg = ViewPhotoDialog(a.filePath)
            dlg.exec_()
            return

        point=self._transformPoint(QgsPoint(a.lon, a.lat))
        self.canvas.freeze(True)
        self.canvas.setCenter(point)
        self.canvas.freeze(False)
        self.canvas.refresh()


    def SetPointToSelection(self):
        pass
        if  self._checkLoadLayer() ==False:
            return

        tbl =self.tblPhotos
        if len(tbl.selectedItems())==0:
            return
        
        pl=[]
        for p in tbl.selectedItems():
            a=p.data(32)
            if a is not None :
                pl.append(a)

        if self.AskUpdatePoint(pl) is False:
            return
        
        if len(pl):
            self.canvas.freeze(True)
            self.SetPhotoPosition(pl,self.canvas.center())
            self.canvas.freeze(False)
            self.canvas.refresh()

            i=0
            for p in tbl.selectedItems():
                if p.row()==1 :
                    p.setBackground(QBrush(QColor('#FFFFFF')))


        
    def AskUpdatePoint(self,pl):
        
        i=False
        for p in pl:
            if  p.lat  :
                if p.lon :
                    i=True

        if i :
            reply = QtGui.QMessageBox.question(self, u'位置情報変更の確認',u"画像に紐づく位置情報を変更してもよろしいですか?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                return True
            else:
                return False
        else :
                return True




        
    def AddSelectiontoLandmark(self):
    
        if self.loadListCount == 0 :
            return
        
        tbl =self.tblPhotos
        if len(tbl.selectedItems())==0:
            return

        lid=self.land.toolbox.getLandmarkID()

        if lid is None:
            return

        pl=[]
        for p in tbl.selectedItems():
            a=p.data(32)
            if a is not None :
                pl.append(a)

        if self.AskUpdateLandmark(lid,pl) is False:
            return
        
        if len(pl):
            if self.SetLandMarkID(lid,pl) :
                self.land.toolbox._highlightLandmark()
                self.land.toolbox.populatePhotos()
            
        

    def AskUpdateLandmark(self,lid,pl):
        
        i=False
        for p in pl:
            if  p.landmark_id  :
                if p.landmark_id <> lid :
                    i=True

        if i :
            reply = QtGui.QMessageBox.question(self, u'史料情報変更の確認',u"画像に紐づく史料情報を変更してもよろしいですか?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                return True
            else:
                return False
        else :
                return True


    
    def FilterMode(self):
        self.filtermode=self.FilterNoEdit.isChecked()
        self.ResetTable()
        self.AddPhotosToList()
        self.btnLoadMorePhoto.setEnabled(True)
        self.btnSetLandmark.setEnabled(True)
        self.btnSetToPoint.setEnabled(True)


    def ResetTable(self):

        self.tblPhotos.clear()

        del self.photolist[:]

        self.loadListCount=0
        self.tblPhotos.setColumnCount(20)
        self.tblPhotos.setBackgroundRole(QtGui.QPalette.Dark)
        self.loadmax=self.tblPhotos.columnCount()
        self.tblPhotos.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)


    def ScrollTableLeft(self):
        tbl=self.tblPhotos
        tbl.setColumnCount(self.loadListCount+5)
        self.LoadMorePhotoThread(5)

    def LoadPhotosToList(self):
        self.loadListCount=0
        self.AddPhotosToList()

    def AddMorePhotosToList(self):

        oldst=self.loadListCount
        n=100

        QApplication.setOverrideCursor(Qt.WaitCursor)
        if not self.GetPhotosList( self.loadListCount+1,self.loadListCount+n):
            QApplication.restoreOverrideCursor()
            return
        
        tbl=self.tblPhotos
        tbl.verticalHeader().resizeSection(0,50)

        for i in range(oldst,self.loadListCount) :
            fn=os.path.join(self.folderpath,self.photolist[i].filename)
            self.photolist[i].filePath=fn
            tp=os.path.join(os.path.join(self.folderpath,'thumb'),str(self.photolist[i].p_id)+'.png')
            self.photolist[i].thumbPath=tp
            item=ImgWidget(fn,tp,self)
            hd=QTableWidgetItem(str(self.photolist[i].p_id))
            tbl.insertColumn(i)
            tbl.setHorizontalHeaderItem(i,hd)
            tbl.setCellWidget(0,i,item)
            b=QtGui.QTableWidgetItem(self.photolist[i].filename)
            b.setData(32,self.photolist[i])
            tbl.setItem(1,i, b)
            if self.photolist[i].lon==0 and self.photolist[i].lat==0:
                tbl.item(1,i).setBackground(QBrush(QColor('#CCFFFF')))
            if self.photolist[i].keywords :
                tbl.setItem(2,i, QtGui.QTableWidgetItem(self.photolist[i].keywords))

            QgsMessageLog.logMessage(u"LoadPhoto..." + str(i), tag="LoadMorePhotoThread", level=QgsMessageLog.INFO )

        QApplication.restoreOverrideCursor()


    def AddPhotosToList(self):

        oldst=self.loadListCount
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        if not self.GetPhotosList( self.loadListCount+1,self.loadListCount+self.loadmax):
            QApplication.restoreOverrideCursor()
            return
        
        
        tbl=self.tblPhotos
        tbl.verticalHeader().resizeSection(0,50)

        self.ClearTableCells()
        
        for i in range(oldst,self.loadListCount) :
            fn=os.path.join(self.folderpath,self.photolist[i].filename)
            self.photolist[i].filePath=fn
            tp=os.path.join(os.path.join(self.folderpath,'thumb'),str(self.photolist[i].p_id)+'.png')
            self.photolist[i].thumbPath=tp
            item=ImgWidget(fn,tp,self)
            pos=i-oldst
            hd=QTableWidgetItem(str(i+1))
            tbl.setHorizontalHeaderItem(pos,hd)
            tbl.setCellWidget(0,pos,item)
            b=QtGui.QTableWidgetItem(self.photolist[i].filename)
            b.setData(32,self.photolist[i])
            tbl.setItem(1,i, b)
            
            if self.photolist[i].lon==0 and self.photolist[i].lat==0:
                tbl.item(1,i).setBackground(QBrush(QColor('#CCFFFF')))

            if self.photolist[i].keywords :
                tbl.setItem(2,pos, QtGui.QTableWidgetItem(self.photolist[i].keywords))

            QgsMessageLog.logMessage(u"LoadPhoto..." + str(i), tag="LoadPhotoThread", level=QgsMessageLog.INFO )

        QApplication.restoreOverrideCursor()


    def ClearSelection(self):

        tbl =self.tblPhotos
        if len(tbl.selectedItems())==0:
            return

        tbl.selectionModel().clearSelection()

    def ClearTableCells(self):
            tbl=self.tblPhotos
            tbl.clear()

    def openDatabase(self):
        if self.db.isValid():
            settings = QSettings('MatsueGkukan', 'Gkukandb')
            dbHostName = settings.value('hostname')
            dbDatabaseName = settings.value('databasename')
            dbUserName = settings.value('username')
            dbPassword = settings.value('dbpassword')

            self.db.setHostName(dbHostName);
            self.db.setDatabaseName(dbDatabaseName);
            self.db.setUserName(dbUserName);
            self.db.setPassword(dbPassword);

            if not self.db.open():
                self.GKukanMusiumMessage.emit(self.tr('Can not open GKukanMusium database'), QgsMessageBar.WARNING)
                return False

            self.query = QSqlQuery(self.db)
            return True
        else:
            settings = QSettings('MatsueGkukan', 'Gkukandb')
            dbHostName = settings.value('hostname')
            dbDatabaseName = settings.value('databasename')
            dbUserName = settings.value('username')
            dbPassword = settings.value('dbpassword')

            self.db.removeDatabase(dbDatabaseName)
            del self.db
            self.db = None
            self.db = QSqlDatabase.addDatabase('QPSQL')

            self.db.setHostName(dbHostName);
            self.db.setDatabaseName(dbDatabaseName);
            self.db.setUserName(dbUserName);
            self.db.setPassword(dbPassword);

            if not self.db.open():
                self.GKukanMusiumMessage.emit(self.tr('Can not open GKukanMusium database'), QgsMessageBar.WARNING)
                return False

            self.query = QSqlQuery(self.db)
            return True

        return False
    
    def GetPhotoFolderPath(self):
        if not self.openDatabase():
            return False

        if self.query.exec_(u'select * from m_folder'):
            self.query.first()
            self.folderpath=self.query.value(2)
            ret= self.folderpath
        else:
            ret= ''
            
        self.db.close()

        return ret

    def GetPhotosList(self,st,ed):
        folder=self.GetPhotoFolderPath()

        if not self.openDatabase():
            return False

        l=ed-st+1
        if self.filtermode:
            sql=u'select * from (select row_number() over() as rid, * from t_photo  where t_photo.lat=0 and t_photo.lon=0 order by p_id) as p where (p.rid between %s and %s ) limit %s;' % (str(st),str(ed),str(l))
        else :
            sql=u'select * from (select row_number() over() as rid, * from t_photo order by p_id) as p where p.rid between %s and %s  limit %s;' % (str(st),str(ed),str(l))
        
        if self.query.exec_(sql):
            self.query.first()
            
            for i in range(self.query.size()):
                v=self.query.value
                self.photolist.append(PhotoData(v(1),v(2),v(3),v(4),v(5),v(6),v(7),v(8),v(9),v(10),v(11),v(12),v(13),v(14),v(15),v(16),v(17),v(18),v(19),v(20),v(21),v(22)) )
                self.query.next()
            
            self.loadListCount+=self.query.size()
            self.query.clear()
            self.db.close()
            return True
        else:
            self.db.close()
            return False
        
        
    def SetLandMarkID(self,lid,pl):

        if not len(pl):
            return False

        if not self.openDatabase():
            return False

        a=[]
        for p in pl:
            a.append(p.p_id)

        sp=",".join(map(str,a))
        sql=u'UPDATE t_photo SET landmark_id=%s WHERE p_id in (%s);' % (str(lid),str(sp))
        print sql
        if self.query.exec_(sql):
            self.query.clear()
            self.db.close()
        else:
            self.db.close()
            return False
        
        return True

    def SetPhotoPosition(self,pl,pos):

        if not len(pl):
            return False

        a=[]
        for p in pl:
            a.append(p.p_id)

        sp=",".join(map(str,a))
        pos=self._transformMapToPoint(pos)

        geom=QgsGeometry.fromPoint(pos)
        x=geom.asQPointF().x()
        y=geom.asQPointF().y()
        gt= "'" + geom.exportToWkt() + "'"
        sql=u'UPDATE t_photo SET lon=%s,lat=%s,geom=ST_GeomFromText(%s,4326) WHERE p_id in (%s);' % (str(x),str(y),gt,str(sp))
        
        v=self.convertGeomFromPostGis(geom)
        
        self.updatePhotoDataXY(a,x,y,v)

        if not self.openDatabase():
            return False

        if self.query.exec_(sql):
            self.query.clear()
            self.db.close()
        else:
            a= self.query.lastError().text()
            self.db.close()
            return False
        
        return True

    def updatePhotoDataXY(self,pl,x,y,v):
        pass
        pp=self.photolist
        
        for i in range(len(pp)):
            if pp[i].p_id in pl :
                self.photolist[i].x=x
                self.photolist[i].y=y
                self.photolist[i].geom=v
        
        return

    def decodeBinary(self, wkb):
        """Decode the binary wkb and return as a hex string"""
        value = binascii.a2b_hex(wkb)
        value = value[::-1]
        value = binascii.b2a_hex(value)
        return value


    def _checkLoadLayer(self):
        pass

        return True
        
    def _transformMapToPoint(self, pnt):
        crsDest = self.canvas.mapSettings().destinationCrs()
        xform = QgsCoordinateTransform(crsDest,self.geoCrs)
        p2 = xform.transform(pnt)
        return p2

    def _transformPoint(self, pnt):
        crsDest = self.canvas.mapSettings().destinationCrs()
        xform = QgsCoordinateTransform(self.geoCrs, crsDest)
        p2 = xform.transform(pnt)
        return p2

    def convertGeomFromPostGis(self,geom):
        if not self.openDatabase():
            return None
        
        gt= "'" + geom.exportToWkt() + "'"
        sql=u'SELECT ST_GeomFromText(%s,4326);' % (gt)

        if self.query.exec_(sql):
            self.query.first()
            v=self.query.value
            self.db.close()
            
            return v

        else:
            a= self.query.lastError().text()
            self.db.close()
            return False
