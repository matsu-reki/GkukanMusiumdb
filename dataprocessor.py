# -*- coding: utf-8 -*-

"""
***************************************************************************
    dataeprocessor.py
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
from qgis import core

__author__ = 'Hirofumi Hayashi(osgeo.jp)'
__date__ = 'January 2017'
__copyright__ = 'Copyright (c)  2017 MATSUE REKISHIKAN'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import re
import os
import csv
import uuid
import zipfile
import StringIO
import locale
from PyQt4.QtCore import QDir, QSettings
from PyQt4.QtSql import QSqlDatabase, QSqlQuery
from qgis.core import  QgsVectorFileWriter, QgsProject , NULL
from GkukanMusiumdb.csvunicode import UnicodeWriter, UnicodeReader

class DataProcessor:
    def __init__(self, source):
        self.layer = None
        self.dataFile = None

        regex = re.compile("dbname='(.+)'")
        r = regex.search(source)
        self.source = r.groups()[0]

	#QPSQL
        #self.db = QSqlDatabase.addDatabase('QPSQL')
        self.db = QSqlDatabase.addDatabase('QSQLITE')

        encoding = locale.getdefaultlocale()[1]
        if encoding is None:
            self.csvEncoding = 'utf-8'
        else:
            self.csvEncoding = encoding.lower()

    def setLayer(self, layer):
        self.layer = layer

    def setDataFile(self, fileName):
        self.dataFile = fileName

    def exportData(self):
        landmarks = self._exportLayer()
        if landmarks is None:
            return False

        photos = self._exportPhotos()
        if photos is None:
            return False

        zf = zipfile.ZipFile(self.dataFile, 'w')

        zf.write(landmarks, 'landmarks.csv')
        zf.write(photos, 'photos.csv')
        zf.close()
        return True

    def importData(self):
        if not self._importLayer():
            return False
        if not self._importPhotos():
            return False
        return True

    def _openDatabase(self):


        self.db.setDatabaseName(self.source)
        if not self.db.open():
            return False

        self.query = QSqlQuery()
        return True

    def _exportLayer(self):
        fileName = self._tempFileName()
        err =QgsVectorFileWriter.writeAsVectorFormat(
            self.layer,
            fileName,
            self.csvEncoding,
            self.layer.crs(),
            'CSV',
            layerOptions=['GEOMETRY=AS_XY']
            )

        if err != QgsVectorFileWriter.NoError:
            return None

        return fileName

    def _importLayer(self):
        ids = []
        titles = []
        types = []
        angles = []
        x = []
        y = []

        result = False

        zf = zipfile.ZipFile(self.dataFile, 'r')
        fh = StringIO.StringIO(zf.read('landmarks.csv'))

        reader = UnicodeReader(fh, dialect='excel', quotechar='"', encoding=self.csvEncoding)
        reader.next()
        for r in reader:
            x.append(float(r[0]) if r[0] else None)
            y.append(float(r[1]) if r[1] else None)
            ids.append(int(r[2]) if r[2] else None)
            titles.append(r[3])
            types.append(int(r[4]) if r[4] else None)
            angles.append(float(r[5]) if r[5] else None)

        if not self._openDatabase():
            return False

        self.query.prepare('INSERT OR REPLACE INTO landmark("id", "title", "icon_type", "label_angle", "the_geom") VALUES(?, ?, ?, ?, MakePoint(?, ?, 4326));')
        self.query.addBindValue(ids)
        self.query.addBindValue(titles)
        self.query.addBindValue(types)
        self.query.addBindValue(angles)
        self.query.addBindValue(x)
        self.query.addBindValue(y)
        if self.query.execBatch():
            result = True

        self.db.close()

        return result

    def _exportPhotos(self):
        if not self._openDatabase():
            return None

        result = None

        fileName = self._tempFileName()
        self.query.prepare('SELECT "id", "angle", "date", "title", "comment", "imagepath", "landmark_id" FROM photo;')
        if self.query.exec_():
            result = fileName
            with open(fileName, 'wb') as f:
                writer = UnicodeWriter(f, dialect='excel', quotechar='"', encoding=self.csvEncoding)
                writer.writerow(('id', 'angle', 'date', 'title', 'comment', 'imagepath', 'landmark_id'))
                while self.query.next():
                    pid = unicode(self.query.value(0)) if self.query.value(0) != None else ''
                    angle = unicode(self.query.value(1)) if self.query.value(1) else ''
                    date = self.query.value(2) if self.query.value(2) else ''
                    title = self.query.value(3) if self.query.value(3) else ''
                    comment = self.query.value(4) if self.query.value(4) else ''
                    imgpath = self.query.value(5) if self.query.value(5) else ''
                    landmarkid = unicode(self.query.value(6)) if self.query.value(6) != None else ''
                    writer.writerow((pid, angle, date, title, comment, imgpath, landmarkid))

        self.db.close()

        return result

    def _importPhotos(self):
        pids = []
        angles = []
        dates = []
        titles = []
        comments = []
        paths = []
        ids = []

        result = False

        zf = zipfile.ZipFile(self.dataFile, 'r')
        fh = StringIO.StringIO(zf.read('photos.csv'))

        reader = UnicodeReader(fh, dialect='excel', quotechar='"', encoding=self.csvEncoding)
        reader.next()
        for r in reader:
            pids.append(int(r[0]) if r[0] else None)
            angles.append(float(r[1]) if r[1] else None)
            dates.append(r[2])
            titles.append(r[3])
            comments.append(r[4])
            paths.append(r[5])
            ids.append(int(r[6]) if r[6] else None)

        if not self._openDatabase():
            return False

        self.query.prepare('INSERT OR REPLACE INTO photo("id", "angle", "date", "title", "comment", "imagepath", "landmark_id") VALUES(?, ?, ?, ?, ?, ?, ?);')
        self.query.addBindValue(pids)
        self.query.addBindValue(angles)
        self.query.addBindValue(dates)
        self.query.addBindValue(titles)
        self.query.addBindValue(comments)
        self.query.addBindValue(paths)
        self.query.addBindValue(ids)
        if self.query.execBatch():
            result = True

        self.db.close()

        return result

    def _tempDirectory(self):
        tmp = unicode(os.path.join(QDir.tempPath(), 'landmark'))
        if not os.path.exists(tmp):
            QDir().mkpath(tmp)

        return os.path.abspath(tmp)

    def _tempFileName(self):
        tmpDir = self._tempDirectory()
        fName = os.path.join(tmpDir, str(uuid.uuid4()).replace('-', '') + '.csv')
        return fName
