'''
This program run zonal stats on raster images


'''

# import
import pandas as pd
import geopandas as gpd
import sys
from multiprocessing import Pool
from rasterstats import zonal_stats
import json
import os
import glob
from functools import reduce


def get_raster_info(csv_path):
    # column names
    header_list = ['path','name','theme','time','pose','dype','band_move','run']

    # read csv file as dataframe and add column names and change band_move string to list of strings
    df = pd.read_csv(csv_path, names=header_list, converters={'band_move': lambda x: x.split('|')})

    # edit dataframe - keep only rows to run
    run_df = df[df['run'] == 1]

    # cast dataframe as list of dictionaries
    df_dic = run_df.to_dict('records')

    # return list of dictionaries
    return df_dic

def mutate_dic(ras_info):

    # new mutated dictionary
    out_dic_list = []

    # loop over list
    for dic in ras_info:

        # if band move only has a zero
        if len(dic['band_move']) == 1 and dic['band_move'][0] == '0':

            # make copy of dic
            tempdic = dic.copy()

            # add band move value to dic copy
            tempdic['band_move'] = "0"

            # append mutated tempdic to list
            out_dic_list.append(tempdic)

        # if band move has a list of values
        else:

            # get the band move value list
            templist = dic['band_move']

            # loop over the band move list
            for i in templist:

                # make copy of dic
                tempdic1 = dic.copy()

                # add single band move value to temp dic
                tempdic1['band_move'] = i

                # append mutated tempdic to list
                out_dic_list.append(tempdic1)

    return out_dic_list

def make_run_params(shp,ras_list):

    # read in shp file as geo dataframe
    shp_gpd = gpd.read_file(shp)

    # split geo dataframe into list of dataframes based on year values
    dict_of_regions = {k: v for k, v in shp_gpd.groupby('year')}

    param = []

    # loop over dic of dataframes and add the dataframe to a dictionary of parameters
    for i in dict_of_regions:
        print('index',i)

        # calculate the band value from the year of the dataframe
        band = list(range(1985,2020+1)).index(i)
        print('band',band)
        max_band = list(range(1985,2020+1)).index(max(list(range(1990,2019+1))))
        min_band = 1

        # loop over raster info and make parameter dic and append to list of params
        for e in ras_list:

            # make copy of dictionary
            tempdic = e.copy()

            # add dataframe to dic copy
            tempdic['df'] = dict_of_regions[i]

            # add band value to dic. the band value is calculated for the year value in the dataframe
            #################### ADD logic for post and pre band calculation

            if tempdic['pose'] == 'pst':
                play_band = band + int(tempdic['band_move'])
                if play_band <= max_band:
                    tempdic['band_zonal'] = band + int(tempdic['band_move'])
                else:
                    continue
            elif tempdic['pose'] == 'pre':
                play_band = band - int(tempdic['band_move'])
                if play_band >= min_band:
                    tempdic['band_zonal'] = band - int(tempdic['band_move'])
                else:
                    continue
            else:
                tempdic['band_zonal'] = band

            tempdic['df_year'] = i

            tempdic['df_band'] = band

            # add mutated dic to list
            param.append(tempdic)

    # return list of dics
    return param

def get_zonals(param):


    # temp !! this should be removed later as the csv should have full paths
    dirPath = "D:\\v1\\al_nps\\MISS\\" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    if not os.path.exists(dirPath+"temp\\"):
        os.makedirs(dirPath+"temp\\")

    # make csv file path
    shpfilepath = dirPath+"temp\\"+param['name'] +param['band_move']+"_"+str(param['df_year'])+".shp"

    # look for csv file path
    if os.path.exists(shpfilepath):

        #  read file
        tempshp = gpd.read_file(shpfilepath)
        print("--------")
        # if last row is complete break out
        if tempshp.iloc[-1][0] == None:
            print(shpfilepath,' exists')
            return


    # if not continue to zonal

    print(param['name'],param['pose'],param['df_year'],param['df_band'],param['band_move'],param['band_zonal'])
    stats = zonal_stats(param['df'], dirPath+param['path'], geojson_out=True, band=param['band_zonal'],stats=['min', 'max', 'mean', 'count','std'])

    geoJson = {"type": "FeatureCollection", "features": stats}
    json_object = json.dumps(geoJson)
    gdf = gpd.read_file(json_object)
    gdfreNamed = gdf.rename(columns={'min': param['name'] +param['band_move']+ '_min', 'max': param['name'] +param['band_move']+ '_max', 'mean': param['name'] +param['band_move']+ '_mean', 'count': param['name'] +param['band_move']+ '_count','std': param['name'] +param['band_move']+ '_std'})

    width = gdfreNamed.shape[1]

    gdfreNamed.loc[len(gdfreNamed.index)] = [None] * width
    #print(gdfreNamed)
    gdfreNamed.to_file(shpfilepath)


    return gdfreNamed

def get_temp_shp(path):

    list_of_all_shp = glob.glob(path+"*.shp")
    temp_list = []
    for i in list_of_all_shp:
        temp_list.append(int(i[-8:-4]))

    listmax = max(temp_list)
    listmin = min(temp_list)

    list_of_shpLists = []

    for e in range(listmin, listmax+1):
        temp = []
        for ee in list_of_all_shp:
            if str(e) in ee:
                temp.append(ee)
        list_of_shpLists.append(temp)


    return list_of_shpLists

def merge_shpfiles(list_of_shpfiles):

    dirPath = "D:\\v1\\al_nps\\MISS\\temp2\\" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    gdf_list = []

    for shp in list_of_shpfiles:
        df_1 = gpd.read_file(shp)#.crs =4269
        print(df_1.crs)
        gdf_list.append(df_1)


    rdf = reduce(lambda x, y: pd.merge(x, y, on = ['id','Shape_Area','Shape_Leng','UNIQUE','annualID','change_occ','uniqID','year','geometry']), gdf_list)
    rdf.to_file(dirPath+list_of_shpfiles[0][-8:-4]+".shp")
    print(rdf)

def main():

    # csv file path
    csvPath = "D:\\v1\\al_nps\\MISS\\miss_attributes.csv" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # shp file path
    shpPath = "D:\\v1\\al_nps\\MISS\\miss_vector\\MISS_true_dist\\miss_true_disturbances.shp" #<<<<<<<<<<<<<


    # get raster info as a python dictionary
    raster_info = get_raster_info(csvPath)

    # edit raster info dictionary
    mutated_raster_info = mutate_dic(raster_info)

    # get shp file and add there file path to raster info
    param_list = make_run_params(shpPath, mutated_raster_info)

    # run zonal stats
    with Pool(5) as p:
        p.map(get_zonals, param_list)

    dir = "D:\\v1\\al_nps\\MISS\\temp\\" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # get shp files and group by year -- returns a list of lists -- the child lists are lists of shp file paths
    list_of_shp = get_temp_shp(dir)
    #print(list_of_shp)

    # map over list of lists and merge shp files
    merge_shpfiles(list_of_shp[0])
    with Pool(5) as p:
        p.map(merge_shpfiles,list_of_shp)

    # Merge all year shp files back together.... Each year has different numbers of rows...

if __name__ == "__main__":
    main()
    sys.exit