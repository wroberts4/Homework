from __future__ import with_statement

import random
import sys

import numpy as np

from pyresample import geo_filter, geometry
from pyresample.geometry import (IncompatibleAreas,
                                 combine_area_extents_vertical,
                                 concatenate_area_defs)
from pyresample.test.utils import catch_warnings

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    # separate mock package py<3.3
    from mock import MagicMock, patch

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class Test(unittest.TestCase):

    """Unit testing the geometry and geo_filter modules"""

    def test_lonlat_precomp(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])
        lons, lats = area_def.get_lonlats()
        lon, lat = area_def.get_lonlat(400, 400)
        self.assertAlmostEqual(lon, 5.5028467120975835,
                               msg='lon retrieval from precomputated grid failed')
        self.assertAlmostEqual(lat, 52.566998432390619,
                               msg='lat retrieval from precomputated grid failed')

    def test_cartesian(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])
        cart_coords = area_def.get_cartesian_coords()
        exp = 5872039989466.8457031
        self.assertTrue((cart_coords.sum() - exp) < 1e-7 * exp,
                        msg='Calculation of cartesian coordinates failed')

    def test_cartopy_crs(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)',
                                           'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                            -909968.64000000001,
                                            1029087.28,
                                            1490031.3600000001])
        crs = area_def.to_cartopy_crs()
        self.assertEqual(crs.bounds,
                         (area_def.area_extent[0],
                          area_def.area_extent[2],
                          area_def.area_extent[1],
                          area_def.area_extent[3]))

    def test_base_type(self):
        lons1 = np.arange(-135., +135, 50.)
        lats = np.ones_like(lons1) * 70.

        # Test dtype is preserved without longitude wrapping
        basedef = geometry.BaseDefinition(lons1, lats)
        lons, _ = basedef.get_lonlats()
        self.assertEqual(lons.dtype, lons1.dtype,
                         "BaseDefinition did not maintain dtype of longitudes (in:%s out:%s)" %
                         (lons1.dtype, lons.dtype,))

        lons1_ints = lons1.astype('int')
        basedef = geometry.BaseDefinition(lons1_ints, lats)
        lons, _ = basedef.get_lonlats()
        self.assertEqual(lons.dtype, lons1_ints.dtype,
                         "BaseDefinition did not maintain dtype of longitudes (in:%s out:%s)" %
                         (lons1_ints.dtype, lons.dtype,))

        # Test dtype is preserved with automatic longitude wrapping
        lons2 = np.where(lons1 < 0, lons1 + 360, lons1)
        with catch_warnings():
            basedef = geometry.BaseDefinition(lons2, lats)

        lons, _ = basedef.get_lonlats()
        self.assertEqual(lons.dtype, lons2.dtype,
                         "BaseDefinition did not maintain dtype of longitudes (in:%s out:%s)" %
                         (lons2.dtype, lons.dtype,))

        lons2_ints = lons2.astype('int')
        with catch_warnings():
            basedef = geometry.BaseDefinition(lons2_ints, lats)

        lons, _ = basedef.get_lonlats()
        self.assertEqual(lons.dtype, lons2_ints.dtype,
                         "BaseDefinition did not maintain dtype of longitudes (in:%s out:%s)" %
                         (lons2_ints.dtype, lons.dtype,))

    def test_area_hash(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        self.assertIsInstance(hash(area_def), int)

        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'lat_0': '50.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        self.assertIsInstance(hash(area_def), int)

        area_def = geometry.AreaDefinition('New area', 'Europe', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'lat_0': '50.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        self.assertIsInstance(hash(area_def), int)

    def test_get_array_hashable(self):
        arr = np.array([1.2, 1.3, 1.4, 1.5])
        if sys.byteorder == 'little':
            # arr.view(np.uint8)
            reference = np.array([51,  51,  51,  51,  51,  51, 243,
                                  63, 205, 204, 204, 204, 204,
                                  204, 244,  63, 102, 102, 102, 102,
                                  102, 102, 246,  63,   0,   0,
                                  0,   0,   0,   0, 248,  63],
                                 dtype=np.uint8)
        else:
            # on le machines use arr.byteswap().view(np.uint8)
            reference = np.array([63, 243,  51,  51,  51,  51,  51,
                                  51,  63, 244, 204, 204, 204,
                                  204, 204, 205,  63, 246, 102, 102,
                                  102, 102, 102, 102,  63, 248,
                                  0,   0,   0,   0,   0,   0],
                                 dtype=np.uint8)

        np.testing.assert_allclose(reference,
                                   geometry.get_array_hashable(arr))

        try:
            import xarray as xr
        except ImportError:
            pass
        else:
            xrarr = xr.DataArray(arr)
            np.testing.assert_allclose(reference,
                                       geometry.get_array_hashable(arr))

            xrarr.attrs['hash'] = 42
            self.assertEqual(geometry.get_array_hashable(xrarr),
                             xrarr.attrs['hash'])

    def test_swath_hash(self):
        lons = np.array([1.2, 1.3, 1.4, 1.5])
        lats = np.array([65.9, 65.86, 65.82, 65.78])
        swath_def = geometry.SwathDefinition(lons, lats)

        self.assertIsInstance(hash(swath_def), int)

        try:
            import dask.array as da
        except ImportError:
            print("Not testing with dask arrays")
        else:
            dalons = da.from_array(lons, chunks=1000)
            dalats = da.from_array(lats, chunks=1000)
            swath_def = geometry.SwathDefinition(dalons, dalats)

            self.assertIsInstance(hash(swath_def), int)

        try:
            import xarray as xr
        except ImportError:
            print("Not testing with xarray")
        else:
            xrlons = xr.DataArray(lons)
            xrlats = xr.DataArray(lats)
            swath_def = geometry.SwathDefinition(xrlons, xrlats)

            self.assertIsInstance(hash(swath_def), int)

        try:
            import xarray as xr
            import dask.array as da
        except ImportError:
            print("Not testing with xarrays and dask arrays")
        else:
            xrlons = xr.DataArray(da.from_array(lons, chunks=1000))
            xrlats = xr.DataArray(da.from_array(lats, chunks=1000))
            swath_def = geometry.SwathDefinition(xrlons, xrlats)

            self.assertIsInstance(hash(swath_def), int)

        lons = np.ma.array([1.2, 1.3, 1.4, 1.5])
        lats = np.ma.array([65.9, 65.86, 65.82, 65.78])
        swath_def = geometry.SwathDefinition(lons, lats)

        self.assertIsInstance(hash(swath_def), int)

    def test_area_equal(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])
        area_def2 = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                            {'a': '6378144.0',
                                             'b': '6356759.0',
                                             'lat_0': '50.00',
                                             'lat_ts': '50.00',
                                             'lon_0': '8.00',
                                             'proj': 'stere'},
                                            800,
                                            800,
                                            [-1370912.72,
                                                -909968.64000000001,
                                                1029087.28,
                                                1490031.3600000001])
        self.assertFalse(
            area_def != area_def2, 'area_defs are not equal as expected')

    def test_not_area_equal(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        msg_area = geometry.AreaDefinition('msg_full', 'Full globe MSG image 0 degrees',
                                           'msg_full',
                                           {'a': '6378169.0',
                                            'b': '6356584.0',
                                            'h': '35785831.0',
                                            'lon_0': '0',
                                            'proj': 'geos'},
                                           3712,
                                           3712,
                                           [-5568742.4000000004,
                                               -5568742.4000000004,
                                               5568742.4000000004,
                                               5568742.4000000004]
                                           )
        self.assertFalse(
            area_def == msg_area, 'area_defs are not expected to be equal')

    def test_swath_equal_area(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        swath_def = geometry.SwathDefinition(*area_def.get_lonlats())

        self.assertFalse(
            swath_def != area_def, "swath_def and area_def should be equal")

        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        self.assertFalse(
            area_def != swath_def, "swath_def and area_def should be equal")

    def test_swath_not_equal_area(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        lons = np.array([1.2, 1.3, 1.4, 1.5])
        lats = np.array([65.9, 65.86, 65.82, 65.78])
        swath_def = geometry.SwathDefinition(lons, lats)

        self.assertFalse(
            swath_def == area_def, "swath_def and area_def should be different")

        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           800,
                                           800,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])

        self.assertFalse(
            area_def == swath_def, "swath_def and area_def should be different")

    def test_grid_filter_valid(self):
        lons = np.array([-170, -30, 30, 170])
        lats = np.array([20, -40, 50, -80])
        swath_def = geometry.SwathDefinition(lons, lats)
        filter_area = geometry.AreaDefinition('test', 'test', 'test',
                                              {'proj': 'eqc', 'lon_0': 0.0,
                                                  'lat_0': 0.0},
                                              8, 8,
                                              (-20037508.34, -10018754.17, 20037508.34, 10018754.17))
        filter = np.array([[1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           ])
        grid_filter = geo_filter.GridFilter(filter_area, filter)
        valid_index = grid_filter.get_valid_index(swath_def)
        expected = np.array([1, 0, 0, 1])
        self.assertTrue(
            np.array_equal(valid_index, expected), 'Failed to find grid filter')

    def test_grid_filter(self):
        lons = np.array([-170, -30, 30, 170])
        lats = np.array([20, -40, 50, -80])
        swath_def = geometry.SwathDefinition(lons, lats)
        data = np.array([1, 2, 3, 4])
        filter_area = geometry.AreaDefinition('test', 'test', 'test',
                                              {'proj': 'eqc', 'lon_0': 0.0,
                                                  'lat_0': 0.0},
                                              8, 8,
                                              (-20037508.34, -10018754.17, 20037508.34, 10018754.17))
        filter = np.array([[1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           ])
        grid_filter = geo_filter.GridFilter(filter_area, filter)
        swath_def_f, data_f = grid_filter.filter(swath_def, data)
        expected = np.array([1, 4])
        self.assertTrue(
            np.array_equal(data_f, expected), 'Failed grid filtering data')
        expected_lons = np.array([-170, 170])
        expected_lats = np.array([20, -80])
        self.assertTrue(np.array_equal(swath_def_f.lons[:], expected_lons)
                        and np.array_equal(swath_def_f.lats[:], expected_lats),
                        'Failed finding grid filtering lon lats')

    def test_grid_filter2D(self):
        lons = np.array([[-170, -30, 30, 170],
                         [-170, -30, 30, 170]])
        lats = np.array([[20, -40, 50, -80],
                         [25, -35, 55, -75]])
        swath_def = geometry.SwathDefinition(lons, lats)
        data1 = np.ones((2, 4))
        data2 = np.ones((2, 4)) * 2
        data3 = np.ones((2, 4)) * 3
        data = np.dstack((data1, data2, data3))
        filter_area = geometry.AreaDefinition('test', 'test', 'test',
                                              {'proj': 'eqc', 'lon_0': 0.0,
                                                  'lat_0': 0.0},
                                              8, 8,
                                              (-20037508.34, -10018754.17, 20037508.34, 10018754.17))
        filter = np.array([[1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 1, 1, 1, 1],
                           ])
        grid_filter = geo_filter.GridFilter(filter_area, filter, nprocs=2)
        swath_def_f, data_f = grid_filter.filter(swath_def, data)
        expected = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]])
        self.assertTrue(
            np.array_equal(data_f, expected), 'Failed 2D grid filtering data')
        expected_lons = np.array([-170, 170, -170, 170])
        expected_lats = np.array([20, -80, 25, -75])
        self.assertTrue(np.array_equal(swath_def_f.lons[:], expected_lons)
                        and np.array_equal(swath_def_f.lats[:], expected_lats),
                        'Failed finding 2D grid filtering lon lats')

    def test_boundary(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           10,
                                           10,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])
        proj_x_boundary, proj_y_boundary = area_def.projection_x_coords, area_def.projection_y_coords
        expected_x = np.array([-1250912.72, -1010912.72, -770912.72,
                               -530912.72, -290912.72, -50912.72, 189087.28,
                               429087.28, 669087.28, 909087.28])
        expected_y = np.array([1370031.36, 1130031.36, 890031.36, 650031.36,
                               410031.36, 170031.36, -69968.64, -309968.64,
                               -549968.64, -789968.64])
        self.assertTrue(np.allclose(proj_x_boundary, expected_x),
                        'Failed to find projection x coords')
        self.assertTrue(np.allclose(proj_y_boundary, expected_y),
                        'Failed to find projection y coords')

    def test_area_extent_ll(self):
        area_def = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                           {'a': '6378144.0',
                                            'b': '6356759.0',
                                            'lat_0': '50.00',
                                            'lat_ts': '50.00',
                                            'lon_0': '8.00',
                                            'proj': 'stere'},
                                           10,
                                           10,
                                           [-1370912.72,
                                               -909968.64000000001,
                                               1029087.28,
                                               1490031.3600000001])
        self.assertAlmostEqual(sum(area_def.area_extent_ll),
                               122.06448093539757, 5,
                               'Failed to get lon and lats of area extent')

    def test_latlong_area(self):
        area_def = geometry.AreaDefinition('', '', '',
                                           {'proj': 'latlong'},
                                           360, 180,
                                           [-180, -90, 180, 90])
        lons, lats = area_def.get_lonlats()
        self.assertEqual(lons[0, 0], -179.5)
        self.assertEqual(lats[0, 0], 89.5)

    def test_lonlat2colrow(self):
        from pyresample import utils
        area_id = 'meteosat_0deg'
        area_name = 'Meteosat 0 degree Service'
        proj_id = 'geos0'
        x_size = 3712
        y_size = 3712
        area_extent = [-5570248.477339261, -5567248.074173444,
                       5567248.074173444, 5570248.477339261]
        proj_dict = {'a': '6378169.00',
                     'b': '6356583.80',
                     'h': '35785831.0',
                     'lon_0': '0.0',
                     'proj': 'geos'}
        area = utils.get_area_def(area_id,
                                  area_name,
                                  proj_id,
                                  proj_dict,
                                  x_size, y_size,
                                  area_extent)

        # Imatra, Wiesbaden
        longitudes = np.array([28.75242, 8.24932])
        latitudes = np.array([61.17185, 50.08258])
        cols__, rows__ = area.lonlat2colrow(longitudes, latitudes)

        # test arrays
        cols_expects = np.array([2304, 2040])
        rows_expects = np.array([186, 341])
        self.assertTrue((cols__ == cols_expects).all())
        self.assertTrue((rows__ == rows_expects).all())

        # test scalars
        lon, lat = (-8.125547604568746, -14.345524111874646)
        self.assertTrue(area.lonlat2colrow(lon, lat) == (1567, 2375))

    def test_colrow2lonlat(self):

        from pyresample import utils
        area_id = 'meteosat_0deg'
        area_name = 'Meteosat 0 degree Service'
        proj_id = 'geos0'
        x_size = 3712
        y_size = 3712
        area_extent = [-5570248.477339261, -5567248.074173444,
                       5567248.074173444, 5570248.477339261]
        proj_dict = {'a': '6378169.00',
                     'b': '6356583.80',
                     'h': '35785831.0',
                     'lon_0': '0.0',
                     'proj': 'geos'}
        area = utils.get_area_def(area_id,
                                  area_name,
                                  proj_id,
                                  proj_dict,
                                  x_size, y_size,
                                  area_extent)

        # Imatra, Wiesbaden
        cols = np.array([2304, 2040])
        rows = np.array([186, 341])
        lons__, lats__ = area.colrow2lonlat(cols, rows)

        # test arrays
        lon_expects = np.array([28.77763033, 8.23765962])
        lat_expects = np.array([61.20120556, 50.05836402])
        self.assertTrue(np.allclose(lons__, lon_expects, rtol=0, atol=1e-7))
        self.assertTrue(np.allclose(lats__, lat_expects, rtol=0, atol=1e-7))

        # test scalars
        lon__, lat__ = area.colrow2lonlat(1567, 2375)
        lon_expect = -8.125547604568746
        lat_expect = -14.345524111874646
        self.assertTrue(np.allclose(lon__, lon_expect, rtol=0, atol=1e-7))
        self.assertTrue(np.allclose(lat__, lat_expect, rtol=0, atol=1e-7))

    def test_get_proj_coords(self):
        from pyresample import utils
        area_id = 'test'
        area_name = 'Test area with 2x2 pixels'
        proj_id = 'test'
        x_size = 10
        y_size = 10
        area_extent = [1000000, 0, 1050000, 50000]
        proj_dict = {"proj": 'laea',
                     'lat_0': '60',
                     'lon_0': '0',
                     'a': '6371228.0', 'units': 'm'}
        area_def = utils.get_area_def(area_id,
                                      area_name,
                                      proj_id,
                                      proj_dict,
                                      x_size, y_size,
                                      area_extent)

        xcoord, ycoord = area_def.get_proj_coords()
        self.assertTrue(np.allclose(xcoord[0, :],
                                    np.array([1002500., 1007500., 1012500.,
                                              1017500., 1022500., 1027500.,
                                              1032500., 1037500., 1042500.,
                                              1047500.])))
        self.assertTrue(np.allclose(ycoord[:, 0],
                                    np.array([47500., 42500., 37500., 32500.,
                                              27500., 22500., 17500., 12500.,
                                              7500.,  2500.])))

        xcoord, ycoord = area_def.get_proj_coords(data_slice=(slice(None, None, 2),
                                                              slice(None, None, 2)))

        self.assertTrue(np.allclose(xcoord[0, :],
                                    np.array([1002500., 1012500., 1022500.,
                                              1032500., 1042500.])))
        self.assertTrue(np.allclose(ycoord[:, 0],
                                    np.array([47500., 37500., 27500., 17500.,
                                              7500.])))

    def test_get_xy_from_lonlat(self):
        """Test the function get_xy_from_lonlat"""
        from pyresample import utils
        area_id = 'test'
        area_name = 'Test area with 2x2 pixels'
        proj_id = 'test'
        x_size = 2
        y_size = 2
        area_extent = [1000000, 0, 1050000, 50000]
        proj_dict = {"proj": 'laea',
                     'lat_0': '60',
                     'lon_0': '0',
                     'a': '6371228.0', 'units': 'm'}
        area_def = utils.get_area_def(area_id,
                                      area_name,
                                      proj_id,
                                      proj_dict,
                                      x_size, y_size,
                                      area_extent)
        import pyproj
        p__ = pyproj.Proj(proj_dict)
        lon_ul, lat_ul = p__(1000000, 50000, inverse=True)
        lon_ur, lat_ur = p__(1050000, 50000, inverse=True)
        lon_ll, lat_ll = p__(1000000, 0, inverse=True)
        lon_lr, lat_lr = p__(1050000, 0, inverse=True)

        eps_lonlat = 0.01
        eps_meters = 100
        x__, y__ = area_def.get_xy_from_lonlat(lon_ul + eps_lonlat,
                                               lat_ul - eps_lonlat)
        x_expect, y_expect = 0, 0
        self.assertEqual(x__, x_expect)
        self.assertEqual(y__, y_expect)
        x__, y__ = area_def.get_xy_from_lonlat(lon_ur - eps_lonlat,
                                               lat_ur - eps_lonlat)
        self.assertEqual(x__, 1)
        self.assertEqual(y__, 0)
        x__, y__ = area_def.get_xy_from_lonlat(lon_ll + eps_lonlat,
                                               lat_ll + eps_lonlat)
        self.assertEqual(x__, 0)
        self.assertEqual(y__, 1)
        x__, y__ = area_def.get_xy_from_lonlat(lon_lr - eps_lonlat,
                                               lat_lr + eps_lonlat)
        self.assertEqual(x__, 1)
        self.assertEqual(y__, 1)

        lon, lat = p__(1025000 - eps_meters, 25000 - eps_meters, inverse=True)
        x__, y__ = area_def.get_xy_from_lonlat(lon, lat)
        self.assertEqual(x__, 0)
        self.assertEqual(y__, 1)

        lon, lat = p__(1025000 + eps_meters, 25000 - eps_meters, inverse=True)
        x__, y__ = area_def.get_xy_from_lonlat(lon, lat)
        self.assertEqual(x__, 1)
        self.assertEqual(y__, 1)

        lon, lat = p__(1025000 - eps_meters, 25000 + eps_meters, inverse=True)
        x__, y__ = area_def.get_xy_from_lonlat(lon, lat)
        self.assertEqual(x__, 0)
        self.assertEqual(y__, 0)

        lon, lat = p__(1025000 + eps_meters, 25000 + eps_meters, inverse=True)
        x__, y__ = area_def.get_xy_from_lonlat(lon, lat)
        self.assertEqual(x__, 1)
        self.assertEqual(y__, 0)

        lon, lat = p__(999000, -10, inverse=True)
        self.assertRaises(ValueError, area_def.get_xy_from_lonlat, lon, lat)
        self.assertRaises(ValueError, area_def.get_xy_from_lonlat, 0., 0.)

        # Test getting arrays back:
        lons = [lon_ll + eps_lonlat, lon_ur - eps_lonlat]
        lats = [lat_ll + eps_lonlat, lat_ur - eps_lonlat]
        x__, y__ = area_def.get_xy_from_lonlat(lons, lats)

        x_expects = np.array([0, 1])
        y_expects = np.array([1, 0])
        self.assertTrue((x__.data == x_expects).all())
        self.assertTrue((y__.data == y_expects).all())

    def test_get_area_slices(self):
        """Check area slicing."""
        from pyresample import utils

        # The area of our source data
        area_id = 'orig'
        area_name = 'Test area'
        proj_id = 'test'
        x_size = 3712
        y_size = 3712
        area_extent = (-5570248.477339745, -5561247.267842293, 5567248.074173927, 5570248.477339745)
        proj_dict = {'a': 6378169.0, 'b': 6356583.8, 'h': 35785831.0,
                     'lon_0': 0.0, 'proj': 'geos', 'units': 'm'}
        area_def = utils.get_area_def(area_id,
                                      area_name,
                                      proj_id,
                                      proj_dict,
                                      x_size, y_size,
                                      area_extent)

        # An area that is a subset of the original one
        area_to_cover = utils.get_area_def(
            'cover_subset',
            'Area to cover',
            'test',
            proj_dict,
            1000, 1000,
            area_extent=(area_extent[0] + 10000,
                         area_extent[1] + 10000,
                         area_extent[2] - 10000,
                         area_extent[3] - 10000))
        slice_x, slice_y = area_def.get_area_slices(area_to_cover)
        self.assertEqual(slice(3, 3709, None), slice_x)
        self.assertEqual(slice(3, 3709, None), slice_y)

        # An area similar to the source data but not the same
        area_id = 'cover'
        area_name = 'Area to cover'
        proj_id = 'test'
        x_size = 3712
        y_size = 3712
        area_extent = (-5570248.477339261, -5567248.074173444, 5567248.074173444, 5570248.477339261)
        proj_dict = {'a': 6378169.5, 'b': 6356583.8, 'h': 35785831.0,
                     'lon_0': 0.0, 'proj': 'geos', 'units': 'm'}

        area_to_cover = utils.get_area_def(area_id,
                                           area_name,
                                           proj_id,
                                           proj_dict,
                                           x_size, y_size,
                                           area_extent)
        slice_x, slice_y = area_def.get_area_slices(area_to_cover)
        self.assertEqual(slice(46, 3667, None), slice_x)
        self.assertEqual(slice(52, 3663, None), slice_y)

        area_to_cover = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                                {'a': 6378144.0,
                                                 'b': 6356759.0,
                                                 'lat_0': 50.00,
                                                 'lat_ts': 50.00,
                                                 'lon_0': 8.00,
                                                 'proj': 'stere'},
                                                10,
                                                10,
                                                [-1370912.72,
                                                 -909968.64,
                                                 1029087.28,
                                                 1490031.36])
        slice_x, slice_y = area_def.get_area_slices(area_to_cover)
        self.assertEqual(slice_x, slice(1610, 2343))
        self.assertEqual(slice_y, slice(158, 515, None))

        # totally different area
        area_to_cover = geometry.AreaDefinition('epsg4326', 'Global equal latitude/longitude grid for global sphere',
                                                'epsg4326',
                                                {"init": 'EPSG:4326',
                                                 'units': 'degrees'},
                                                8192,
                                                4096,
                                                [-180.0, -90.0, 180.0, 90.0])

        slice_x, slice_y = area_def.get_area_slices(area_to_cover)
        self.assertEqual(slice_x, slice(46, 3667, None))
        self.assertEqual(slice_y, slice(52, 3663, None))

    def test_get_area_slices_nongeos(self):
        """Check area slicing for non-geos projections."""
        from pyresample import utils

        # The area of our source data
        area_id = 'orig'
        area_name = 'Test area'
        proj_id = 'test'
        x_size = 3712
        y_size = 3712
        area_extent = (-5570248.477339745, -5561247.267842293, 5567248.074173927, 5570248.477339745)
        proj_dict = {'a': 6378169.0, 'b': 6356583.8, 'lat_1': 25.,
                     'lat_2': 25., 'lon_0': 0.0, 'proj': 'lcc', 'units': 'm'}
        area_def = utils.get_area_def(area_id,
                                      area_name,
                                      proj_id,
                                      proj_dict,
                                      x_size, y_size,
                                      area_extent)

        # An area that is a subset of the original one
        area_to_cover = utils.get_area_def(
            'cover_subset',
            'Area to cover',
            'test',
            proj_dict,
            1000, 1000,
            area_extent=(area_extent[0] + 10000,
                         area_extent[1] + 10000,
                         area_extent[2] - 10000,
                         area_extent[3] - 10000))
        slice_x, slice_y = area_def.get_area_slices(area_to_cover)
        self.assertEqual(slice(3, 3709, None), slice_x)
        self.assertEqual(slice(3, 3709, None), slice_y)

    def test_proj_str(self):
        from collections import OrderedDict
        proj_dict = OrderedDict()
        proj_dict['proj'] = 'stere'
        proj_dict['a'] = 6378144.0
        proj_dict['b'] = 6356759.0
        proj_dict['lat_0'] = 50.00
        proj_dict['lat_ts'] = 50.00
        proj_dict['lon_0'] = 8.00
        area = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                       proj_dict, 10, 10,
                                       [-1370912.72, -909968.64, 1029087.28,
                                        1490031.36])
        self.assertEquals(area.proj_str,
                          '+a=6378144.0 +b=6356759.0 +lat_0=50.0 +lat_ts=50.0 +lon_0=8.0 +proj=stere')
        proj_dict['no_rot'] = ''
        self.assertEquals(area.proj_str,
                          '+a=6378144.0 +b=6356759.0 +lat_0=50.0 +lat_ts=50.0 +lon_0=8.0 +no_rot +proj=stere')


