Geometry definitions
====================
The module **pyresample.geometry** contains classes for describing different kinds of types
of remote sensing data geometries. The use of the different classes is described below.

Remarks
-------

# from_params can take radians.
All longitudes and latitudes provided to **pyresample.geometry** must be in degrees.
Longitudes must additionally be in the [-180;+180[ validity range.

# data outside of range does not clip.
As of version 1.1.1, the **pyresample.geometry** contructors will check the range of
longitude values, send a warning if some of them fall outside validity range,
and automatically correct the invalid values into [-180;+180[.

Use function **utils.wrap_longitudes** for wrapping longitudes yourself.

AreaDefinition
--------------

The cartographic definition of grid areas used by Pyresample is contained in an
object of type AreaDefintion. The following arguments are needed to initialize
an area:

* **area_id** ID of area
* **name**: Description
* **proj_id**: ID of projection (being deprecated)
* **proj_dict**: Proj4 parameters as dict
* **x_size**: Number of grid columns
* **y_size**: Number of grid rows
* **area_extent**: (x_ll, y_ll, x_ur, y_ur)

where

* **x_ll**: projection x coordinate of lower left corner of lower left pixel
* **y_ll**: projection y coordinate of lower left corner of lower left pixel
* **x_ur**: projection x coordinate of upper right corner of upper right pixel
* **y_ur**: projection y coordinate of upper right corner of upper right pixel

Creating an area definition:

.. doctest::

 >>> from pyresample import geometry
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> proj_dict = {'a': '6371228.0', 'units': 'm', 'lon_0': '0',
 ...              'proj': 'laea', 'lat_0': '-90'}
 >>> area_def = geometry.AreaDefinition(area_id, description, proj_id,
 ... 									proj_dict, x_size, y_size, area_extent)
 >>> print(area_def)
 Area ID: ease_sh
 Description: Antarctic EASE grid
 Projection ID: ease_sh
 Projection: {'a': '6371228.0', 'lat_0': '-90', 'lon_0': '0', 'proj': 'laea', 'units': 'm'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

pyresample.utils
****************
# list of proj4 arguments?
The utils module of pyresample has convenience functions for constructing
area defintions. The function **get_area_def** can construct an area definition
based on area extent and a proj4-string/dict or a list of proj4 arguments.

.. doctest::

 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                  			   x_size, y_size, area_extent)
 >>> print(area_def)
 Area ID: ease_sh
 Description: Antarctic EASE grid
 Projection ID: ease_sh
 Projection: {'a': '6371228.0', 'lat_0': '-90', 'lon_0': '0', 'proj': 'laea', 'units': 'm'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

The following arguments can be put in a yamle or passed to the function **get_params** in
order to make an area definition. Note: Not all of the arguments are needed; the functions
will attempt to figure out the information required (area_extent, x_size, and y_size) to make
an area definition from the information you provide.

required:
* **description**: Description
* **projection**: Proj4 parameters as a dict or string
optional:
* **area_id**: ID of area
* **proj_id**: ID of projection (being deprecated)
* **units**: Default projection units (meters/radians/degrees). If units are not specified,
they will default to the proj4's units and then to meters if they are still not provided.
* **shape**: (y_size, x_size). Note: if x_size = y_size, then only x_size or y_size needs to be passed
* **area_extent**: (x_ll, y_ll, x_ur, y_ur). lower_left_xy and upper_right_xy can be specified as (x_ll, y_ll) and
(x_ur, y_ur) respectively. Note: if x_ll = y_ll or x_ur = y_ur, then only x_ll/y_ll or x_ur/y_ur needs to be
passed respectively.
* **top_left_extent**: (x_ul, y_ul). Note: if x_ul = y_ul, then only x_ul or y_ul needs to be passed
* **center**: (center_x, center_y). Note: if center_x = center_y, then only center_x or center_y needs to be passed
* **pixel_size**: size of each pixel in projection units
* **radius**: length from center of projection to edge of projection in projection units

The **load_area** function can be used to parse area definitions from a
configuration file. Assuming the file **areas.yaml** exists with the following
content.

.. code-block:: yaml

 ease_sh:
   description: Antarctic EASE grid
   area_id: ease_sh
   proj_id: ease_sh
   units: meters

   projection:
     a: 6371228.0
     units: m
     lon_0: 0
     proj: laea
     lat_0: -90

   shape:
     height: 425
     width: 425
   shape: 425/[425, 425]
   shape:
     size: 425/[425, 425]

   area_extent:
     lower_left_xy: -5326849.0625
     upper_right_xy: 5326849.0625
     units: m/deg/rad
   area_extent: [-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625]
   area_extent:
     size: [-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625]
     units: m/deg/rad

   top_left_extent:
     x: -5326849.0625
     y: 5326849.0625
     units: m/deg/rad
   top_left_extent: 5326849.0625/[-5326849.0625, 5326849.0625]
   top_left_extent:
     size: 5326849.0625/[-5326849.0625, 5326849.0625]
     units: m/deg/rad

   center:
     x: 0
     y: 0
    units: m/deg/rad
   center: 0/[0, 0]
   center:
     size: 0/[0, 0]
     units: m/deg/rad

   pixel_size:
     x: 12533.7625
     y: 25067.525
     units: m/deg/rad
   pixel_size: 25067.525/[12533.7625, 25067.525]
   pixel_size:
     size: 25067.525/[12533.7625, 25067.525]
     units: m/deg/rad

   radius:
     x: 5326849.0625
     y: 5326849.0625
     units: m/deg/rad
   radius: 5326849.0625/[5326849.0625, 5326849.0625]
   radius:
     size: 5326849.0625/[5326849.0625, 5326849.0625]
     units: m/deg/rad

 ease_nh:
   description: Arctic EASE grid
   projection:
     a: 6371228.0
     units: m
     lon_0: 0
     proj: laea
     lat_0: 90
   shape:
     height: 425
     width: 425
   area_extent:
     lower_left_xy: [-5326849.0625, -5326849.0625]
     upper_right_xy: [5326849.0625, 5326849.0625]
     units: m


An area definition dict can be read using

.. doctest::

 >>> from pyresample import utils
 >>> area = utils.load_area('areas.yaml', 'ease_nh')
 >>> print(area)
 Area ID: ease_nh
 Description: Arctic EASE grid
 Projection: {'a': '6371228.0', 'lat_0': '90', 'lon_0': '0', 'proj': 'laea', 'units': 'm'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

Note: In the configuration file, the section name maps to **area_id**.

.. note::

  The `lower_left_xy` and `upper_right_xy` items give the coordinates of the
  outer edges of the corner pixels on the x and y axis respectively. When the
  projection coordinates are longitudes and latitudes, it is expected to
  provide the extent in `longitude, latitude` order.

Several area definitions can be read at once using the region names in an argument list

.. doctest::

 >>> from pyresample import utils
 >>> nh_def, sh_def = utils.load_area('areas.yaml', 'ease_nh', 'ease_sh')
 >>> print(sh_def)
 Area ID: ease_sh
 Description: Antarctic EASE grid
 Projection: {'a': '6371228.0', 'lat_0': '-90', 'lon_0': '0', 'proj': 'laea', 'units': 'm'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)



.. note::

  For backwards compatibility, we still support the legacy area file format:

Assuming the file **areas.cfg** exists with the following content

.. code-block:: bash

 REGION: ease_sh {
	NAME:           Antarctic EASE grid
	PCS_ID:         ease_sh
        PCS_DEF:        proj=laea, lat_0=-90, lon_0=0, a=6371228.0, units=m
        XSIZE:          425
        YSIZE:          425
        AREA_EXTENT:    (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 };

 REGION: ease_nh {
        NAME:           Arctic EASE grid
        PCS_ID:         ease_nh
        PCS_DEF:        proj=laea, lat_0=90, lon_0=0, a=6371228.0, units=m
        XSIZE:          425
        YSIZE:          425
        AREA_EXTENT:    (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 };

An area definition dict can be read using

.. doctest::

 >>> from pyresample import utils
 >>> area = utils.load_area('areas.cfg', 'ease_nh')
 >>> print(area)
 Area ID: ease_nh
 Description: Arctic EASE grid
 Projection ID: ease_nh
 Projection: {'a': '6371228.0', 'lat_0': '90', 'lon_0': '0', 'proj': 'laea', 'units': 'm'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

Note: In the configuration file **REGION** maps to **area_id** and **PCS_ID** maps to **proj_id**.

Several area definitions can be read at once using the region names in an argument list

.. doctest::

 >>> from pyresample import utils
 >>> nh_def, sh_def = utils.load_area('areas.cfg', 'ease_nh', 'ease_sh')
 >>> print(sh_def)
 Area ID: ease_sh
 Description: Antarctic EASE grid
 Projection ID: ease_sh
 Projection: {'a': '6371228.0', 'lat_0': '-90', 'lon_0': '0', 'proj': 'laea', 'units': 'm'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

GridDefinition
--------------
If the lons and lats grid values are known the area definition information can be skipped for some types
of resampling by using a GridDefinition object instead an AreaDefinition object.

.. doctest::

 >>> import numpy as np
 >>> from pyresample import geometry
 >>> lons = np.ones((100, 100))
 >>> lats = np.ones((100, 100))
 >>> grid_def = geometry.GridDefinition(lons=lons, lats=lats)

SwathDefinition
---------------
A swath is defined by the lon and lat values of the data points

.. doctest::

 >>> import numpy as np
 >>> from pyresample import geometry
 >>> lons = np.ones((500, 20))
 >>> lats = np.ones((500, 20))
 >>> swath_def = geometry.SwathDefinition(lons=lons, lats=lats)

Two swaths can be concatenated if their coloumn count matches

.. doctest::

 >>> import numpy as np
 >>> from pyresample import geometry
 >>> lons1 = np.ones((500, 20))
 >>> lats1 = np.ones((500, 20))
 >>> swath_def1 = geometry.SwathDefinition(lons=lons1, lats=lats1)
 >>> lons2 = np.ones((300, 20))
 >>> lats2 = np.ones((300, 20))
 >>> swath_def2 = geometry.SwathDefinition(lons=lons2, lats=lats2)
 >>> swath_def3 = swath_def1.concatenate(swath_def2)

Geographic coordinates and boundaries
-------------------------------------
A ***definition** object allows for retrieval of geographic coordinates using array slicing (slice stepping is currently not supported).

All ***definition** objects expose the coordinates **lons**, **lats** and **cartesian_coords**.
AreaDefinition exposes the full set of projection coordinates as
**projection_x_coords** and **projection_y_coords**. Note that in the case of
projection coordinates expressed in longitude and latitude,
**projection_x_coords** will be longitude and **projection_y_coords** will be
latitude.

.. versionchanged:: 1.5.1

    Renamed `proj_x_coords` to `projection_x_coords` and `proj_y_coords`
    to `projection_y_coords`.

Get full coordinate set:

.. doctest::

 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                               x_size, y_size, area_extent)
 >>> lons, lats = area_def.get_lonlats()

Get slice of coordinate set:

.. doctest::

 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                               x_size, y_size, area_extent)
 >>> cart_subset = area_def.get_cartesian_coords()[100:200, 350:]

If only the 1D range of a projection coordinate is required it can be extracted
using the **projection_x_coord** or **projection_y_coords** property of a geographic coordinate

.. doctest::

 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                  			   x_size, y_size, area_extent)
 >>> proj_x_range = area_def.projection_x_coords

Spherical geometry operations
-----------------------------
Some basic spherical operations are available for ***definition** objects. The
spherical geometry operations are calculated based on the corners of a
GeometryDefinition (2D SwathDefinition or Grid/AreaDefinition) and assuming the
edges are great circle arcs.

It can be tested if geometries overlaps

.. doctest::

 >>> import numpy as np
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                  			   x_size, y_size, area_extent)
 >>> lons = np.array([[-40, -11.1], [9.5, 19.4], [65.5, 47.5], [90.3, 72.3]])
 >>> lats = np.array([[-70.1, -58.3], [-78.8, -63.4], [-73, -57.6], [-59.5, -50]])
 >>> swath_def = geometry.SwathDefinition(lons, lats)
 >>> print(swath_def.overlaps(area_def))
 True

The fraction of overlap can be calculated

.. doctest::

 >>> import numpy as np
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                  			   x_size, y_size, area_extent)
 >>> lons = np.array([[-40, -11.1], [9.5, 19.4], [65.5, 47.5], [90.3, 72.3]])
 >>> lats = np.array([[-70.1, -58.3], [-78.8, -63.4], [-73, -57.6], [-59.5, -50]])
 >>> swath_def = geometry.SwathDefinition(lons, lats)
 >>> overlap_fraction = swath_def.overlap_rate(area_def)

And the polygon defining the (great circle) boundaries over the overlapping area can be calculated

.. doctest::

 >>> import numpy as np
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                  			   x_size, y_size, area_extent)
 >>> lons = np.array([[-40, -11.1], [9.5, 19.4], [65.5, 47.5], [90.3, 72.3]])
 >>> lats = np.array([[-70.1, -58.3], [-78.8, -63.4], [-73, -57.6], [-59.5, -50]])
 >>> swath_def = geometry.SwathDefinition(lons, lats)
 >>> overlap_polygon = swath_def.intersection(area_def)

It can be tested if a (lon, lat) point is inside a GeometryDefinition

.. doctest::

 >>> import numpy as np
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> description = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> projection = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, description, proj_id, projection,
 ...                  			   x_size, y_size, area_extent)
 >>> print((0, -90) in area_def)
 True
