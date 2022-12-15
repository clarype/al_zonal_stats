"""This program calculates zonal statistics for polygons of a shapefile over one or more raster datasets. The raster datasets should be of a temporal 
stack; that is, each band in a raster dataset must pertain to an observation in time or change in time (delta images). These two types of raster 
datasets are denoted in a CSV file by keywords .The CSV file contains raster information; such as, raster location, raster type, zonal offset, and 
more information can be obtained at the end of this document. The input Shapefile must be of polygons attributed with a year field. The year field is 
used to align the polygons with the correct band of the raster being used in the zonal calculation. The program outputs a shapefile for each observation 
in the timeseries. The delta images are merged for each matching observation while the single observation shapefiles are not."""

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

# Tihs function gets raster information from a CSV file if raster row is turned on 
def get_raster_info(csv_path):

    # read csv file as dataframe
    df = pd.read_csv(csv_path, converters={'band_move': lambda x: x.split('|')})

    # edit dataframe - keep only rows to run
    run_df = df[df['run'] == 1]

    # cast dataframe as list of dictionaries
    df_dic = run_df.to_dict('records')

    # return list of dictionaries
    return df_dic

# This function 
def mutate_dic(ras_info):

    # a list of store the new mutated dictionary
    out_dic_list = []

    # loop over list a list of dictionary. Each dictionary contians raster informatino ... file path, raster name, targt band distances, etc
    for dic in ras_info:

        # if the band move value, the distance from the target year to get stats, is 0 and is the only value do this 
        if len(dic['band_move']) == 1 and dic['band_move'][0] == '0':

            # make copy of dic
            tempdic = dic.copy()

            # add band move value to the dictionary copy 
            tempdic['band_move'] = "0"

            # append the copied dictionary to the list that will store the mutated dictionaries
            out_dic_list.append(tempdic)

        # if band move has a list of values do this
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

# This function makes a list of dictionaries where each dictionary has a shp dataframe and all the associated parameters to 
# get zonal stats. The parameter include keys such as the band to run zonal stats on and what dictory to store the data in.   
def make_run_params(shp,ras_list,startYear,endYear,root):

    # read in shp file as geo dataframe
    shp_gpd = gpd.read_file(shp)

    # split geo dataframe into dictionary of dataframes based on year values where the key is the year value
    dict_of_regions = {k: v for k, v in shp_gpd.groupby('year')}

    # empty list of to be populated with dataframe/parameter dictionaries  
    param = []

    # loop over dictionary of dataframes and adds the dataframe to a dictionary with parameters for that dataframe
    for i in dict_of_regions:
    
        # calculate the band value from the year of the dataframe, the start year and end year arguments. 
        band = list(range(startYear,endYear+1)).index(i)+1
        
        # finds the maxiimum/min band value to make sure we don't ask for something we dont have------------------  
        max_band = list(range(startYear,endYear+1)).index(max(list(range(startYear,endYear+1))))
        # for delta images
        max_band_d = list(range(startYear,endYear)).index(max(list(range(startYear,endYear))))
        # the first band so we dont ask for less than it  
        min_band = 1
        #---------------------------------------------------------------------------------------------------------
        
        # loop over raster info and add parameter to dataframe/dictionary list
        for e in ras_list:

            # make copy of raster info dictionary. this is the source of the parameters for each dataframe
            tempdic = e.copy()

            # add dataframe to dataframe/parameter dictionary
            tempdic['df'] = dict_of_regions[i]
            
            # add workspace folder path to dataframe/parameter dictionary 
            tempdic['root'] = root

            # <for annual images> if the raster info row has a pst in the pose field the dataframe/parameter dictionary get a band_move value  
            if tempdic['pose'] == 'pst':
                
                # calculates the band move value. the band value to perform zonal stats
                play_band = band + int(tempdic['band_move'])
                
                # checks to see if the band value is possible (avaiable in the raster stack)
                if play_band <= max_band:
                    
                    # asigns the band value to the dataframe/parameter dictionary
                    tempdic['band_zonal'] = band + int(tempdic['band_move'])
                
                else:
                    continue
                    
            # <for annual iamages> if the raster info row has a pre in the pose field the dataframe/parameter dictionary get a band_move value       
            elif tempdic['pose'] == 'pre':
                
                # calculates the band move value. the band value to perform zonal stats
                play_band = band - int(tempdic['band_move'])
                
                # checks to see if the band value is possible (avaiable in the raster stack)
                if play_band >= min_band:
                    
                    # asigns the band value to the dataframe/parameter dictionary
                    tempdic['band_zonal'] = band - int(tempdic['band_move'])
                
                else:
                    
                    continue
                    
            # < for delta (difference images)>  if the raster info is not a annual image the dataframe/parameter 
            # dictionary get a band_move value -1 to adjust for the delta image which is a band short 
            else:
                
                # calculates the band move value. the band value to perform zonal stats
                play_band = band - 1 
                
                 # checks to see if the band value is possible (avaiable in the raster stack)
                if play_band <= max_band:
                    
                    # asigns the band value to the dataframe/parameter dictionary
                    tempdic['band_zonal'] = band - 1
                
                else:
                    
                    continue

            # asigns the year value to the dataframe/parameter dictionary
            tempdic['df_year'] = i

            # asigns the year/band value to the dataframe/parameter dictionary
            tempdic['df_band'] = band

            # adds the dataframe/parameter to list of the dataframe/parameter dictionaries 
            param.append(tempdic)

    # return list of dictionaries
    return param

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<here
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

    # run zonal stats on year dataframe and raster 
    stats = zonal_stats(param['df'], param['path'], geojson_out=True, band=param['band_zonal'],stats=['min', 'max', 'mean', 'count','std'])

    # init json object
    geoJson = {"type": "FeatureCollection", "features": stats}
    
    # python object to json string
    json_object = json.dumps(geoJson)
    
    # reads json string as geo pandas dataframe
    gdf = gpd.read_file(json_object)
    
    # condistional for delta images
    if param['imageType'] == 'difference':
     
        #if delta image rename columns
        gdfreNamed = gdf.rename(columns={'min': param['name'] + '_MIN', 'max': param['name'] + '_MAX', 'mean': param['name'] + '_MN', 'count': param['name']+ '_CNT','std': param['name']+ '_STD'})
    
    else:
        
        # else  not delta image rename columns 
        gdfreNamed = gdf.rename(columns={'min':param['band_move'] + '_MIN', 'max': param['band_move'] + '_MAX','mean':param['band_move'] + '_MN','count': param['band_move'] + '_CNT','std': param['band_move'] + '_STD'})
   
    #
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
    if len(search) == 0:
        return []
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
    if len(search) == 0:
        return []

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
    csvPath ="E:\\v1\\al_nps\\zonal_stats\\miss_attributes.csv" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # shp file path
    shpPath = "E:\\v1\\al_nps\\MISS\\miss_vector\\miss_true_disturbances.shp" #<<<<<<<<<<<

    # out directory
    dir = "E:\\v1\\al_nps\\MISS\\results\\" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
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

    # if there are no delta shp file to merge dont merge them
    if len(list_of_shp) > 0:
    
        # map over list of lists and merge shp files
        with Pool(5) as p:
            p.map(merge_shpfiles,list_of_shp)

    # clean up script
    clean_up(dir,raster_info)
    
    
if __name__ == "__main__":
    main()
    sys.exit()
