"""Retrieve images for VIIRS Nighttime overlay
"""
import datetime
import dateutil.parser
import imageio
import json
import os
import threading
import urllib
import numpy as np

_base_url = "https://gibs-b.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi?"

_concurrent_download = 20
_concurrent_semaphore = threading.Semaphore(_concurrent_download)

_mem_cache = {}
_mem_cache_limit = 1000

_file_cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
	"getimage.cache")
_file_cache_lock = threading.Lock()

try:
	os.mkdir(_file_cache_path)
except OSError:
	if not os.path.isdir(_file_cache_path):
		raise

def _build_url(tileMatrix, tileCol, tileRow, **kwargs):
	parameters = {
		"layer": "VIIRS_SNPP_DayNightBand_ENCC",
		"style": "default",
		"tilematrixset": "500m",
		"Service": "WMTS",
		"Request": "GetTile",
		"Version": "1.0.0",
		"Format": "image/png",
		"TileMatrix": tileMatrix,
		"TileCol": tileCol,
		"TileRow": tileRow
	}

	if "date" in kwargs:
		parameters["TIME"] = kwargs["date"]
		del kwargs["date"]

	parameters.update(kwargs)

	return _base_url + urllib.urlencode(parameters)

def _mem_cache_dec(layer_name):
	def _real_mem_cache_dec(func):
		def f(tileMatrix, tileCol, tileRow, date=None):
			key = "%s_%s_%s_%s_%s" % (layer_name, tileMatrix, tileCol, tileRow, date)
			try:
				return _mem_cache[key]
			except KeyError:
				while len(_mem_cache) >= _mem_cache_limit:
					_mem_cache.popitem()

				image = func(tileMatrix, tileCol, tileRow, date)
				_mem_cache[key] = image
				return image
		return f
	return _real_mem_cache_dec

def _file_cache_dec(layer_name):
	def _real_file_cache_dec(func):
		def f(tileMatrix, tileCol, tileRow, date=None):
			key = "%s_%s_%s_%s_%s" % (layer_name, tileMatrix, tileCol, tileRow, date)
			fname = os.path.join(_file_cache_path, "%s.png" % key)
			try:
				with _file_cache_lock:
					return imageio.imread(fname)
			except (OSError, IOError):
				image = func(tileMatrix, tileCol, tileRow, date)
				with _file_cache_lock:
					imageio.imwrite(fname, image)
				return image
		return f
	return _real_file_cache_dec

@_mem_cache_dec("VIIRS_SNPP_DayNightBand_ENCC")
@_file_cache_dec("VIIRS_SNPP_DayNightBand_ENCC")
def _get_image(tileMatrix, tileCol, tileRow, date):
	"""Get a matrix for a given date. Result is cached.

	Args:
	    tileMatrix (int, optional): Zoom in level
	    tileCol (int, optional): Column
	    tileRow (int, optional): Row
	    date (str, optional): Date string in iso format

	Returns:
	    Image: A numpy matrix
	"""
	url = _build_url(
		tileMatrix=tileMatrix,
		tileCol=tileCol,
		tileRow=tileRow,
		date=date
	)

	print url

	with _concurrent_semaphore:
		return imageio.imread(url)

def get_image(tileMatrix=5, tileCol=6, tileRow=5, date="2017-10-31", sea="smooth"):
	"""Get a matrix for a tile. Data for sea area can be masked out.

	If sea is set to "smooth", a numpy.array is returned. Pixels for sea area
	set to 0. Coast lines are properly anti-aliased.

	If sea is set to "masked", a numpy.ma.array is returned with pixels of sea
	area masked.

	If sea is set to anything else, the original data is returned.

	Args:
	    tileMatrix (int, optional): Zoom in level
	    tileCol (int, optional): Column
	    tileRow (int, optional): Row
	    date (str, optional): Date string in iso format
	    sea (str, optional): Specify how sea pixels are handled. See above.

	Returns:
	    TYPE: Description
	"""
	image = _get_image(
		tileMatrix=tileMatrix,
		tileCol=tileCol,
		tileRow=tileRow,
		date=date
	)

	if sea in ["smooth", "masked"]:
		land_mask = get_mask(
			tileMatrix=tileMatrix,
			tileCol=tileCol,
			tileRow=tileRow
		)

	if sea == "smooth":
		return np.multiply(image.astype(np.float), land_mask) / 255.0
	elif sea == "masked":
		sea_mask = np.invert(land_mask)
		return np.ma.masked_where(land_mask < 128, image)
	else:
		return image

@_mem_cache_dec("OSM_Land_Mask")
@_file_cache_dec("OSM_Land_Mask")
def _get_mask(tileMatrix=5, tileCol=6, tileRow=5, date=None):
	url = _build_url(
		tileMatrix=tileMatrix,
		tileCol=tileCol,
		tileRow=tileRow,

		layer="OSM_Land_Mask",
		tilematrixset="250m"
	)

	with _concurrent_semaphore:
		return imageio.imread(url)

def get_mask(tileMatrix=5, tileCol=6, tileRow=5):
	"""Get land mask for a tile

	Args:
	    tileMatrix (int, optional): Description
	    tileCol (int, optional): Description
	    tileRow (int, optional): Description

	Returns:
	    np.array: 512x512 uint8 array. 255 means land, 0 means sea. Coast line
	              is anti-aliased, so it can be anything between 1~254
	"""
	image_mask = _get_mask(
		tileMatrix=tileMatrix,
		tileCol=tileCol,
		tileRow=tileRow
	)

	array_mask = image_mask.take(-1, axis=2)
	return array_mask

class _GetImageThread(threading.Thread):
	def __init__(self, **kwargs):
		super(_GetImageThread, self).__init__()

		self.kwargs = kwargs
		self._result = None

	def run(self):
		self._result = get_image(**self.kwargs)

	@property
	def result(self):
		self.join()
		return self._result

def get_image_date_range(
		start_date="2017-10-01",
		num_days=None,
		end_date="2017-10-10",
		**kwargs):
	"""Get a list of matrixes for a date range.

	At least one of num_days and end_date should be set. If both are set,
	num_days takes precedence over end_date.

	Args:
	    start_date (str, optional): start date
	    num_days (int, optional): number of days
	    end_date (str, optional): end date
	    **kwargs: Extra parameters passed to get_image

	Returns:
	    list: list of image matrixes

	Raises:
	    ValueError: Neither of num_days and end_date is set.
	"""
	start_date = dateutil.parser.parse(start_date).date()
	if end_date:
		end_date = dateutil.parser.parse(end_date).date()

	if num_days:
		end_date = start_date + datetime.timedelta(days=num_days)

	if not end_date:
		raise ValueError("num_days and end_date can not be both None")


	threads = []
	date = start_date
	while date <= end_date:
		thread = _GetImageThread(date=date.isoformat(), **kwargs)

		thread.start()
		threads.append(thread)

		date += datetime.timedelta(days=1)

	return [thread.result for thread in threads]