def assert_np_dict_allclose(dict1, dict2):

    assert set(dict1.keys()) == set(dict2.keys())
    for key, val in dict1.items():
        try:
            np.testing.assert_allclose(val, dict2[key])
        except TypeError:
            assert(val == dict2[key])


class TestSwathDefinition(unittest.TestCase):

    """Test the SwathDefinition."""

    def test_swath(self):
        lons1 = np.fromfunction(lambda y, x: 3 + (10.0 / 100) * x, (5000, 100))
        lats1 = np.fromfunction(
            lambda y, x: 75 - (50.0 / 5000) * y, (5000, 100))

        swath_def = geometry.SwathDefinition(lons1, lats1)

        lons2, lats2 = swath_def.get_lonlats()

        self.assertFalse(id(lons1) != id(lons2) or id(lats1) != id(lats2),
                         msg='Caching of swath coordinates failed')

    def test_slice(self):
        """Test that SwathDefinitions can be sliced."""
        lons1 = np.fromfunction(lambda y, x: 3 + (10.0 / 100) * x, (5000, 100))
        lats1 = np.fromfunction(
            lambda y, x: 75 - (50.0 / 5000) * y, (5000, 100))

        swath_def = geometry.SwathDefinition(lons1, lats1)
        new_swath_def = swath_def[1000:4000, 20:40]
        self.assertTupleEqual(new_swath_def.lons.shape, (3000, 20))
        self.assertTupleEqual(new_swath_def.lats.shape, (3000, 20))

    def test_concat_1d(self):
        lons1 = np.array([1, 2, 3])
        lats1 = np.array([1, 2, 3])
        lons2 = np.array([4, 5, 6])
        lats2 = np.array([4, 5, 6])
        swath_def1 = geometry.SwathDefinition(lons1, lats1)
        swath_def2 = geometry.SwathDefinition(lons2, lats2)
        swath_def_concat = swath_def1.concatenate(swath_def2)
        expected = np.array([1, 2, 3, 4, 5, 6])
        self.assertTrue(np.array_equal(swath_def_concat.lons, expected) and
                        np.array_equal(swath_def_concat.lons, expected),
                        'Failed to concatenate 1D swaths')

    def test_concat_2d(self):
        lons1 = np.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])
        lats1 = np.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])
        lons2 = np.array([[4, 5, 6], [6, 7, 8]])
        lats2 = np.array([[4, 5, 6], [6, 7, 8]])
        swath_def1 = geometry.SwathDefinition(lons1, lats1)
        swath_def2 = geometry.SwathDefinition(lons2, lats2)
        swath_def_concat = swath_def1.concatenate(swath_def2)
        expected = np.array(
            [[1, 2, 3], [3, 4, 5], [5, 6, 7], [4, 5, 6], [6, 7, 8]])
        self.assertTrue(np.array_equal(swath_def_concat.lons, expected) and
                        np.array_equal(swath_def_concat.lons, expected),
                        'Failed to concatenate 2D swaths')

    def test_append_1d(self):
        lons1 = np.array([1, 2, 3])
        lats1 = np.array([1, 2, 3])
        lons2 = np.array([4, 5, 6])
        lats2 = np.array([4, 5, 6])
        swath_def1 = geometry.SwathDefinition(lons1, lats1)
        swath_def2 = geometry.SwathDefinition(lons2, lats2)
        swath_def1.append(swath_def2)
        expected = np.array([1, 2, 3, 4, 5, 6])
        self.assertTrue(np.array_equal(swath_def1.lons, expected) and
                        np.array_equal(swath_def1.lons, expected),
                        'Failed to append 1D swaths')

    def test_append_2d(self):
        lons1 = np.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])
        lats1 = np.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])
        lons2 = np.array([[4, 5, 6], [6, 7, 8]])
        lats2 = np.array([[4, 5, 6], [6, 7, 8]])
        swath_def1 = geometry.SwathDefinition(lons1, lats1)
        swath_def2 = geometry.SwathDefinition(lons2, lats2)
        swath_def1.append(swath_def2)
        expected = np.array(
            [[1, 2, 3], [3, 4, 5], [5, 6, 7], [4, 5, 6], [6, 7, 8]])
        self.assertTrue(np.array_equal(swath_def1.lons, expected) and
                        np.array_equal(swath_def1.lons, expected),
                        'Failed to append 2D swaths')

    def test_swath_equal(self):
        """Test swath equality."""
        lons = np.array([1.2, 1.3, 1.4, 1.5])
        lats = np.array([65.9, 65.86, 65.82, 65.78])
        swath_def = geometry.SwathDefinition(lons, lats)
        swath_def2 = geometry.SwathDefinition(lons, lats)
        # Identical lons and lats
        self.assertFalse(
            swath_def != swath_def2, 'swath_defs are not equal as expected')
        # Identical objects
        self.assertFalse(
            swath_def != swath_def, 'swath_defs are not equal as expected')

        lons = np.array([1.2, 1.3, 1.4, 1.5])
        lats = np.array([65.9, 65.86, 65.82, 65.78])
        lons2 = np.array([1.2, 1.3, 1.4, 1.5])
        lats2 = np.array([65.9, 65.86, 65.82, 65.78])
        swath_def = geometry.SwathDefinition(lons, lats)
        swath_def2 = geometry.SwathDefinition(lons2, lats2)
        # different arrays, same values
        self.assertFalse(
            swath_def != swath_def2, 'swath_defs are not equal as expected')

        lons = np.array([1.2, 1.3, 1.4, np.nan])
        lats = np.array([65.9, 65.86, 65.82, np.nan])
        lons2 = np.array([1.2, 1.3, 1.4, np.nan])
        lats2 = np.array([65.9, 65.86, 65.82, np.nan])
        swath_def = geometry.SwathDefinition(lons, lats)
        swath_def2 = geometry.SwathDefinition(lons2, lats2)
        # different arrays, same values, with nans
        self.assertFalse(
            swath_def != swath_def2, 'swath_defs are not equal as expected')

        try:
            import dask.array as da
            lons = da.from_array(np.array([1.2, 1.3, 1.4, np.nan]), chunks=2)
            lats = da.from_array(np.array([65.9, 65.86, 65.82, np.nan]), chunks=2)
            lons2 = da.from_array(np.array([1.2, 1.3, 1.4, np.nan]), chunks=2)
            lats2 = da.from_array(np.array([65.9, 65.86, 65.82, np.nan]), chunks=2)
            swath_def = geometry.SwathDefinition(lons, lats)
            swath_def2 = geometry.SwathDefinition(lons2, lats2)
            # different arrays, same values, with nans
            self.assertFalse(
                swath_def != swath_def2, 'swath_defs are not equal as expected')
        except ImportError:
            pass

        try:
            import xarray as xr
            lons = xr.DataArray(np.array([1.2, 1.3, 1.4, np.nan]))
            lats = xr.DataArray(np.array([65.9, 65.86, 65.82, np.nan]))
            lons2 = xr.DataArray(np.array([1.2, 1.3, 1.4, np.nan]))
            lats2 = xr.DataArray(np.array([65.9, 65.86, 65.82, np.nan]))
            swath_def = geometry.SwathDefinition(lons, lats)
            swath_def2 = geometry.SwathDefinition(lons2, lats2)
            # different arrays, same values, with nans
            self.assertFalse(
                swath_def != swath_def2, 'swath_defs are not equal as expected')

        except ImportError:
            pass

    def test_swath_not_equal(self):
        """Test swath inequality."""
        lats1 = np.array([65.9, 65.86, 65.82, 65.78])
        lons = np.array([1.2, 1.3, 1.4, 1.5])
        lats2 = np.array([65.91, 65.85, 65.80, 65.75])
        swath_def = geometry.SwathDefinition(lons, lats1)
        swath_def2 = geometry.SwathDefinition(lons, lats2)
        self.assertFalse(
            swath_def == swath_def2, 'swath_defs are not expected to be equal')

    def test_compute_omerc_params(self):
        """Test omerc parameters computation."""
        lats = np.array([[85.23900604248047, 62.256004333496094, 35.58000183105469],
                         [80.84000396728516, 60.74200439453125, 34.08500289916992],
                         [67.07600402832031, 54.147003173828125, 30.547000885009766]]).T

        lons = np.array([[-90.67900085449219, -21.565000534057617, -21.525001525878906],
                         [79.11000061035156, 7.284000396728516, -5.107000350952148],
                         [81.26400756835938, 29.672000885009766, 10.260000228881836]]).T

        area = geometry.SwathDefinition(lons, lats)
        proj_dict = {'lonc': -11.391744043133668, 'ellps': 'WGS84',
                     'proj': 'omerc', 'alpha': 9.185764390923012,
                     'gamma': 0, 'lat_0': -0.2821013754097188}
        assert_np_dict_allclose(area._compute_omerc_parameters('WGS84'),
                                proj_dict)

    def test_get_edge_lonlats(self):
        """Test the `get_edge_lonlats` functionality."""
        lats = np.array([[85.23900604248047, 62.256004333496094, 35.58000183105469],
                         [80.84000396728516, 60.74200439453125, 34.08500289916992],
                         [67.07600402832031, 54.147003173828125, 30.547000885009766]]).T

        lons = np.array([[-90.67900085449219, -21.565000534057617, -21.525001525878906],
                         [79.11000061035156, 7.284000396728516, -5.107000350952148],
                         [81.26400756835938, 29.672000885009766, 10.260000228881836]]).T

        area = geometry.SwathDefinition(lons, lats)
        lons, lats = area.get_edge_lonlats()

        np.testing.assert_allclose(lons, [-90.67900085, 79.11000061,  81.26400757,
                                          81.26400757, 29.67200089, 10.26000023,
                                          10.26000023, -5.10700035, -21.52500153,
                                          -21.52500153, -21.56500053, -90.67900085])
        np.testing.assert_allclose(lats, [85.23900604, 80.84000397, 67.07600403,
                                          67.07600403, 54.14700317, 30.54700089,
                                          30.54700089, 34.0850029, 35.58000183,
                                          35.58000183, 62.25600433,  85.23900604])

        lats = np.array([[80., 80., 80.],
                         [80., 90., 80],
                         [80., 80., 80.]]).T

        lons = np.array([[-45., 0., 45.],
                         [-90, 0., 90.],
                         [-135., -180., 135.]]).T

        area = geometry.SwathDefinition(lons, lats)
        lons, lats = area.get_edge_lonlats()

        np.testing.assert_allclose(lons, [-45., -90., -135., -135., -180., 135.,
                                          135., 90., 45., 45., 0., -45.])
        np.testing.assert_allclose(lats, [80., 80., 80., 80., 80., 80., 80.,
                                          80., 80., 80., 80., 80.])

    def test_compute_optimal_bb(self):
        """Test computing the bb area."""
        lats = np.array([[85.23900604248047, 62.256004333496094, 35.58000183105469],
                         [80.84000396728516, 60.74200439453125, 34.08500289916992],
                         [67.07600402832031, 54.147003173828125, 30.547000885009766]]).T

        lons = np.array([[-90.67900085449219, -21.565000534057617, -21.525001525878906],
                         [79.11000061035156, 7.284000396728516, -5.107000350952148],
                         [81.26400756835938, 29.672000885009766, 10.260000228881836]]).T

        area = geometry.SwathDefinition(lons, lats)

        res = area.compute_optimal_bb_area({'proj': 'omerc', 'ellps': 'WGS84'})

        np.testing.assert_allclose(res.area_extent, [-2348379.728104, 2284625.526467,
                                                     2432121.058435, 11719235.223912])
        proj_dict = {'gamma': 0.0, 'lonc': -11.391744043133668,
                     'ellps': 'WGS84', 'proj': 'omerc',
                     'alpha': 9.185764390923012, 'lat_0': -0.2821013754097188}
        assert_np_dict_allclose(res.proj_dict, proj_dict)
        self.assertEqual(res.shape, (3, 3))


