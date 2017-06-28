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
from PyQt4.QtGui import QCursor, QPixmap, QApplication

from qgis.core import QgsMapLayer, QgsRectangle, QgsCsException, QgsFeatureRequest, QgsFeature, QgsCsException, QgsFeatureRendererV2, QgsRenderContext
from qgis.gui import QgsMapTool, QgsMessageBar

import GkukanMusiumdb.resources_rc

class IdentifyTool(QgsMapTool):
    identifyMessage = pyqtSignal(unicode, int)
    identified = pyqtSignal(list)

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.cursor = QCursor(QPixmap(':/icons/cursor.png'), 1, 1)

        self.results = []

    def setLayer(self, layer):
        self.layer = layer

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        QgsMapTool.deactivate(self)

    def canvasReleaseEvent(self, event):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(
            event.x(), event.y())

        if self.layer is None:
            self.identifyMessage.emit(
                self.tr('To identify landmarks, you must select landmarks '
                        'layer by clicking on its name in the legend'),
                QgsMessageBar.WARNING)
            return

        if self.layer.type() != QgsMapLayer.VectorLayer:
            self.identifyMessage.emit(
                self.tr('This tool works only for vector layers. Please '
                        'select another layer in legend and try again'),
                QgsMessageBar.WARNING)
            return

        res = self.identifyLayer(point)

        if res:
            print 'Identify OK'
            self.identified.emit(self.results)
        else:
            pass

    def identifyLayer(self, point):
        self.results[:] = []

        if not self.layer.hasGeometryType():
            return False

        if (self.layer.hasScaleBasedVisibility() and
                (self.layer.minimumScale() > self.canvas.mapSettings().scale() or
                 self.layer.maximumScale() <= self.canvas.mapSettings().scale())):
            print 'Out of scale limits'
            return False

        QApplication.setOverrideCursor(Qt.WaitCursor)

        featureCount = 0
        featureList = []

        try:
            searchRadius = self.searchRadiusMU(self.canvas)

            r = QgsRectangle()
            r.setXMinimum(point.x() - searchRadius)
            r.setXMaximum(point.x() + searchRadius)
            r.setYMinimum(point.y() - searchRadius)
            r.setYMaximum(point.y() + searchRadius)

            r = self.toLayerCoordinates(self.layer, r)

            req = QgsFeatureRequest()
            req.setFilterRect(r)
            req.setFlags(QgsFeatureRequest.ExactIntersect)
            for f in self.layer.getFeatures(req):
                featureList.append(QgsFeature(f))
        except QgsCsException as cse:
            print 'Caught CRS exception', cse.what()

        myFilter = False
        context = QgsRenderContext(
            QgsRenderContext.fromMapSettings(self.canvas.mapSettings()))
        renderer = self.layer.rendererV2()

        if (renderer is not None and
                (renderer.capabilities() | QgsFeatureRendererV2.ScaleDependent)):
            renderer.startRender(context, self.layer.pendingFields())
            myFilter =  renderer.capabilities() and QgsFeatureRendererV2.Filter

        for f in featureList:
            if myFilter and not renderer.willRenderFeature(f):
                continue

            featureCount += 1
            self.results.append((self.layer, f))

        if (renderer is not None and
                (renderer.capabilities() | QgsFeatureRendererV2.ScaleDependent)):
            renderer.stopRender(context)

        print 'Feature count on identify:', featureCount

        QApplication.restoreOverrideCursor()

        return featureCount > 0
