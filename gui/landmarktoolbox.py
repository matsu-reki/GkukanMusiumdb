# -*- coding: utf-8 -*-

"""
***************************************************************************
    landmarktoolbox.py
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

import shutil

from PyQt4.QtCore import pyqtSignal, Qt, QSettings, QFileInfo, QDateTime
from PyQt4.QtGui import QDockWidget, QPixmap, QApplication, QIcon, QFileDialog, QImageReader, QStandardItemModel, QStandardItem, QItemSelectionModel, QColor
from PyQt4.QtSql import QSqlDatabase, QSqlQuery

from qgis.core import * #QgsProject, QGis, NULL
from qgis.gui import * #QgsMessageBar, QgsMapLayerProxyModel, QgsHighlight

from GkukanMusiumdb.exifpy import exifread

from GkukanMusiumdb.gui.viewphotodialog import ViewPhotoDialog
from GkukanMusiumdb.csvunicode import UnicodeReader, UnicodeWriter

from GkukanMusiumdb.ui.ui_landmarktoolboxbase import Ui_DockWidget

import GkukanMusiumdb.resources_rc


class LandmarkToolbox(QDockWidget, Ui_DockWidget):
    landmarkMessage = pyqtSignal(unicode, int)

    def __init__(self, iface):
        QDockWidget.__init__(self)
        self.setupUi(self)

        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.geoCrs = QgsCoordinateReferenceSystem(4326)

        self.btnAddPhoto.setIcon(QIcon(':/icons/camera.svg'))

        self.txtPhotoComment.setPlaceholderText(self.tr('Comment'))
        self.cmbLayers.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.db = QSqlDatabase.addDatabase('QPSQL')
        self.landmarkId = None
        self.photoId = None
        self.highlight = None

        self.model = QStandardItemModel()
        self.lstPhotos.setModel(self.model)

        self.btnUpdateLandmark.clicked.connect(self.saveLandmark)
        self.btnDeleteLandmark.clicked.connect(self.deleteLandmark)
        self.btnAddPhoto.clicked.connect(self.addPhoto)
        self.btnUpdatePhoto.clicked.connect(self.savePhoto)
        self.btnDeletePhoto.clicked.connect(self.removePhoto)
        self.lstPhotos.selectionModel().selectionChanged.connect(self.photoSelected)
        self.lstPhotos.doubleClicked.connect(self.showPhoto)

        self._enableOrDisableButtons()
        self.ToggleToolbox()

    def ToggleToolbox(self):
        layer_list = self.canvas.layers()
        
        if not layer_list :
            self.hide()
            return 
        elif len(layer_list)==0:
            self.hide()
            return

        self.setVisible(not self.isVisible())


    def getLandmarkID(self):
        #ランドマークがなかった時の処理
        return self.landmarkId

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
            self.thumbpath=os.path.join(self.folderpath,'thumb')
            ret= self.folderpath
        else:
            ret= ''
            
        self.db.close()

        return ret

    def landmarkSelected(self, infos):
        self.info = infos[0]
        ft = self.info[1]
        self.landmarkId = ft['id']

        self.leLandmarkTitle.setText(ft['title'] if ft['title'] else '')
        self.spnLandmarkClass.setValue(ft['icon_type'] if ft['icon_type'] != None else 0)

        self._highlightLandmark()
        self.populatePhotos()
        self._enableOrDisableButtons()


    def populatePhotos(self, index=0):
        self.model.clear()

        QApplication.setOverrideCursor(Qt.WaitCursor)

        # photos is a list of tuples (id, title, imagepath)
        photos = self._photosOfLandmark()
        for i in photos:

            tp=os.path.join(self.thumbpath, str(i[0])) +'.png'

            img=self.thumbnailPhoto(i[2],tp)

            icon = QIcon(img)

            title = i[1] if i[1] else '<unnamed photo> %s' % i[0]

            item = QStandardItem(title)
            item.setIcon(icon)
            item.setData(i[0], Qt.UserRole)
            item.setToolTip(title)
            self.model.appendRow(item)
            lastIdx = self.model.indexFromItem(item)

        idx = self.model.createIndex(0, 0)
        if self.model.rowCount() > 0:
            if index == -1:
                idx = lastIdx
            elif index > 0:
                idx = self.model.createIndex(index, 0)
            self.lstPhotos.selectionModel().select(idx, QItemSelectionModel.Select)
        else:
            self._clearForm()

        QApplication.restoreOverrideCursor()

    def thumbnailPhoto(self,imagePath,tp):

        if os.path.exists(tp) :
            return QPixmap(tp)
        else :
            if os.path.exists(os.path.dirname(tp)) == False:
                os.mkdir(os.path.dirname(tp))
            pixmap=QPixmap(imagePath).scaled(800, 600).scaled(75, 50, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            a=pixmap.save(tp, 'PNG')
            return pixmap
        
    def showPhoto(self, index):
        if not self.openDatabase():
            return

        item = self.lstPhotos.model().itemFromIndex(index)
        self.query.prepare('SELECT filename ,ST_X(geom),ST_Y(geom),geom FROM t_photo WHERE p_id=?;')
        self.query.addBindValue(item.data(Qt.UserRole))
        if self.query.exec_():
            self.query.first()
            path = os.path.join(self.folderpath, self.query.value(0))
            if self.query.value(3) <> '010100000000000000000000000000000000000000' :
                lon=self.query.value(1)
                lat=self.query.value(2)
                point=self._transformPoint(QgsPoint(lon, lat))
                self.canvas.freeze(True)
                self.canvas.setCenter(point)
                self.canvas.freeze(False)
                self.canvas.refresh()

            dlg = ViewPhotoDialog(path)
            dlg.exec_()

        else:
            a= self.query.lastError().text()
            
        self.db.close()

    def saveLandmark(self):
        layer = self.info[0]
        fid = self.info[1].id()

        idxTitle = layer.fieldNameIndex('title')
        idxClassification = layer.fieldNameIndex('icon_type')

        attrs = {idxTitle: self.leLandmarkTitle.text(),\
                 idxClassification: self.spnLandmarkClass.value()
                }

        layer.dataProvider().changeAttributeValues({fid: attrs})
        layer.reload()
        layer.triggerRepaint()

        self.landmarkMessage.emit(self.tr('Landmark updated.'), QgsMessageBar.INFO)

    def deleteLandmark(self):
        layer = self.info[0]
        fid = self.info[1].id()

        layer.dataProvider().deleteFeatures([fid])
        layer.reload()
        layer.triggerRepaint()

        self._clearAllFields()

        self.landmarkMessage.emit(self.tr('Landmark deleted.'), QgsMessageBar.INFO)

    def addPhoto(self):
        if self.landmarkId is not None:
            settings = QSettings('MatsueGkukan', 'Gkukandb')
            lastDir = settings.value('lastPhotoDir', '.')

            fileName = QFileDialog.getOpenFileName(
                self, self.tr('Select photo'), lastDir, self._createFilter())

            if fileName == '':
                return

            settings.setValue('lastPhotoDir', QFileInfo(fileName).absoluteDir().absolutePath())

            projectPath =self.GetPhotoFolderPath()+os.sep
            photoPath = os.path.basename(fileName)
            photoDate = self._photoDate(fileName).toString('yyyy-MM-dd')

            if not self.openDatabase():
                return

            self.query.prepare('INSERT INTO t_photo("cdate", "filename", "landmark_id",lon,lat,angle,geomtype,geom) VALUES(?, ?, ?,?,?,?,?,?);')
            self.query.addBindValue(photoDate)
            self.query.addBindValue(photoPath)
            self.query.addBindValue(self.landmarkId)
            self.query.addBindValue(0)
            self.query.addBindValue(0)
            self.query.addBindValue(0)
            self.query.addBindValue(0)
            self.query.addBindValue('010100000000000000000000000000000000000000')
            if self.query.exec_():
                self._copyPhotoToFolder(fileName,self.landmarkId)
                self.populatePhotos(-1)
            else:
                a= self.query.lastError().text()

            self.db.close()
        else:
            self.landmarkMessage.emit(self.tr('Select landmark before adding a photo.'), QgsMessageBar.WARNING)

    def savePhoto(self):
        if not self.openDatabase():
            return


        self.query.prepare('UPDATE t_photo SET film_no=?, keywords=?, keyword1=?, keyword2=?, keyword3=?, notes=?, mdate=?, registrant=?, comment=?, reference=?, angle=? WHERE p_id=?;')
        self.query.addBindValue(self.lePhotoTitle.text())
        self.query.addBindValue(self.leKeywords.text())
        self.query.addBindValue(self.leKeyword1.text())
        self.query.addBindValue(self.leKeyword2.text())
        self.query.addBindValue(self.leKeyword3.text())
        self.query.addBindValue(self.txtPhotoComment.toPlainText())
        self.query.addBindValue(self.edPhotoDate.dateTime().toString('yyyy-MM-dd'))
        self.query.addBindValue(self.leRegistrant.text())
        self.query.addBindValue(self.leComment.text())
        self.query.addBindValue(self.lerRference.text())
        self.query.addBindValue(self.spnPhotoAngle.value())
        self.query.addBindValue(self.photoId)


        if self.query.exec_():
            self.landmarkMessage.emit(self.tr('Photo updated.'), QgsMessageBar.INFO)
            self.populatePhotos(self.lstPhotos.currentIndex().row())
        else :
            a= self.query.lastError().text()

        self.db.close()

    def removePhoto(self):
        if not self.openDatabase():
            return

        self.query.prepare('DELETE FROM t_photo WHERE "p_id"=?;')
        self.query.addBindValue(self.photoId)
        if self.query.exec_():
            self.db.close()
            self._removePhotofromFolder()

            self.populatePhotos()

    def photoSelected(self, current, previous):
        if not self.openDatabase():
            return

        idx = current.indexes()[0]
        item = self.lstPhotos.model().itemFromIndex(idx)
        self.photoId = item.data(Qt.UserRole)

        self.query.prepare('SELECT film_no, filename, keywords, keyword1, keyword2, keyword3, notes, mdate, registrant, comment, reference, angle FROM t_photo WHERE p_id=?;')
        self.query.addBindValue(self.photoId)
        if self.query.exec_():
            self.query.first()
            self.filename=self.query.value(1)
            self.lePhotoTitle.setText(self.query.value(0) if self.query.value(0) else '')
            self.txtPhotoComment.setPlainText(self.query.value(6) if self.query.value(6) else '')
            self.leKeywords.setText(self.query.value(2) if self.query.value(2) else '')
            self.leKeyword1.setText(self.query.value(3) if self.query.value(3) else '')
            self.leKeyword2.setText(self.query.value(4) if self.query.value(4) else '')
            self.leKeyword3.setText(self.query.value(5) if self.query.value(5) else '')
            self.leRegistrant.setText(self.query.value(8) if self.query.value(8) else '')
            self.leComment.setText(self.query.value(9) if self.query.value(9) else '')
            self.lerRference.setText(self.query.value(10) if self.query.value(10) else '')
            self.spnPhotoAngle.setValue(int(self.query.value(11)) if self.query.value(11) else 0)
            self.edPhotoDate.setDateTime(self.query.value(7) if self.query.value(7) else QDateTime.currentDateTime())

        self._enableOrDisableButtons()

        self.db.close()

    def _photosOfLandmark(self):

        projectPath =self.GetPhotoFolderPath()

        if not self.openDatabase():
            return

        photos = []
        self.query.prepare('SELECT "p_id", "keywords", "filename" FROM t_photo WHERE "landmark_id"=? ORDER BY "p_id";')
        self.query.addBindValue(self.landmarkId)
        if self.query.exec_():
            while self.query.next():
                photos.append((self.query.value(0), self.query.value(1), os.path.join(projectPath, self.query.value(2))))

        self.db.close()

        return photos

    def _createFilter(self):
        formats = ''
        for f in QImageReader.supportedImageFormats():
            f = unicode(f)
            if f == 'svg':
                continue
            formats += '*.{} *.{} '.format(f.lower(), f.upper())

        return self.tr('Image files (%s);;All files (*.*)' % formats[:-1])

    def _clearForm(self):
        self.lePhotoTitle.clear()
        self.txtPhotoComment.clear()
        self.leKeyword1.clear()
        self.leKeyword2.clear()
        self.leKeyword3.clear()
        self.leRegistrant.clear()
        self.leComment.clear()
        self.lerRference.clear()

        self.photoId = None
        self.landmarkId=None

    def _enableOrDisableButtons(self):
        if self.landmarkId is None:
            self.btnAddPhoto.setEnabled(False)
        else:
            self.btnAddPhoto.setEnabled(True)

        if self.photoId is None:
            self.btnDeletePhoto.setEnabled(False)
            self.btnUpdatePhoto.setEnabled(False)
        else:
            self.btnDeletePhoto.setEnabled(True)
            self.btnUpdatePhoto.setEnabled(True)

    def _highlightLandmark(self):
        self._clearHighlight()

        self.highlight = QgsHighlight(self.canvas, self.info[1].geometry(), self.info[0])

        settings = QSettings()
        color = QColor(settings.value('/Map/highlight/color', QGis.DEFAULT_HIGHLIGHT_COLOR.name()))
        alpha = settings.value('/Map/highlight/colorAlpha', QGis.DEFAULT_HIGHLIGHT_COLOR.alpha(), type=int)
        buffer = settings.value('/Map/highlight/buffer', QGis.DEFAULT_HIGHLIGHT_BUFFER_MM, type=float)
        minWidth = settings.value('/Map/highlight/minWidth', QGis.DEFAULT_HIGHLIGHT_MIN_WIDTH_MM, type=float)

        self.highlight.setColor(color)
        color.setAlpha(alpha)
        self.highlight.setFillColor(color)
        self.highlight.setBuffer(buffer);
        self.highlight.setMinWidth(minWidth)
        self.highlight.show()

    def _photoDate(self, path):
        with open(path, 'rb') as imgFile:
            tags = exifread.process_file(imgFile, details=False)

        if 'EXIF GPS GPSDate' in tags:
            return QDateTime.fromString(tags['EXIF GPS GPSDate'].values, 'yyyy:MM:dd')
        else:
            return QDateTime.currentDateTime()

    def _clearHighlight(self):
        if hasattr(self, 'highlight'):
            del self.highlight
            self.highlight = None

    def _clearAllFields(self):
        self.leLandmarkTitle.clear()
        self.spnLandmarkClass.clear()

        self._clearHighlight()
        self._clearForm()
        self.model.clear()

    def _copyPhotoToFolder(self,path,landmark_id):
        projectPath =self.GetPhotoFolderPath()
        dst= os.path.join(projectPath,os.path.basename(path))

        shutil.copy2(path, dst)

    def _removePhotofromFolder(self,path,landmark_id):
        projectPath =self.GetPhotoFolderPath()
        dst= os.path.join(projectPath,path)

        os.remove(dst)
        
    def _transformPoint(self, pnt):
        crsDest = self.canvas.mapSettings().destinationCrs()
        xform = QgsCoordinateTransform(self.geoCrs, crsDest)
        p2 = xform.transform(pnt)
        return p2