class TestStackedAreaDefinition(unittest.TestCase):

    """Test the StackedAreaDefition."""

    def test_append(self):
        """Appending new definitions."""
        area1 = geometry.AreaDefinition("area1", 'area1', "geosmsg",
                                        {'a': '6378169.0', 'b': '6356583.8',
                                         'h': '35785831.0', 'lon_0': '0.0',
                                         'proj': 'geos', 'units': 'm'},
                                        5568, 464,
                                        (3738502.0095458371, 3715498.9194295374,
                                            -1830246.0673044831, 3251436.5796920112)
                                        )

        area2 = geometry.AreaDefinition("area2", 'area2', "geosmsg",
                                        {'a': '6378169.0', 'b': '6356583.8',
                                         'h': '35785831.0', 'lon_0': '0.0',
                                         'proj': 'geos', 'units': 'm'},
                                        5568, 464,
                                        (3738502.0095458371, 4179561.259167064,
                                            -1830246.0673044831, 3715498.9194295374)
                                        )

        adef = geometry.StackedAreaDefinition(area1, area2)
        self.assertEqual(len(adef.defs), 1)
        self.assertTupleEqual(adef.defs[0].area_extent,
                              (3738502.0095458371, 4179561.259167064,
                               -1830246.0673044831, 3251436.5796920112))

        # same

        area3 = geometry.AreaDefinition("area3", 'area3', "geosmsg",
                                        {'a': '6378169.0', 'b': '6356583.8',
                                         'h': '35785831.0', 'lon_0': '0.0',
                                         'proj': 'geos', 'units': 'm'},
                                        5568, 464,
                                        (3738502.0095458371, 3251436.5796920112,
                                         -1830246.0673044831, 2787374.2399544837))
        adef.append(area3)
        self.assertEqual(len(adef.defs), 1)
        self.assertTupleEqual(adef.defs[0].area_extent,
                              (3738502.0095458371, 4179561.259167064,
                               -1830246.0673044831, 2787374.2399544837))

        self.assertIsInstance(adef.squeeze(), geometry.AreaDefinition)

        # transition
        area4 = geometry.AreaDefinition("area4", 'area4', "geosmsg",
                                        {'a': '6378169.0', 'b': '6356583.8',
                                         'h': '35785831.0', 'lon_0': '0.0',
                                         'proj': 'geos', 'units': 'm'},
                                        5568, 464,
                                        (5567747.7409681147, 2787374.2399544837,
                                         -1000.3358822065015, 2323311.9002169576))

        adef.append(area4)
        self.assertEqual(len(adef.defs), 2)
        self.assertTupleEqual(adef.defs[-1].area_extent,
                              (5567747.7409681147, 2787374.2399544837,
                               -1000.3358822065015, 2323311.9002169576))

        self.assertEqual(adef.y_size, 4 * 464)
        self.assertIsInstance(adef.squeeze(), geometry.StackedAreaDefinition)

        adef2 = geometry.StackedAreaDefinition()
        self.assertEqual(len(adef2.defs), 0)

        adef2.append(adef)
        self.assertEqual(len(adef2.defs), 2)
        self.assertTupleEqual(adef2.defs[-1].area_extent,
                              (5567747.7409681147, 2787374.2399544837,
                               -1000.3358822065015, 2323311.9002169576))

        self.assertEqual(adef2.y_size, 4 * 464)

    def test_get_lonlats(self):
        """Test get_lonlats on StackedAreaDefinition."""
        area3 = geometry.AreaDefinition("area3", 'area3', "geosmsg",
                                        {'a': '6378169.0', 'b': '6356583.8',
                                         'h': '35785831.0', 'lon_0': '0.0',
                                         'proj': 'geos', 'units': 'm'},
                                        5568, 464,
                                        (3738502.0095458371, 3251436.5796920112,
                                         -1830246.0673044831, 2787374.2399544837))

        # transition
        area4 = geometry.AreaDefinition("area4", 'area4', "geosmsg",
                                        {'a': '6378169.0', 'b': '6356583.8',
                                         'h': '35785831.0', 'lon_0': '0.0',
                                         'proj': 'geos', 'units': 'm'},
                                        5568, 464,
                                        (5567747.7409681147, 2787374.2399544837,
                                         -1000.3358822065015, 2323311.9002169576))

        final_area = geometry.StackedAreaDefinition(area3, area4)
        self.assertEqual(len(final_area.defs), 2)
        lons, lats = final_area.get_lonlats()
        lons0, lats0 = final_area.defs[0].get_lonlats()
        lons1, lats1 = final_area.defs[1].get_lonlats()
        np.testing.assert_allclose(lons[:464, :], lons0)
        np.testing.assert_allclose(lons[464:, :], lons1)
        np.testing.assert_allclose(lats[:464, :], lats0)
        np.testing.assert_allclose(lats[464:, :], lats1)

    def test_combine_area_extents(self):
        """Test combination of area extents."""
        area1 = MagicMock()
        area1.area_extent = (1, 2, 3, 4)
        area2 = MagicMock()
        area2.area_extent = (1, 6, 3, 2)
        res = combine_area_extents_vertical(area1, area2)
        self.assertListEqual(res, [1, 6, 3, 4])

        area1 = MagicMock()
        area1.area_extent = (1, 2, 3, 4)
        area2 = MagicMock()
        area2.area_extent = (1, 4, 3, 6)
        res = combine_area_extents_vertical(area1, area2)
        self.assertListEqual(res, [1, 2, 3, 6])

    def test_append_area_defs_fail(self):
        """Fail appending areas."""
        area1 = MagicMock()
        area1.proj_dict = {"proj": 'A'}
        area1.x_size = 4
        area1.y_size = 5
        area2 = MagicMock()
        area2.proj_dict = {'proj': 'B'}
        area2.x_size = 4
        area2.y_size = 6
        # res = combine_area_extents_vertical(area1, area2)
        self.assertRaises(IncompatibleAreas,
                          concatenate_area_defs, area1, area2)

    @patch('pyresample.geometry.AreaDefinition')
    def test_append_area_defs(self, adef):
        """Test appending area definitions."""
        x_size = random.randrange(6425)
        area1 = MagicMock()
        area1.area_extent = (1, 2, 3, 4)
        area1.proj_dict = {"proj": 'A'}
        area1.y_size = random.randrange(6425)
        area1.x_size = x_size

        area2 = MagicMock()
        area2.area_extent = (1, 4, 3, 6)
        area2.proj_dict = {"proj": 'A'}
        area2.y_size = random.randrange(6425)
        area2.x_size = x_size

        concatenate_area_defs(area1, area2)
        area_extent = [1, 2, 3, 6]
        y_size = area1.y_size + area2.y_size
        adef.assert_called_once_with(area1.area_id, area1.name, area1.proj_id,
                                     area1.proj_dict, area1.x_size, y_size,
                                     area_extent)

    def test_from_params(self):
        """Test from_params and the four sub-methods that call it in AreaDefinition."""
        from xarray import DataArray
        from pyresample.geometry import AreaDefinition
        from pyresample.geometry import DynamicAreaDefinition
        from pyresample import utils

        def verify_area(area_def, area_extent=(-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625),
                        shape=(425, 850)):
            """Makes sure that the area definitions created are correct."""
            self.assertTrue(isinstance(area_def, AreaDefinition))
            self.assertTrue(np.allclose(area_def.area_extent, area_extent))
            self.assertEqual(area_def.shape, shape)

        area_id = 'ease_sh'
        name = 'Antarctic EASE grid'
        proj4_list = [{'a': '6371228.0', 'units_list': 'm', 'lon_0': '0', 'proj': 'laea', 'lat_0': '-90'},
                      '+a=6371228.0 +units_list=m +lon_0=0 +proj=laea +lat_0=-90']
        proj_id = 'ease_sh'
        shape = (425, 850)
        top_left_extent = (-5326849.0625, 5326849.0625)
        center_list = [[0, 0], 'a', (1, 2, 3)]
        area_extent = (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)
        pixel_size = (12533.7625, 25067.525)
        radius = [5326849.0625, 5326849.0625]
        units_list = ['meters', 'degrees', 'radians']
        # reducing the length of AreaDefinition.from_params makes lines much shorter.
        area = utils.from_params

        # Tests that incorrect lists do not create an area definition, that both proj4 strings and dicts are accepted,
        # and that degrees, meters, and radians all create the same area definition.
        # area_list used to check that areas are all correct at the end.
        area_list = []
        for proj4 in proj4_list:
            for units in units_list:
                for center in center_list:
                    # essentials = center, radius, top_left_extent, pixel_size, area_extent.
                    if 'm' in units:
                        # Meters.
                        essentials = [[0, 0], [5326849.0625, 5326849.0625], (-5326849.0625, 5326849.0625),
                                      (12533.7625, 25067.525), (-5326849.0625, -5326849.0625, 5326849.0625,
                                                                5326849.0625)]
                    elif 'deg' in units:
                        # Degrees.
                        essentials = [(0.0, -90.0), (45.0, -17.516001139327766), (-45.0, -17.516001139327766),
                                      (26.56505117707799, -89.74796184090499), (-135.0, -17.516001139327766, 45.0,
                                                                                -17.516001139327766)]
                    else:
                        # Radians.
                        essentials = [(0.0, -1.5707963267948966), (0.7853981633974483, -0.30571189166434753),
                                      (-0.7853981633974483, -0.30571189166434753),
                                      (0.4636476090008061, -1.5663974310780233),
                                      (-2.356194490192345, -0.30571189166434753, 0.7853981633974483,
                                       -0.30571189166434753)]
                    # If center is valid, use it.
                    if len(center) == 2:
                        center = essentials[0]
                    try:
                        area_list.append(area(name, proj4, proj_id=proj_id, top_left_extent=essentials[2],
                                              center=center, area_extent=essentials[4], pixel_size=essentials[3],
                                              radius=essentials[1], area_id=area_id, units=units))
                    except ValueError:
                        pass
        self.assertEqual(len(area_list), 6)

        # Tests that specifying units through xarrays works.
        area_list.append(area(name, proj4_list[1], shape=shape,
                                                    area_extent=DataArray((-135.0, -17.516001139327766,
                                                                           45.0, -17.516001139327766),
                                                                          attrs={'units': 'degrees'})))
        # Tests area functions 1-A and 2-A.
        area_list.append(area(name, proj4_list[1], pixel_size=pixel_size, area_extent=area_extent))
        # Tests area function 1-B.
        area_list.append(area(name, proj4_list[1], shape=shape, center=center_list[0], top_left_extent=top_left_extent))
        # Tests area function 1-C.
        area_list.append(area(name, proj4_list[1], shape=shape, center=center_list[0], radius=radius))
        # Tests area function 1-D.
        area_list.append(area(name, proj4_list[1], shape=shape, radius=radius, top_left_extent=top_left_extent))
        # Tests all 4 user cases.
        area_list.append(AreaDefinition.from_extent(name, proj4_list[1], area_extent, shape))
        area_list.append(AreaDefinition.from_circle(name, proj4_list[1], center_list[0], radius, pixel_size))
        area_list.append(AreaDefinition.from_area_of_interest(name, proj4_list[1], center_list[0], pixel_size, shape))
        area_list.append(AreaDefinition.from_geotiff(name, proj4_list[1], top_left_extent, pixel_size, shape))

        # Checks every area definition made
        for area_def in area_list:
            verify_area(area_def)

        # Makes sure if shape or area_extent is found/given, a DynamicAreaDefinition is made.
        self.assertTrue(isinstance(area(name, proj4_list[1], shape=shape), DynamicAreaDefinition))
        self.assertTrue(isinstance(area(name, proj4_list[1], area_extent=area_extent), DynamicAreaDefinition))


