"""Retrieve images for VIIRS Nighttime overlay
"""
import urllib
import imageio
import json
import datetime
import dateutil.parser

_base_url = "https://gibs-b.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi?"

_cache = {}
_cache_limit = 1000

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

def _get_image(tileMatrix, tileCol, tileRow, date):
	url = _build_url(
		tileMatrix=tileMatrix,
		tileCol=tileCol,
		tileRow=tileRow,
		date=date
	)

	return imageio.imread(url)

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
	key_dict = {
		"tileMatrix": tileMatrix,
		"tileCol": tileCol,
		"tileRow": tileRow,
		"date": date
	}

	key = json.dumps(key_dict)

	try:
		return _cache[key]
	except KeyError:
		while len(_cache) >= _cache_limit:
			_cache.popitem()

		image = _get_image(**key_dict)
		_cache[key] = image
		return image

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


	ret = []
	date = start_date
	while date <= end_date:
		ret.append(get_image(
			tileMatrix=tileMatrix,
			tileCol=tileCol,
			tileRow=tileRow,
			date=date.isoformat()
		))

		date += datetime.timedelta(days=1)

	return ret


