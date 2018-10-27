# MULTISPECTRAL
Módulo Python para cargar fácilmente datos de sensores remotos multiespectrales.
Permite cambiar la resolución espacial de trabajo en una sola linea sin afectar su algoritmo.


### Requerimientos
python3,    python3-gdal,   python3-numpy

#### Debian/Ubuntu
sudo apt-get install python3 python3-numpy python3-gdal


# Uso

```Python
from multispectral import Multispectral

# Factor de reduccion para trabajo con las imágenes
# Por defecto 8, None para usar imágenes originales
Multispectral.resizeFactor = 10     

# Activar Caché de imagenes, Aumenta Enormemente la velocidad de carga
# Por defecto True
Multispectral.cache = True

# Cargar imagen
folderPath = '/sensor-data/FOLDER_WITH_DATA' # Ruta a folder con los datos de la imagen
sensorType = 'landsat8' # Tipo de sensor, se soporta 'sentinel2' y 'landsat8'
img = Multispectral(folderPath + '.' + sensorType)

vnir = img.vnir()       # Array con Reflexión Blue, Green, Red y NIR
ublue = img.ublue()     # Reflexión en la banda Utra Blue
pan = img.pan()         # Reflexión en la banda Pancromatica
trueRGB = img.rgb()     # Imagen RGB con correccion de colores

b2 = img.band(2)        # Reflexión en la Banda 2
b3 = img.band(3)        # Reflexión en la Banda 3
b4 = img.band(4)        # Reflexión en la Banda 4

#Array de Numpy con Composición a color
comp = Multispectral.composite(b2, b3,  b4) 

#Reflectancia a espacio de color
gray = Multispectral.color(pan)

```

### Ejemplo
[example.py](example.py)

### Configuración de nombres de archivos y extensiones
```Python
print( Multispectral.validExtensions )
print( Multispectral.extensionsConfig )

```
