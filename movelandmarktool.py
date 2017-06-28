# -*- coding: utf-8 -*-

"""
***************************************************************************
    movetool.py
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

import sys

from PyQt4.QtCore import QSettings, pyqtSignal
from PyQt4.QtGui import QCursor, QPixmap, QMouseEvent, QColor

from qgis.core import QgsRectangle, QgsTolerance, QgsGeometry, QgsFeatureRequest, QgsFeature
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMessageBar

import GkukanMusiumdb.resources_rc

class MoveLandmarkTool(QgsMapTool):
    landmarkMoved = pyqtSignal(unicode, int)

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.cursor = QCursor(QPixmap(':/icons/cursor.png'), 1, 1)

        self.rubberBand = None
        self.movedFeatures = []

    def setLayer(self, layer):
        self.layer = layer

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        if self.rubberBand is not None:
            self.rubberBand.reset()
        del self.rubberBand
        self.rubberBand = None
        self.canvas.refresh()

        QgsMapTool.deactivate(self)

    def canvasMoveEvent(self, event):
        if self.rubberBand is not None:
            pointCanvasCoords = self.toMapCoordinates(event.pos())
            offsetX = pointCanvasCoords.x() - self.startPointMapCoords.x()
            offsetY = pointCanvasCoords.y() - self.startPointMapCoords.y()
            self.rubberBand.setTranslationOffset(offsetX, offsetY)
            self.rubberBand.updatePosition()
            self.rubberBand.update()

    def canvasPressEvent(self, event):
        if self.rubberBand is not None:
            self.rubberBand.reset()
        del self.rubberBand
        self.rubberBand = None
        self.canvas.refresh()

        layerCoords = self.toLayerCoordinates(self.layer, event.pos())
        searchRadius = QgsTolerance.vertexSearchRadius(self.canvas.currentLayer(), self.canvas.mapSettings())
        selectRect = QgsRectangle(layerCoords.x() - searchRadius,
                                  layerCoords.y() - searchRadius,
                                  layerCoords.x() + searchRadius,
                                  layerCoords.y() + searchRadius)

        pointGeometry = QgsGeometry.fromPoint(layerCoords)
        if not pointGeometry:
            return

        minDistance = sys.float_info.max

        cf = None
        for f in self.layer.getFeatures(QgsFeatureRequest().setFilterRect(selectRect).setSubsetOfAttributes([])):
            if f.geometry():
                currentDistance = pointGeometry.distance(f.geometry())
                if currentDistance < minDistance:
                    minDistance = currentDistance
                    cf = f

        if minDistance == sys.float_info.max:
            return

        self.movedFeatures[:] = []
        self.movedFeatures.append(QgsFeature(cf))

        self.rubberBand = self.createRubberBand(self.layer.geometryType())
        self.rubberBand.setToGeometry(cf.geometry(), self.layer)

        self.startPointMapCoords = self.toMapCoordinates(event.pos())
        self.rubberBand.setColor(QColor(255, 0, 0, 65))
        self.rubberBand.setWidth(2)
        self.rubberBand.show()

    def canvasReleaseEvent(self, event):
        if self.rubberBand is None:
            return

        startPointLayerCoords = self.toLayerCoordinates(self.layer, self.startPointMapCoords)
        stopPointLayerCoords = self.toLayerCoordinates(self.layer, event.pos())
        dx = stopPointLayerCoords.x() - startPointLayerCoords.x()
        dy = stopPointLayerCoords.y() - startPointLayerCoords.y()

        for f in self.movedFeatures:
             geom = QgsGeometry(f.geometry())
             geom.translate(dx, dy)
             self.layer.dataProvider().changeGeometryValues({f.id(): geom})

        if self.rubberBand is not None:
            self.rubberBand.reset()
        del self.rubberBand
        self.rubberBand = None
        self.canvas.refresh()
        self.layer.triggerRepaint()
        self.landmarkMoved.emit(self.tr('Landmark moved.'), QgsMessageBar.INFO)

    def createRubberBand(self, geomType):
        settings = QSettings()

        rb = QgsRubberBand(self.canvas, geomType)
        rb.setWidth(settings.value('/qgis/digitizing/line_width', 1, type=int))
        color = QColor(settings.value('/qgis/digitizing/line_color_red', 255, type=int),
                       settings.value('/qgis/digitizing/line_color_green', 0, type=int),
                       settings.value('/qgis/digitizing/line_color_blue', 0, type=int))
        alpha = settings.value('/qgis/digitizing/line_color_alpha', 200, type=int) / 255.0
        color.setAlphaF(alpha)
        rb.setColor(color)
        return rb