class TestDynamicAreaDefinition(unittest.TestCase):

    """Test the DynamicAreaDefinition class."""

    def test_freeze(self):
        """Test freezing the area."""
        area = geometry.DynamicAreaDefinition('test_area', 'A test area',
                                              {'proj': 'laea'})
        lons = [10, 10, 22, 22]
        lats = [50, 66, 66, 50]
        result = area.freeze((lons, lats),
                             resolution=3000,
                             proj_info={'lon0': 16, 'lat0': 58})

        np.testing.assert_allclose(result.area_extent, (538546.7274949469,
                                                        5380808.879250369,
                                                        1724415.6519203288,
                                                        6998895.701001488))
        self.assertEqual(result.proj_dict['lon0'], 16)
        self.assertEqual(result.proj_dict['lat0'], 58)
        self.assertEqual(result.x_size, 395)
        self.assertEqual(result.y_size, 539)

    def test_freeze_with_bb(self):
        """Test freezing the area with bounding box computation."""
        area = geometry.DynamicAreaDefinition('test_area', 'A test area',
                                              {'proj': 'omerc'},
                                              optimize_projection=True)
        lons = [[10, 12.1, 14.2, 16.3],
                [10, 12, 14, 16],
                [10, 11.9, 13.8, 15.7]]
        lats = [[66, 67, 68, 69.],
                [58, 59, 60, 61],
                [50, 51, 52, 53]]
        sdef = geometry.SwathDefinition(lons, lats)
        result = area.freeze(sdef,
                             resolution=1000)
        np.testing.assert_allclose(result.area_extent,
                                   [-336277.698941, 5047207.008079,
                                    192456.651909, 8215588.023806])
        self.assertEqual(result.x_size, 4)
        self.assertEqual(result.y_size, 3)

    def test_compute_domain(self):
        """Test computing size and area extent."""
        area = geometry.DynamicAreaDefinition('test_area', 'A test area',
                                              {'proj': 'laea'})
        corners = [1, 1, 9, 9]
        self.assertRaises(ValueError, area.compute_domain, corners, 1, 1)

        area_extent, x_size, y_size = area.compute_domain(corners, size=(5, 5))
        self.assertTupleEqual(area_extent, (0, 0, 10, 10))
        self.assertEqual(x_size, 5)
        self.assertEqual(y_size, 5)

        area_extent, x_size, y_size = area.compute_domain(corners, resolution=2)
        self.assertTupleEqual(area_extent, (0, 0, 10, 10))
        self.assertEqual(x_size, 5)
        self.assertEqual(y_size, 5)


