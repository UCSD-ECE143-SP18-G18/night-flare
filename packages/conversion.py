import numpy as np
import pandas as pd

def get_coordinates(tileMatrix, tileCol, tileRow):
    """
    Convert from TWMS format to coordinates (latitude, longtitude)
    
    Args:
        tileMatrix (int, optional): Zoom in level
        tileCol (int, optional): Column
        tileRow (int, optional): Row
        date (str, optional): Date string in iso format
    Returns:
        latitude: The latitude at upper left conner of the tile.
        longtitude: The longtitude at the upper left conner of the tile.
    """
    latitude = 90.0 - tileRow * 180.0/(0.625 * (2 ** tileMatrix))
    longitude = -180.0 + tileCol * 360.0/(1.25 * (2 ** tileMatrix))
    return latitude, longitude


def get_tile_info(latitude, longtitude, tileMatrix):
    """
    Convert from coordinates (latitude, longtitude) to TWMS tile location coordinate(row, col)
    
    Args:
        latitude (int, optional): The latitude.
        longtitude (int, optional): The longtitude.
        tileMatrix (int, optional): Zoom in level
    Returns:
        tileCol (int, optional): Column
        tileRow (int, optional): Row
    """
    lat_seg = int(0.625 * (2 ** tileMatrix))
    lon_seg = int(1.25 * (2 ** tileMatrix))
    
    if tileMatrix == 0:
        return 0,0
    for i in range(lat_seg):
        cur_lat = 90.0 - i * 180.0/lat_seg
        next_lat = cur_lat - 180.0 / lat_seg
        if cur_lat >= latitude > next_lat:
            #print cur_lat, next_lat 
            tileRow = i
    for i in range(lon_seg):
        cur_lon = -180.0 + i * 360.0/lon_seg
        next_lon = -180.0 + (i+1) * 360.0/lon_seg
        if cur_lon <= longtitude < next_lon:
            #print cur_lon, next_lon
            tileCol = i
    return tileRow, tileCol


def geodecode_region(tileMatrix, tileCol, tileRow, region, mask, win_size=512, state=None, county=None, city=None):
    """
    To decode the region image into meaningful coordinates and the light pollution level.

    Args:
        tileMatrix (int): The zoomed in level.
        tileCol (int): Column
        tileRow (int): Row
        region (np.ndarray): The region map.
        mask (np.ndarray): The mask map (Land = 1, Ocean = 0).
        win_size (int, optional): The length/width of the region image.
        state (str, optional): To decode geo information for specific state.
        county (str, optional): To decode geo information for specific county.
        city (str, optional): To decode geo information for specific city.

    Returns:
        df (pd.DataFrame): The dataframe contains the geo information for the given region.
    """
    import reverse_geocoder as rg # Offline geocoder  
    lat, lon = get_coordinates(tileMatrix, tileCol, tileRow)

    coordinates = []
    for i in range(region.shape[0]):
        for j in range(region.shape[1]):
            if mask[i][j] != 0:
                lat_tmp = lat - (180.0 / (0.625 * (2 ** tileMatrix))) / win_size * i
                lon_tmp = lon + (360.0 / (1.25 * (2 ** tileMatrix))) / win_size * j
                coordinates.append((lat_tmp, lon_tmp))

    results = np.array(rg.search(coordinates))
    #res_reshape = results.reshape(region.shape[0],region.shape[1])
    if state != None:
        select = 'admin1'
        select_item = state
    elif county != None:
        select = 'admin2' 
        select_item = county
    elif city != None:
        select = 'name' 
        select_item = city
    else:
        select = 'admin1'
        select_item = 'California'
    
    info = []
    cnt = 0  
    for i in range(region.shape[0]):
        for j in range(region.shape[1]):
            if mask[i][j] != 0:
                if results[cnt][select] in select_item:
                    info.append([region[i][j],                                      # Light Pollution Level
                                 results[cnt]['name'],                              # Region
                                 results[cnt]['admin2'],                            # County
                                 results[cnt]['admin1'],                            # State
                                 results[cnt]['cc'],                                # Country
                                 (results[cnt]['lat'], results[cnt]['lon']),   # Region Coordinates 
                                 coordinates[cnt][0],                                    # Pixel Latitude
                                 coordinates[cnt][1]])                                   # Pixel Longtitude
                    #if  res_reshape[i][j]['admin2'] == '':
                    #    print(res_reshape[i][j]['lat'], res_reshape[i][j]['lon']), coordinates[cnt][0], coordinates[cnt][1]      
                cnt += 1
    col_names = ['Light Pollution', 'Region', 'County','State', 'Country', 'Region Coordinate', 'Latitude', 'Longtitude']
    df = pd.DataFrame(info, columns = col_names)
    #results = np.array([results[i]['name'] for i in range(len(coordinates))]).reshape(512,512)
    return df
