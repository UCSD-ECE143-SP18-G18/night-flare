"""Retrieve images for VIIRS Nighttime overlay
"""
import datetime
import dateutil.parser
import imageio
import json
import os
import threading
import urllib

_base_url = "https://gibs-b.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi?"

_concurrent_download = 20
_concurrent_semaphore = threading.Semaphore(_concurrent_download)

_mem_cache = {}
_mem_cache_limit = 1000

_file_cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
	"getimage.cache")

try:
	os.mkdir(_file_cache_path)
except OSError:
	if not os.path.isdir(_file_cache_path):
		raise

def _build_url(tileMatrix, tileCol, tileRow, date):
	parameters = {
		"layer": "VIIRS_SNPP_DayNightBand_ENCC",
		"style": "default",
		"tilematrixset": "500m",
		"Service": "WMTS",
		"Request": "GetTile",
		"Version": "1.0.0",
		"Format": "image/png",
		"TIME": date,
		"TileMatrix": tileMatrix,
		"TileCol": tileCol,
		"TileRow": tileRow
	}

	return _base_url + urllib.urlencode(parameters)

def _mem_cache_dec(func):
	def f(tileMatrix, tileCol, tileRow, date):
		key = "%s_%s_%s_%s" % (tileMatrix, tileCol, tileRow, date)
		try:
			return _mem_cache[key]
		except KeyError:
			while len(_mem_cache) >= _mem_cache_limit:
				_mem_cache.popitem()

			image = func(tileMatrix, tileCol, tileRow, date)
			_mem_cache[key] = image
			return image
	return f

def _file_cache_dec(func):
	def f(tileMatrix, tileCol, tileRow, date):
		key = "%s_%s_%s_%s" % (tileMatrix, tileCol, tileRow, date)
		fname = os.path.join(_file_cache_path, "%s.png" % key)
		try:
			return imageio.imread(fname)
		except OSError:
			image = func(tileMatrix, tileCol, tileRow, date)
			imageio.imwrite(fname, image)
			return image
	return f

@_mem_cache_dec
@_file_cache_dec
def get_image(tileMatrix=5, tileCol=6, tileRow=5, date="2017-10-31"):
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

	with _concurrent_semaphore:
		return imageio.imread(url)

class _GetImageThread(threading.Thread):
	def __init__(self, tileMatrix, tileCol, tileRow, date):
		super(_GetImageThread, self).__init__()

		self.tileMatrix = tileMatrix
		self.tileCol = tileCol
		self.tileRow = tileRow
		self.date = date

		self._result = None

	def run(self):
		self._result = get_image(
			tileMatrix=self.tileMatrix,
			tileCol=self.tileCol,
			tileRow=self.tileRow,
			date=self.date
		)

	@property
	def result(self):
		self.join()
		return self._result

def get_image_date_range(
		tileMatrix=5,
		tileCol=6,
		tileRow=5,
		start_date="2017-10-01",
		num_days=None,
		end_date="2017-10-10"):
	"""Get a list of matrixes for a date range.

	At least one of num_days and end_date should be set. If both are set,
	num_days takes precedence over end_date.

	Args:
	    tileMatrix (int, optional): Zoom in level
	    tileCol (int, optional): Column
	    tileRow (int, optional): Row
	    start_date (str, optional): start date
	    num_days (int, optional): number of days
	    end_date (str, optional): end date

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
		thread = _GetImageThread(
			tileMatrix=tileMatrix,
			tileCol=tileCol,
			tileRow=tileRow,
			date=date.isoformat()
		)

		thread.start()
		threads.append(thread)

		date += datetime.timedelta(days=1)

	return [thread.result for thread in threads]
