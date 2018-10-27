#********************************** Cargar Librerías ****************************************
from multispectral import Multispectral
import matplotlib.pyplot as plt
import matplotlib.image as image
import numpy as np

#******************************* Funciones Útiles *****************************************

# Guardar una imagen PNG
def saveImagePng(img, filePath, cmap=None):
    image.imsave(filePath, img, cmap=cmap)

# Muestra una imagen RGB
def plotImageRgb(rgb, title):
    plt.figure()
    plt.title(title)
    plt.imshow(rgb)

# Muestra una imagen a escala de grises
def plotImageGray(gray, title):
    plt.figure()
    plt.title(title)
    plt.imshow(gray, cmap="gray")

# Muestra la distribución de la intensidad de los colores
def plotImageDist(rgb):
    plt.figure()
    plt.xlabel('Intensidad del Color')
    plt.title('Distribución de Intensidad del Color')
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2], 
    r_hist, interv = np.histogram(r[r > 0] ,100)
    g_hist = np.histogram(g[g > 0] ,100)[0]
    b_hist = np.histogram(b[b > 0] ,100)[0]
    plt.plot(interv[:-1], r_hist/rgb.size, color='r')
    plt.plot(interv[:-1], g_hist/rgb.size, color='g')
    plt.plot(interv[:-1], b_hist/rgb.size, color='b')

# Muestra la banda pancromatica a escala de grises
def plotPAN(img):
    plt.figure()
    plt.title('Banda Pancromatica')
    plt.imshow(Multispectral.color(img.pan()), cmap='gray')


#************************* Programa de Ejemplo de Uso de Multispectral *******************

# Trabajar con dimensiones 6 veces menores a la original
Multispectral.resizeFactor = 6

# Trabajar con imágenes Originales
#Multispectral.idealShape = None

# Habilitar Cache
Multispectral.cache = True

# Habilitar modo informativo (Imprime los procedimientos que ejecuta)
Multispectral.verbose = True

# Rutas a las imágenes a cargar
imagesPaths = [
    './landsat-imagery/LC08_L1TP_010054_20181025_20181025_01_RT.landsat8',
    './landsat-imagery/LC080090562017121801T1-SC20181005111414.landsat8',
    './landsat-imagery/LC080090562018083101T1-SC20181005124650.landsat8',
    './sentinel-imagery/IMG_DATA_A017368_20181019T153616.sentinel2',
    './sentinel-imagery/IMG_DATA_A004055_201715T152714.sentinel2',
    './sentinel-imagery/IMG_DATA_A013035_20171220T153107.sentinel2',
    './sentinel-imagery/IMG_DATA_A010747_20170713T153113.sentinel2',
    './sentinel-imagery/IMG_DATA_A004055_201715T152714.sentinel2',
] 

# Cargar Imágenes con Multispectral
images = []
for path in imagesPaths :
    images.append(Multispectral(path))

# Imágen a Color Natural
plotImageRgb(images[2].rgb(), 'Imagen de Color Natural')    # Mostrar Imagen
saveImagePng(images[5].rgb(), 'rgb-natural.png')            # Guardar imagen

# Composición con NIR, Green y Ultra Blue
img = images[0]
nir, green, ublue = img.vnir()[:,:,3], img.vnir()[:,:,1], img.ublue()
composition = Multispectral.composite(nir, green, ublue)
plotImageRgb(composition, 'Composición Nir Green Ublue')    # Mostrar Imagen
saveImagePng(composition, 'nir-green-ublue-composite.png')  # Guardar imagen


# Banda Pancromática a escala de grises
panGray = Multispectral.color(images[0].pan())                  # Convertir de reflexion a espacio de color
plotImageGray(panGray, 'Imagen de la reflexión Pancromatica')   # Mostrar Imagen
saveImagePng(panGray, 'pan-gray.png', cmap='gray')              # Guardar imagen

# Imprimir Información
img = images[0]
print('\nDatos de imagen %s' % (img.pathFolder.name))
print('Sensor: ', img.extension)
print('VNIR Data Array Shape ', img.vnir().shape)
print('PAN Data Array Shape ', img.pan().shape)


# Bandas Individuales a escala de grises
b1 = images[3].band(1)                              # Leer banda 1
b1Gray = Multispectral.color(b1)                    # Convertir de reflexion a espacio de color
plotImageGray(b1Gray, 'Banda 1 a escala de grises') # Mostrar Imagen

b8A = images[5].band('8A')                              # Leer banda 8A
b8AGray = Multispectral.color(b8A)                      # Convertir de reflexion a espacio de color
plotImageGray(b8AGray, 'Banda 8A a escala de grises')   # Mostrar Imagen

# Mostrar Imágenes y Gráficas
plt.show()

