### Al’s Zonal Stats



This program calculates zonal statistics for polygons of a shapefile over one or more raster datasets. The raster datasets should be of a temporal stack; that is, each band in a raster dataset must pertain to an observation in time or change in time (delta images). These two types of raster datasets are denoted in a CSV file by keywords .The CSV file contains raster information; such as, raster location, raster type, zonal offset, and more information can be obtained at the end of this document. The input Shapefile must be of polygons attributed with a *year* field. The year field is used to align the polygons with the correct band of the raster being used in the zonal calculation. The program outputs a shapefile for each observation in the timeseries. The delta images are merged for each matching observation while the single observation shapefiles are not. 



Workflow:



1. Download all products 

2. 1. [Anaconda executable](https://drive.google.com/file/d/1Tm0qBHEbWVF6Gm_DT3m9iOGpHfaFTqhw/view?usp=share_link) (If download does not start try a different browser.)
   2. [Scripts and config CSV GitHub ](https://github.com/clarype/al_zonal_stats/archive/refs/heads/main.zip)

3. Setup workspace 

4. 1. Make a workspace directory 
   2. Move all products to workspace directory (**Not mandatory**)

5. Run ‘PyEnvs-0.5-Windows-x86_64’ to install anaconda environment

6. 1. double click file
   2. Click “More info” in the dialog box that appears.

![img](https://lh6.googleusercontent.com/Acdi-tYgRUB2Q5PSvcGAObGXLd9NmB38DSZsRC35EiMqZzYY8hlE2HD4RFV20915eloG3AWK76KITXnlg51Fl2nKtP-xqBrK7nnE9Ku7mBYMX7gRZtPFoDalB8spaTn0pquM35KqiLSeFJIenHgFaQg894sr5vgl0behp-hY_3B7XDTZ6TVI44zSrw3Oug)

1. Click run anyway

![img](https://lh6.googleusercontent.com/guncH4qST2Q4iirDG9IBgkGmBHqI6hrqlDGoxKRGSfs4ks5O3KzWYv0TqbG1pV1odOjWkmE0slhWRkCJ_4aM9FLgPDlpbGpco45ol5cr-7p6NLCtYuteOC7WZk1B9Kc7IWDnoEe83BHZYcO8rm0CcyRLVkwjxUAUSH4ZxWF15rbqj8E9pvQjsB-ogHX-aQ)

1. Click next in the next dialog box that appears.

![img](https://lh3.googleusercontent.com/cyWvtnLhyty8YrUXArPSWyu2Fc7-cdUwow4_n6QJmOlCQN5cNTyzQ47YqNyV-8EKR9AV2VgzBif1phLfCcIDKw0pRxrNu9EDk1-zQE7OHIAXoadzdbgHDW5rie9CDSMvrudDLgVFRH84WpYt4MCjfKBujzvHMZlF-8nrPaelZV939-pp--UeuA9q7g7D3g)

1. Click “I agree”
2. Install just Me, click next 
3. Use or rename the provided installation location to install in your user directory
4. Click next

![img](https://lh3.googleusercontent.com/TZDD7MeVokOj7Hy1hO4JxtWivTPaFY_HA6ASpJNaitUM7vIoQWO2HuprxwkSBIMIUNUJRzn1nLNQ2kuAWSssYSgDX3hZTL-VuwIO9tU9ZrVVhFh91XAF2v-pRSAM76rwrOcB6-WDWZG0ZHfVOxko8ZKubsST3i0Dlxksd5kcSWbkivkptwtfIMMx2eB4)

1. Select the checkboxes option below and click install. (This should not affect other python interpreters.)

![img](https://lh6.googleusercontent.com/KA6sG6JNaw-OKPDDdPJzrARlOrm9ff9Xs6sq0zOjBkIpIoxCA4pqjPggc6eP8BVYE_4xTpDEuBg1O5xBM5uR99BPw5uGju487S4koehU25xU3iDKFj-DYGKY7DKkS7fRX5n8yzwG0cq-NrIIxt-fA5MLaPpNuZAhiUbw9n9Z1ZWgK6BpClO1wTqnoGsOGQ)

1. Click next once the progress bar is completely filled. 
2. Click finish - If you have an issuse you can add an issuse meassage at the top of the page under "issuses" 
3. Now the Anaconda environment is installed in your project directory.



1. In your favorite text editor, open the BAT file ‘Start_PyEnv’ that came for the github repo.

2. 1. Edit line 1 to point to the anaconda environment directory. 

![img](https://lh5.googleusercontent.com/m41QgcQnRp_RxQC5hyiVRbbjAVv1eQMCDRpRG72f5VSvrsKKYdCPsbzHEEF4qvrEa7qUkYytscmAAStmazCft2csb8FpeoIvtCu-l57kZZhoQiaBw7JqibmJI-1TOpWR7trkTdDqiIZXkeanNBGU-m40klUIwX0nkWbCdydBboZBkhYHUnQzP-pT_BnJ)

1. Save file 

2. Close the text editor

3. Make sure the anaconda environment is working properly.

4. 1. Double click on the BAT file ‘Start_PyEnv’ file and a terminal window will open

   2. Enter “python” into the terminal window and click enter 

   3. 1. The python interpreter show display something like the following:

![img](https://lh5.googleusercontent.com/_yvOJGOqjHU4HZFpE7K0mTH99MNarfL8khxxsEWb4O_3bTkALg5F34QwrmocP5KOzNVD0d8-yce4Mq6lasVNai_QyoScUWJQg4Kmd4bWx5o0gA2LI8TEZ8aV2M3pRciTHO0kszhFDuPNjUZkAKkmbzUB5K2at7oy9EC7IeCMIeENEX8BpxBQ3rO9ARJnmQ)

1. Enter “exit()” into the terminal to exit the python interpreter
2. You can leave the terminal window open if you are going to be running the script or you can close the terminal and open it later.

1. Open and Edit your CSV to reflect your raster layers.

2. 1. [CSV field descriptions ](https://docs.google.com/document/d/1fFuZTMBCehp4FO2wQbpBZcJVbik-pitcykELqBy4W1s/edit#heading=h.qq0vho4rce4f)

3. Edit the zonal stats script in a text editor 

4. 1. Edit line below:

   2. 1. Line 224 : file path to CSV file 
      2. Line 227 : file path to Shape file of polygons 
      3. Line 230 : folder path to an output directory
      4. Line 232 : raster time series start year
      5. Line 234 : raster time series end year

   3. Save file

5. Open anaconda environment if it is not already open

6. 1. Locate and double click on the BAT file *Start_PyEnv*

   2. From the terminal change directory to the script's location.

   3. Once at the scripts location enter *python zonal_stats.py* and press enter 

   4. 1. The script will start. 

7. Outputs 

8. 1. In the temp folder of your raster directory are the outputs of the program.

   2. There are two types of outputs if both difference and annual rasters were used.

   3. 1. Annual outputs pertain to an individual observation and index type and difference outputs are merged into individual observations for each delta index. 

































### CSV file 



This CSV, named “miss_attributes.csv” contains 8 fields which control how the zonal statistics are applied over the rasters. The table below gives the field name and description of that field.





| path      | The full file path to a raster image                         |
| --------- | ------------------------------------------------------------ |
| name      | A name to represent the raster image, must be 6 to 7 characters long.. |
| theme     | Not used                                                     |
| imageType | This field must be one of two labels: **difference** or **annual**. Difference is an image that shows the change difference between the bands of this image. Annual is for images where the pixel value represents a time such as a single image taken at a point in time . |
| pose      | Pose is a determiner on what bands to get zonal stats on. For bands before use **pre**, and for bands after use **pst**. |
| dype      | Not used                                                     |
| band_move | The band values to count away from the current band to get zonal stats. This value or values pertains to the number of bands before or after an observation in the timeseries. |
| run       | A binary operator, 1 to run and 0 not to run                 |

 
