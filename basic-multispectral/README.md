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

Multispectral.idealShape = (1080, 1080) # Tamaño máximo de trabajo de las imágenes (El doble para pancromatica)
Multispectral.idealShape = None     # None para usar imágenes originales (USAR CON CUIDADO)

folderPath = '/sensor-data/FOLDER_WITH_DATA' # Ruta a folder con los datos de la imagen
sensorType = 'landsat8' # Tipo de sensor, se soporta 'sentinel' y 'landsat8'

img = Multispectral(folderPath + '.' + sensorType) # Cargar imagen


vnir = img.vnir()       # Array de Numpy con las bandas BLUE, GREEN, RED y NIR
ublue = img.ublue()     # Array de Numpy con las banda Ultra Blue
pan = img.pan()         # Array de Numpy con las banda Pancromatica
trueRGB = img.rgb()     # Array de Numpy RGB Corregido con valores de 0 a 1

#Array de Numpy con Composición a color bandas NIR, GREEN y Ultra Blue
comp = Multispectral.composite(vnir[:,:,3], vnir[:,:,1]  ublue) 

```

## Ejemplo
[example.py](example.py)
