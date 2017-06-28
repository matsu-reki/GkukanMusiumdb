# -*- coding: utf-8 -*-

"""
***************************************************************************
    landmark_plugin.py
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

from PyQt4.QtCore import Qt, QLocale, QSettings, QFileInfo, QTranslator, QCoreApplication, QSettings, QFileInfo, QDir
from PyQt4.QtGui import QMessageBox, QIcon, QAction, QFileDialog

from qgis.core import QGis, QgsMapLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar

from GkukanMusiumdb.gui.landmarktoolbox import LandmarkToolbox

from GkukanMusiumdb.identifytool import IdentifyTool
from GkukanMusiumdb.addlandmarktool import AddLandmarkTool
from GkukanMusiumdb.movelandmarktool import MoveLandmarkTool
from GkukanMusiumdb.dataprocessor import DataProcessor

import GkukanMusiumdb.resources_rc


class LandmarkPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        pluginPath = os.path.abspath(os.path.dirname(__file__))

        overrideLocale = QSettings().value('locale/overrideFlag', False, bool)
        if not overrideLocale:
            locale = QLocale.system().name()[:2]
        else:
            locale = QSettings().value('locale/userLocale', '')

        translationPath = '{}/i18n/landmark_{}.qm'.format(pluginPath, locale)

        if QFileInfo(translationPath).exists():
            self.translator = QTranslator()
            self.translator.load(translationPath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self,toolbar):
        if int(self.qgsVersion) < 20000:
            qgisVersion = '{}.{}.{}'.format(
                self.qgsVersion[0], self.qgsVersion[2], self.qgsVersion[3])

            QMessageBox.warning(self.iface.mainWindow(), 'Landmark',
                LandmarkPlugin.tr('QGIS %s detected.\nThis version of '
                    'Landmark requires at least QGIS 2.6.0. Plugin will '
                    'not be enabled.' % qgisVersion))
            return None

        self.landmarkinit=True

        self.toolbox = LandmarkToolbox(self.iface)
        self.toolbox.setObjectName('LandmarkToolbox')
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.toolbox)
        self.toolbox.hide()

        self.toolbar = toolbar
        self.toolbar.setObjectName('LandmarkToolbar')
        self.iface.mainWindow().addToolBar(self.toolbar)

        self.actionToolbox = QAction(LandmarkPlugin.tr('Show/hide Landmark toolbox'), self.iface.mainWindow())
        self.actionToolbox.setObjectName('actionToolbox')
        self.actionToolbox.setIcon(QIcon(':/icons/landmark.svg'))
        self.actionToolbox.setWhatsThis(LandmarkPlugin.tr('Show/hide Landmark toolbox'))

        self.actionIdentify = QAction(LandmarkPlugin.tr('Identify landmark'), self.iface.mainWindow())
        self.actionIdentify.setObjectName('actionIdentify')
        self.actionIdentify.setIcon(QIcon(':/icons/identify.svg'))
        self.actionIdentify.setWhatsThis(LandmarkPlugin.tr('Identify landmark'))
        self.actionIdentify.setCheckable(True)

        self.actionNewLandmark = QAction(LandmarkPlugin.tr('Add new landmark'), self.iface.mainWindow())
        self.actionNewLandmark.setObjectName('actionNewLandmark')
        self.actionNewLandmark.setIcon(QIcon(':/icons/add.svg'))
        self.actionNewLandmark.setText(LandmarkPlugin.tr('Add new landmark'))
        self.actionNewLandmark.setWhatsThis(LandmarkPlugin.tr('Add new landmark'))
        self.actionNewLandmark.setCheckable(True)

        self.actionMoveLandmark = QAction(LandmarkPlugin.tr('Move landmark'), self.iface.mainWindow())
        self.actionMoveLandmark.setObjectName('actionMoveLandmark')
        self.actionMoveLandmark.setIcon(QIcon(':/icons/edit.svg'))
        self.actionMoveLandmark.setText(LandmarkPlugin.tr('Move landmark'))
        self.actionMoveLandmark.setWhatsThis(LandmarkPlugin.tr('Move landmark'))
        self.actionMoveLandmark.setCheckable(True)

        self.actionImport = QAction(LandmarkPlugin.tr('Import data'), self.iface.mainWindow())
        self.actionImport.setObjectName('actionImport')
        self.actionImport.setIcon(QIcon(':/icons/import.svg'))
        self.actionImport.setText(LandmarkPlugin.tr('Import data'))
        self.actionImport.setWhatsThis(LandmarkPlugin.tr('Import data'))

        self.actionExport = QAction(LandmarkPlugin.tr('Export data'), self.iface.mainWindow())
        self.actionExport.setObjectName('actionExport')
        self.actionExport.setIcon(QIcon(':/icons/export.svg'))
        self.actionExport.setText(LandmarkPlugin.tr('Export data'))
        self.actionExport.setWhatsThis(LandmarkPlugin.tr('Export data'))

        self.iface.addPluginToVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionToolbox)
        self.iface.addPluginToVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionIdentify)
        self.iface.addPluginToVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionNewLandmark)
        self.iface.addPluginToVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionMoveLandmark)
        self.iface.addPluginToVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionImport)
        self.iface.addPluginToVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionExport)

        self.toolbar.addAction(self.actionToolbox)
        self.toolbar.addAction(self.actionIdentify)
        self.toolbar.addAction(self.actionNewLandmark)
        self.toolbar.addAction(self.actionMoveLandmark)
        self.toolbar.addAction(self.actionImport)
        self.toolbar.addAction(self.actionExport)

        # prepare map tools
        self.identifyTool = IdentifyTool(self.canvas)
        self.addLandmarkTool = AddLandmarkTool(self.canvas)
        self.moveLandmarkTool = MoveLandmarkTool(self.canvas)
        self.iface.mapCanvas().mapToolSet.connect(self.mapToolChanged)

        self.actionToolbox.triggered.connect(self.toolbox.ToggleToolbox)
        self.actionIdentify.triggered.connect(self.identify)
        self.actionNewLandmark.triggered.connect(self.newLandmark)
        self.actionMoveLandmark.triggered.connect(self.moveLandmark)
        self.actionImport.triggered.connect(self.importData)
        self.actionExport.triggered.connect(self.exportData)

        self.identifyTool.identified.connect(self.toolbox.landmarkSelected)
        self.identifyTool.identifyMessage.connect(self._showMessage)
        self.addLandmarkTool.landmarkAdded.connect(self.toolbox.landmarkSelected)
        self.moveLandmarkTool.landmarkMoved.connect(self._showMessage)

        self.toolbox.landmarkMessage.connect(self._showMessage)
        self.toolbox.cmbLayers.layerChanged.connect(self._changeLandmarkLayer)

        QgsMapLayerRegistry.instance().legendLayersAdded.connect(self._toggleTools)
        QgsMapLayerRegistry.instance().layersWillBeRemoved.connect(self._toggleTools)

        self._toggleTools()


    def unload(self):
        self.toolbox.cmbLayers.layerChanged.disconnect(self._changeLandmarkLayer)
        self.iface.removePluginVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionToolbox)
        self.iface.removePluginVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionIdentify)
        self.iface.removePluginVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionNewLandmark)
        self.iface.removePluginVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionMoveLandmark)
        self.iface.removePluginVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionImport)
        self.iface.removePluginVectorMenu(LandmarkPlugin.tr('Landmark'), self.actionExport)

        if self.iface.mapCanvas().mapTool() == self.identifyTool:
            self.iface.mapCanvas().unsetMapTool(self.identifyTool)

        if self.iface.mapCanvas().mapTool() == self.addLandmarkTool:
            self.iface.mapCanvas().unsetMapTool(self.addLandmarkTool)

        if self.iface.mapCanvas().mapTool() == self.moveLandmarkTool:
            self.iface.mapCanvas().unsetMapTool(self.moveLandmarkTool)

        del self.identifyTool
        del self.addLandmarkTool
        del self.moveLandmarkTool

        self.iface.mainWindow().removeToolBar(self.toolbar)

        self.toolbox.close()

        if self.toolbox.db is not None:
            if self.toolbox.db.isOpen():
                self.toolbox.db.close()

        if hasattr(self.toolbox, 'highlight'):
            del self.toolbox.highlight


        del self.toolbox
        self.toolbox = None

        tmp = unicode(os.path.join(QDir.tempPath(), 'landmark'))
        if QDir(tmp).exists():
            shutil.rmtree(tmp, True)

    def identify(self):
        layer = self.toolbox.cmbLayers.currentLayer()
        if layer is None or not layer.isValid():
            return

        self.identifyTool.setLayer(layer)
        self.iface.mapCanvas().setMapTool(self.identifyTool)
        self.actionIdentify.setChecked(True)

    def newLandmark(self):
        layer = self.toolbox.cmbLayers.currentLayer()
        if layer is None or not layer.isValid():
            return

        self.addLandmarkTool.setLayer(layer)
        self.iface.mapCanvas().setMapTool(self.addLandmarkTool)
        self.actionNewLandmark.setChecked(True)

    def moveLandmark(self):
        layer = self.toolbox.cmbLayers.currentLayer()
        if layer is None or not layer.isValid():
            return

        self.moveLandmarkTool.setLayer(layer)
        self.iface.mapCanvas().setMapTool(self.moveLandmarkTool)
        self.actionMoveLandmark.setChecked(True)

    def importData(self):
        fileName = self._selectFile(mode='import')
        if fileName is None:
            return

        layer = self.toolbox.cmbLayers.currentLayer()
        if layer is None or not layer.isValid():
            self._showMessage(self.tr('Landmark layer is not selected.'))
            return

        writer = DataProcessor(layer.source())
        writer.setDataFile(fileName)
        if writer.importData():
            self._showMessage(self.tr('Import completed.'), QgsMessageBar.INFO)
            return

        self._showMessage(self.tr('Import failed.'))

    def exportData(self):
        fileName = self._selectFile()
        if fileName is None:
            return

        layer = self.toolbox.cmbLayers.currentLayer()
        if layer is None or not layer.isValid():
            self._showMessage(self.tr('Landmark layer is not selected.'))
            return

        writer = DataProcessor(layer.source())
        writer.setLayer(layer)
        writer.setDataFile(fileName)
        if writer.exportData():
            self._showMessage(self.tr('Export completed.'), QgsMessageBar.INFO)
            return

        self._showMessage(self.tr('Export failed.'))


    def mapToolChanged(self, tool):
        if tool != self.identifyTool:
            self.actionIdentify.setChecked(False)
            self.toolbox._clearAllFields()

        if tool != self.addLandmarkTool:
            self.actionNewLandmark.setChecked(False)
            self.toolbox._clearAllFields()

        if tool != self.moveLandmarkTool:
            self.actionMoveLandmark.setChecked(False)



    def _toggleTools(self):
        layer = self.toolbox.cmbLayers.currentLayer()
        if layer is None or layer.providerType() != 'postgres':
            self.actionIdentify.setEnabled(False)
            self.actionNewLandmark.setEnabled(False)
            self.actionMoveLandmark.setEnabled(False)
            
        else:
            a=layer.publicSource()
            if a.find('t_landmark') <> -1 :
                self.actionIdentify.setEnabled(True)
                self.actionNewLandmark.setEnabled(True)
                self.actionMoveLandmark.setEnabled(True)
            else:
                self.actionIdentify.setEnabled(False)
                self.actionNewLandmark.setEnabled(False)
                self.actionMoveLandmark.setEnabled(False)



    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'LandmarkPlugin'
        return QCoreApplication.translate(context, string)

    def _showMessage(self, message, level=QgsMessageBar.WARNING):
        self.iface.messageBar().pushMessage(
            message, level, self.iface.messageTimeout())

    def _changeLandmarkLayer(self, layer):

        if layer is None or layer.providerType() != 'postgres':
                self.actionIdentify.setEnabled(False)
                self.actionNewLandmark.setEnabled(False)
                self.actionMoveLandmark.setEnabled(False)
                self.toolbox.hide()
        else:
            a=layer.publicSource()
            if a.find('t_landmark') <> -1 :
                self.actionIdentify.setEnabled(True)
                self.actionNewLandmark.setEnabled(True)
                self.actionMoveLandmark.setEnabled(True)
            else:
                self.actionIdentify.setEnabled(False)
                self.actionNewLandmark.setEnabled(False)
                self.actionMoveLandmark.setEnabled(False)

        try:
            self.identifyTool.setLayer(layer)
        except:
            pass

    def _selectFile(self, mode='export'):
        settings = QSettings('Faunalia', 'landmark')
        lastDir = settings.value('lastZipDir', '.')

        if mode == 'export':
            fileName = QFileDialog.getSaveFileName(
                None, self.tr('Select file'), lastDir, self.tr('ZIP files (*.zip *.ZIP)'))
        else:
            fileName = QFileDialog.getOpenFileName(
                None, self.tr('Select file'), lastDir, self.tr('ZIP files (*.zip *.ZIP)'))


        if fileName == '':
            return None

        if not fileName.lower().endswith('.zip'):
            fileName += '.zip'

        settings.setValue(
            'lastZipDir', QFileInfo(fileName).absoluteDir().absolutePath())
        return fileName
