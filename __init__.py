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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Hirofumi Hayashi(osgeo.jp)'
__date__ = 'January 2017'
__copyright__ = 'Copyright (c)  2017 MATSUE REKISHIKAN'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GkukanMusiumdb class from file GkukanMusiumdb.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .gkukanmusiumdb import GkukanMusiumdb
    return GkukanMusiumdb(iface)
