# -*- coding: utf-8 -*-

"""
***************************************************************************
    identifytool.py
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

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QCursor, QPixmap

from qgis.core import QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry, QgsFeatureRequest
from qgis.gui import QgsMapToolEmitPoint

import GkukanMusiumdb.resources_rc

class AddLandmarkTool(QgsMapToolEmitPoint):
    landmarkAdded = pyqtSignal(list)

    def __init__(self, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)

        self.canvas = canvas
        self.cursor = QCursor(QPixmap(':/icons/cursor.png'), 1, 1)
        self.geoCrs = QgsCoordinateReferenceSystem(4326)

    def setLayer(self, layer):
        self.layer = layer
        self.layer.featureAdded.connect(self.added)

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        if self.layer is not None and self.layer.isValid():
            self.layer.featureAdded.disconnect(self.added)

        QgsMapToolEmitPoint.deactivate(self)

    def canvasPressEvent(self, event):
        pnt = self.toMapCoordinates(event.pos())
        sourceCrs = self.canvas.mapSettings().destinationCrs()
        if sourceCrs.authid() != 'EPSG:4326':
            crsTransform = QgsCoordinateTransform(sourceCrs, self.geoCrs)
            pnt = crsTransform.transform(pnt)

        fields = self.layer.pendingFields()

        ft = QgsFeature()
        ft.setFields(fields)
        ft.setGeometry(QgsGeometry.fromPoint(pnt))

        self.layer.startEditing()
        self.layer.addFeature(ft)
        self.layer.commitChanges()

    def added(self, fid):
        ft = self.layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).next()
        self.landmarkAdded.emit([(self.layer, QgsFeature(ft))])
