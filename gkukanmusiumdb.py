# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GkukanMusiumdb
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


from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QProgressBar
# Initialize Qt resources from file resources.py
import GkukanMusiumdb.resources

# Import the code for the DockWidget
from qgis.core import QgsProject
from qgis.gui import *
from gkukanmusiumdb_dockwidget import GkukanMusiumdbDockWidget
from GkukanMusiumdb.landmark_plugin import LandmarkPlugin

import os.path
import time


class GkukanMusiumdb:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GkukanMusiumdb_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&gkukanmusiumdb')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GkukanMusiumdb')
        self.toolbar.setObjectName(u'GkukanMusiumdb')

        #print "** INITIALIZING GkukanMusiumdb"

        self.pluginIsActive = False
        self.dockwidget = None

        self.GKukanSetting()
        self.land=LandmarkPlugin(self.iface)

        self.projectloaded=False

        QgsProject.instance().readProject.connect(self.project_loaded)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GkukanMusiumdb', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GkukanMusiumdb/icons/MGMusium.png' #icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Matsue G-Kukan'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.land.initGui(self.toolbar)


    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""


        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        self.land.unload()

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&gkukanmusiumdb'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    #--------------------------------------------------------------------------

    def GKukanSetting(self):
        settings = QSettings('MatsueGkukan', 'Gkukandb')
        settings.setValue('hostname','localhost')
        settings.setValue('databasename','gmusiumdb')
        settings.setValue('username','matsueg')
        settings.setValue('dbpassword','matsueg')


    def run(self):
        """Run method that loads and starts the plugin"""

        if self.projectloaded==False:
            return

        layer_list = self.canvas.layers()
        
        if not layer_list :
            return 
        elif len(layer_list)==0:
            return

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = GkukanMusiumdbDockWidget(self.iface,self.land)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
            self.dockwidget.setWindowTitle(self.tr(u'gkukanmusiumdb'))
            self.dockwidget.show()
            

    def project_loaded(self):
        pass
        self.projectloaded=True

