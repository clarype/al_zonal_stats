SET LT_PY_ENV=C:\Users\clary\env
SET PATH=%LT_PY_ENV%;%LT_PY_ENV%\Lib\bin;%LT_PY_ENV%\Scripts;%LT_PY_ENV%\site-packages;%~dp0
SET GDAL_DATA=%LT_PY_ENV%\Library\share\gdal
SET PYTHONPATH=%LT_PY_ENV%\site-packages
start cmd.exe /kv