class TestCrop(unittest.TestCase):

    """Test the area helpers."""

    def test_get_geostationary_bbox(self):
        """Get the geostationary bbox."""

        geos_area = MagicMock()
        lon_0 = 0
        geos_area.proj_dict = {'a': 6378169.00,
                               'b': 6356583.80,
                               'h': 35785831.00,
                               'lon_0': lon_0,
                               'proj': 'geos'}
        geos_area.area_extent = [-5500000., -5500000., 5500000., 5500000.]

        lon, lat = geometry.get_geostationary_bounding_box(geos_area, 20)
        # This musk be equal to lon.
        elon = np.array([-79.23372832, -77.9694809, -74.55229623, -67.32816598,
                         -41.45591465, 41.45591465, 67.32816598, 74.55229623,
                         77.9694809, 79.23372832, 79.23372832, 77.9694809,
                         74.55229623, 67.32816598, 41.45591465, -41.45591465,
                         -67.32816598, -74.55229623, -77.9694809, -79.23372832])
        elat = np.array([6.94302533e-15, 1.97333299e+01, 3.92114217e+01, 5.82244715e+01,
                         7.52409201e+01, 7.52409201e+01, 5.82244715e+01, 3.92114217e+01,
                         1.97333299e+01, -0.00000000e+00, -6.94302533e-15, -1.97333299e+01,
                         -3.92114217e+01, -5.82244715e+01, -7.52409201e+01, -7.52409201e+01,
                         -5.82244715e+01, -3.92114217e+01, -1.97333299e+01, 0.0])

        np.testing.assert_allclose(lon, elon)
        np.testing.assert_allclose(lat, elat)

        geos_area = MagicMock()
        lon_0 = 10
        geos_area.proj_dict = {'a': 6378169.00,
                               'b': 6356583.80,
                               'h': 35785831.00,
                               'lon_0': lon_0,
                               'proj': 'geos'}
        geos_area.area_extent = [-5500000., -5500000., 5500000., 5500000.]

        lon, lat = geometry.get_geostationary_bounding_box(geos_area, 20)
        np.testing.assert_allclose(lon, elon + lon_0)

    def test_get_geostationary_angle_extent(self):
        """Get max geostationary angles."""
        geos_area = MagicMock()
        geos_area.proj_dict = {'a': 6378169.00,
                               'b': 6356583.80,
                               'h': 35785831.00}

        expected = (0.15185342867090912, 0.15133555510297725)

        np.testing.assert_allclose(expected,
                                   geometry.get_geostationary_angle_extent(geos_area))

        geos_area.proj_dict = {'a': 1000.0,
                               'b': 1000.0,
                               'h': np.sqrt(2) * 1000.0 - 1000.0}

        expected = (np.deg2rad(45), np.deg2rad(45))

        np.testing.assert_allclose(expected,
                                   geometry.get_geostationary_angle_extent(geos_area))

    def test_sub_area(self):
        """Sub area slicing."""
        area = geometry.AreaDefinition('areaD', 'Europe (3km, HRV, VTC)', 'areaD',
                                       {'a': '6378144.0',
                                        'b': '6356759.0',
                                        'lat_0': '50.00',
                                        'lat_ts': '50.00',
                                        'lon_0': '8.00',
                                        'proj': 'stere'},
                                       800,
                                       800,
                                       [-1370912.72,
                                        -909968.64000000001,
                                        1029087.28,
                                        1490031.3600000001])
        res = area[slice(20, 720), slice(100, 500)]
        self.assertTrue(np.allclose((-1070912.72, -669968.6399999999,
                                     129087.28000000003, 1430031.36),
                                    res.area_extent))
        self.assertEqual(res.shape, (700, 400))


def suite():
    """The test suite.
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test))
    mysuite.addTest(loader.loadTestsFromTestCase(TestStackedAreaDefinition))
    mysuite.addTest(loader.loadTestsFromTestCase(TestDynamicAreaDefinition))
    mysuite.addTest(loader.loadTestsFromTestCase(TestSwathDefinition))
    mysuite.addTest(loader.loadTestsFromTestCase(TestCrop))

    return mysuite


if __name__ == '__main__':
    unittest.main()
