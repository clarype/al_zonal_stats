
##This program run zonal stats on raster images

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

    # read csv file as dataframe
    df = pd.read_csv(csv_path, converters={'band_move': lambda x: x.split('|')})

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

def make_run_params(shp,ras_list,startYear,endYear,root):

    # read in shp file as geo dataframe
    shp_gpd = gpd.read_file(shp)

    # split geo dataframe into list of dataframes based on year values
    dict_of_regions = {k: v for k, v in shp_gpd.groupby('year')}

    param = []

    # loop over dic of dataframes and add the dataframe to a dictionary of parameters
    for i in dict_of_regions:
    
        #print('index',i)

        # calculate the band value from the year of the dataframe
        band = list(range(startYear,endYear+1)).index(i)+1
        max_band = list(range(startYear,endYear+1)).index(max(list(range(startYear,endYear+1))))
        max_band_d = list(range(startYear,endYear)).index(max(list(range(startYear,endYear))))
        min_band = 1
        #print(band)
        # loop over raster info and make parameter dic and append to list of params
        for e in ras_list:

            # make copy of dictionary
            tempdic = e.copy()

            # add dataframe to dic copy
            tempdic['df'] = dict_of_regions[i]
            tempdic['root'] = root

            # add band value to dic. the band value is calculated for the year value in the dataframe
            # ADD logic for post and pre band calculation


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
                play_band = band - 1 
                if play_band <= max_band:
                    tempdic['band_zonal'] = band - 1
                else:
                    continue

            tempdic['df_year'] = i

            tempdic['df_band'] = band

            # add mutated dic to list
            param.append(tempdic)

    # return list of dics
    return param

def get_zonals(param):
    # temp !! this should be removed later as the csv should have full paths
    dirPath = param['root']
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    # make shp file path
    shpfilepath = dirPath+param['name'] +param['band_move']+"_"+str(param['df_year'])+".shp"
   

    # look for csv file path
    if os.path.exists(shpfilepath):

        #  read file
        tempshp = gpd.read_file(shpfilepath)
        try:
            # if last row is complete break out
            if tempshp.iloc[-1][0] != None:
                print(shpfilepath)
                print(tempshp.iloc[-1][0])
            else:
                return
        except IndexError:
            print(111)



    print(shpfilepath, "   Does not exist; generating it.")
    # if not continue to zonal

    #print('name',param['name'],'idx',param['pose'],'year',param['df_year'],'band',param['df_band'],'bandMove',param['band_move'],'zonalBand',param['band_zonal'])
    stats = zonal_stats(param['df'], param['path'], geojson_out=True, band=param['band_zonal'],stats=['min', 'max', 'mean', 'count','std'])

    geoJson = {"type": "FeatureCollection", "features": stats}
    json_object = json.dumps(geoJson)
    gdf = gpd.read_file(json_object)
    if param['imageType'] == 'difference':
        gdfreNamed = gdf.rename(columns={'min': param['name'] + '_MIN', 'max': param['name'] + '_MAX', 'mean': param['name'] + '_MN', 'count': param['name']+ '_CNT','std': param['name']+ '_STD'})
    else:
        gdfreNamed = gdf.rename(columns={'min':param['band_move'] + '_MIN', 'max': param['band_move'] + '_MAX','mean':param['band_move'] + '_MN','count': param['band_move'] + '_CNT','std': param['band_move'] + '_STD'})

    width = gdfreNamed.shape[1]

    gdfreNamed.loc[len(gdfreNamed.index)] = [None] * width

    gdfreNamed.to_file(shpfilepath,)

    return gdfreNamed

def get_temp_shp(path,r_info):

    #get the name of the difference images
    # loop over list of images
    search = []
    for img in r_info:
       if img['imageType'] == 'difference':
            search.append(img['name'])
    
    inpath = []
    
    for q in search:
        list_of_all_shp = glob.glob(path+"*"+q+"*.shp")
        inpath.append(list_of_all_shp)

    inpath =[item for sublist in inpath for item in sublist]
    #print(inpath)
    
    temp_list = []
    for i in inpath:
        temp_list.append(int(i[-8:-4]))

    listmax = max(temp_list)
    listmin = min(temp_list)

    list_of_shpLists = []

    for e in range(listmin, listmax+1):
        temp = []
        for ee in inpath:
            if str(e) in ee:
                temp.append(ee)
        temp.append(path)
        list_of_shpLists.append(temp)


    return list_of_shpLists

def merge_shpfiles(list_of_shpfiles):

    dirPath = list_of_shpfiles[-1]
    list_of_shpfiles.pop()
    #if not os.path.exists(dirPath):
    #    os.makedirs(dirPath)

    gdf_list = []

    for shp in list_of_shpfiles:

        df_1 = gpd.read_file(shp)
        gdf_list.append(df_1)


    rdf = reduce(lambda x, y: pd.merge(x, y, on = ['id','Shape_Area','Shape_Leng','UNIQUE','annualID','change_occ','uniqID','year','geometry']), gdf_list)
    rdf.to_file(dirPath+list_of_shpfiles[0][-8:-4]+".shp")

    return
    
def clean_up(path,r_info):

    #get the name of the difference images
    # loop over list of images
    search = []
    for img in r_info:
       if img['imageType'] == 'difference':
            search.append(img['name'])

    inpath = []

            
    for q in search:
        list_of_all_shp = glob.glob(path+"*"+q+"*.shp")
        inpath.append(list_of_all_shp)

    inpath =[item for sublist in inpath for item in sublist]
    #print(inpath)
    
    for e in inpath:
        os.remove(e)


def main():

    # csv file path
    csvPath ="C:\\Users\clary\\Documents\\al_project\\al_zonal_stats\\miss_attributes.csv" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # shp file path
    shpPath = "C:\\Users\clary\\Documents\\al_project\\MISS\\miss_vector\\miss_true_disturbances.shp" #<<<<<<<<<<<

    # out directory
    dir = "C:\\Users\clary\\Documents\\al_project\\MISS\\temp\\" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
    start_year = 1985 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
 
    end_year = 2020 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
 
    # get raster info as a python dictionary
    raster_info = get_raster_info(csvPath)

    # edit raster info dictionary
    mutated_raster_info = mutate_dic(raster_info)
    
    # get shp file and add there file path to raster info
    param_list = make_run_params(shpPath, mutated_raster_info,start_year,end_year,dir)

    # run zonal stats
    with Pool(5) as p:
        p.map(get_zonals, param_list)

    # get shp files and group by year -- returns a list of lists -- the child lists are lists of shp file paths
    list_of_shp = get_temp_shp(dir,raster_info)

    # map over list of lists and merge shp files
    with Pool(5) as p:
        p.map(merge_shpfiles,list_of_shp)

    # clean up script
    clean_up(dir,raster_info)
    
    
if __name__ == "__main__":
    main()
    sys.exit()
