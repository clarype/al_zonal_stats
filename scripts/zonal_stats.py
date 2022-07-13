'''
This program run zonal stats on raster images


'''

# import
import pandas as pd
import geopandas as gpd
import sys
from multiprocessing import Pool


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

    # split geo dataframe into list of datafames based on year values
    dict_of_regions = {k: v for k, v in shp_gpd.groupby('year')}

    param = []

    # loop over dic of dataframes and add the dataframe to a dictionary of parameters
    for i in dict_of_regions:


        # calculate the band value from the year of the dataframe
        band = list(range(1990,2019+1)).index(i)+1

        # loop over raster info and make parameter dic and append to list of params
        for e in ras_list:

            # make copy of dictionary
            tempdic = e.copy()

            # add dataframe to dic copy
            tempdic['df'] = dict_of_regions[i]

            # add band value to dic. the band value is calculated for the year value in the dataframe
            tempdic['band_zonal'] = band - tempdic['band_move']

            tempdic['df_year'] = i

            tempdic['df_band']

            # add mutated dic to list
            param.append(tempdic)

    # return list of dics
    return param

def get_zonals(param):
    for i in param:
        print(param[i])

def main():

    # csv file path
    csvPath = "D:\\v1\\al_nps\\MISS\\miss_attributes.csv"

    # shp file path
    shpPath = "D:\\v1\\al_nps\\MISS\\miss_vector\\MISS_true_dist\\miss_true_disturbances.shp"

    # get raster info as a python dictionary
    raster_info = get_raster_info(csvPath)

    # edit raster info dictionary
    mutated_raster_info = mutate_dic(raster_info)

    # get shp file and add there file path to raster info
    param_list = make_run_params(shpPath, mutated_raster_info)

    # run zonal stats
    with Pool(5) as p:
        p.map(get_zonals, param_list)


if __name__ == "__main__":
    main()
    sys.exit