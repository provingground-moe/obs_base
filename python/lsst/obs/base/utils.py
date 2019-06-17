#
# LSST Data Management System
# Copyright 2017 AURA/LSST
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import lsst.afw.geom as afwGeom
from lsst.afw.cameraGeom import PIXELS, FIELD_ANGLE
from lsst.afw.image import RotType
from lsst.afw.geom.skyWcs import makeSkyWcs
import re


def createInitialSkyWcs(visitInfo, detector, flipX=False):
    """Create a SkyWcs from the telescope boresight and detector geometry.

    A typical usecase for this is to create the initial WCS for a newly-read
    raw exposure.


    Parameters
    ----------
    visitInfo : `lsst.afw.image.VisitInfo`
        Where to get the telescope boresight and rotator angle from.
    detector : `lsst.afw.cameraGeom.Detector`
        Where to get the camera geomtry from.
    flipX : `bool`
        If False, +X is along W, if True +X is along E.

    Returns
    -------
    skyWcs : `lsst.afw.geom.SkyWcs`
        The new composed WCS.
    """

    if visitInfo.getRotType() != RotType.SKY:
        raise RuntimeError("Cannot handle rotator angle defined on %s", visitInfo.getRotType())
    orientation = visitInfo.getBoresightRotAngle()
    boresight = visitInfo.getBoresightRaDec()
    pixelsToFieldAngle = detector.getTransform(detector.makeCameraSys(PIXELS),
                                               detector.makeCameraSys(FIELD_ANGLE))
    return makeSkyWcs(pixelsToFieldAngle, orientation, flipX, boresight)


def bboxFromIraf(irafBBoxStr):
    """Return a Box2I corresponding to an IRAF-style BBOX

    [x0:x1,y0:y1] where x0 and x1 are the one-indexed start and end columns, and correspondingly
    y0 and y1 are the start and end rows.
    """

    mat = re.search(r"^\[([-\d]+):([-\d]+),([-\d]+):([-\d]+)\]$", irafBBoxStr)
    if not mat:
        raise RuntimeError("Unable to parse IRAF-style bbox \"%s\"" % irafBBoxStr)
    x0, x1, y0, y1 = [int(_) for _ in mat.groups()]

    return afwGeom.BoxI(afwGeom.PointI(x0 - 1, y0 - 1), afwGeom.PointI(x1 - 1, y1 - 1))
