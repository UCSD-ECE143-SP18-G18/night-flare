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
    Convert from coordinates (latitude, longtitude) to TWMS tile location coordinate(row, col)/
    
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



def geodecode_region(tileMatrix, tileCol, tileRow, region, mask, win_size=512):
    import reverse_geocoder as rg # Offline geocoder  
    import pandas as pd 
    lat, lon = get_coordinates(tileMatrix, tileCol, tileRow)

    coordinates = []
    #print (180.0 / (0.625 * (2 ** tileMatrix)))
    for i in range(region.shape[0]):
        for j in range(region.shape[1]):
            lat_tmp = lat - (180.0 / (0.625 * (2 ** tileMatrix))) / win_size * i
            lon_tmp = lon + (360.0 / (1.25 * (2 ** tileMatrix))) / win_size * j
            coordinates.append((lat_tmp, lon_tmp))

    results = np.array(rg.search(coordinates))
    print results[5000]
    print coordinates[0]
    res_reshape = results.reshape(region.shape[0],region.shape[1])
    cnt = 0

    info = []
    for i in range(region.shape[0]):
        for j in range(region.shape[1]):
            if mask[i][j] != 0:
                info.append([region[i][j],                                           # Light Pollution Level
                             res_reshape[i][j]['name'],                              # Region
                             res_reshape[i][j]['admin2'],                            # County
                             res_reshape[i][j]['admin1'],                            # State
                             res_reshape[i][j]['cc'],                                # Country
                             (res_reshape[i][j]['lat'], res_reshape[i][j]['lon']),   # Region Coordinates 
                             coordinates[cnt][0],                                    # Pixel Latitude
                             coordinates[cnt][1]])                                   # Pixel Longtitude
                #if  res_reshape[i][j]['admin2'] == '':
                #    print(res_reshape[i][j]['lat'], res_reshape[i][j]['lon']), coordinates[cnt][0], coordinates[cnt][1]      
            cnt += 1
    col_names = ['Light Pollution', 'Region', 'County','State', 'Country', 'Region Coordinate', 'Latitude', 'Longtitude']
    df = pd.DataFrame(info, columns = col_names)
    #results = np.array([results[i]['name'] for i in range(len(coordinates))]).reshape(512,512)
    return df
