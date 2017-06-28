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


class PhotoData:
    def __init__(self, p_id,film_no,filename,keywords,keyword1,keyword2,keyword3,filetype,exifflg,notes,cdate,mdate,filesize,registrant,comment,reference,landmark_id,lon,lat,angle,geomtype,geom, parent=None):
        self.p_id=p_id
        self.film_no=film_no
        self.filename=filename
        self.keywords=keywords
        self.keyword1=keyword1
        self.keyword2=keyword2
        self.keyword3=keyword3
        self.filetype=filetype
        self.exifflg=exifflg
        self.notes=notes
        self.cdate=cdate
        self.mdate=mdate
        self.filesize=filesize
        self.registrant=registrant
        self.comment=comment
        self.reference=reference
        self.landmark_id=landmark_id
        self.lon=lon
        self.lat=lat
        self.angle=angle
        self.geomtype=geomtype
        self.geom=geom
    