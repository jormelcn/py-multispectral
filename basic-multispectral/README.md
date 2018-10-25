# MULTISPECTRAL
Módulo Python para cargar fácilmente datos de sensores remotos multiespectrales.
Permite cambiar la resolución espacial de trabajo en una sola linea sin afectar su algoritmo.


## Requerimientos
python3,    python3-gdal,   python3-numpy

### Debian/Ubuntu
sudo apt-get install python3 python3-numpy python3-gdal


# Uso

```Python
from multispectral import Multispectral

Multispectral.idealShape = (1080, 1080) # Tamaño máximo de trabajo de las imágenes
Multispectral.idealShape = None     # None para usar imágenes originales (USAR CON CUIDADO)

folderPath = '/sensor-data/FOLDER_WITH_DATA' # Ruta a folder con los datos de la imagen
sensorType = 'landsat8' # Tipo de sensor, se soporta 'sentinel' y 'landsat8'

img = Multispectral(folderPath + '.' + sensorType) # Cargar imagen

vnirData = img.vnir  # Array de Numpy con las bandas BLUE, GREEN, RED y NIR
rgbImg = img.rgb() # Array de Numpy RGB con valores de 0 a 1

```

## Ejemplo
[example.py](example.py)
