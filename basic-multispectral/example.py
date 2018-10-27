#********************************** Cargar Librerías ****************************************
from multispectral import Multispectral
import matplotlib.pyplot as plt
import numpy as np

#******************************* Funciones Útiles *****************************************

# Muestra la estimación RGB de la imagen y la distribución del Color
def plotRgbAndHistogram(img):
    plt.figure()
    plt.title('Estimación RGB')
    plt.imshow(img.rgb())
    plt.figure()
    plt.xlabel('Intensidad del Color')
    plt.title('Distribución de Intensidad del Color')
    rgb = img.rgb()
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2], 
    r_hist, interv = np.histogram(r[r > 0] ,100)
    g_hist = np.histogram(g[g > 0] ,100)[0]
    b_hist = np.histogram(b[b > 0] ,100)[0]
    plt.plot(interv[:-1], r_hist/rgb.size, color='r')
    plt.plot(interv[:-1], g_hist/rgb.size, color='g')
    plt.plot(interv[:-1], b_hist/rgb.size, color='b')

#Muestra una composición remplazando NIR GREEN UBLUE
def plotUblueComposite(img):
    plt.figure()
    plt.title('Composición Nir Green Ublue')
    plt.imshow(Multispectral.composite(img.vnir()[:,:,3], img.vnir()[:,:,1], img.ublue()))

# Muestra la banda NIR a escala de grises
def plotNIR(img):
    plt.figure()
    plt.title('Banda NIR')
    plt.imshow(img.vnir()[:,:,3], cmap='gray')

# Muestra la banda pancromatica a escala de grises
def plotPAN(img):
    plt.figure()
    plt.title('Banda Pancromatica')
    plt.imshow(img.pan(), cmap='gray')

# Imprime Información acerca de los datos contenidos en la imagen
def printImageDataInfo(img):
    print('\nDatos de imagen %s' % (img.pathFolder.name))
    print('Sensor: ', img.extension)
    print('Patron del nombre de las imágenes: ', img.namePatern)
    # Obtener array VNIR
    vnir = img.vnir()
    print('VNIR Data Array Shape ', vnir.shape)
    pan = img.pan()
    print('PAN Data Array Shape ', pan.shape)


#************************* Programa de Ejemplo de Uso de Multispectral *******************

# Trabajar con imágenes de tamaño máximo 1000x1000, PAN 2000x2000
Multispectral.idealShape = (1000, 1000)

# Trabajar con imágenes Originales
#Multispectral.idealShape = None

# Habilitar modo informativo (Imprime los procedimientos que ejecuta)
Multispectral.vervose = True


# Rutas a las imágenes a cargar
imagesPaths = [
    '../sentinel-imagery/IMG_DATA_A004055_201715T152714.sentinel',
    '../landsat-imagery/LC080090562017121801T1-SC20181005111414.landsat8',
    '../sentinel-imagery/IMG_DATA_A010747_20170713T153113.sentinel',
    '../landsat-imagery/LC080090562018083101T1-SC20181005124650.landsat8',
    '../sentinel-imagery/IMG_DATA_A010747_20170713T153113.sentinel',
    '../sentinel-imagery/IMG_DATA_A013035_20171220T153107.sentinel',
    '../landsat-imagery/LC08_L1TP_010054_20181025_20181025_01_RT.landsat8',
] 

# Cargar Imágenes con Multispectral
images = []
for path in imagesPaths :
    images.append(Multispectral(path))

# Mostrar la imagen 0 y 1 a Color
plotRgbAndHistogram(images[0])
plotRgbAndHistogram(images[1])

# Mostrar composición con Ultra Blue
# de la imagen 3
plotUblueComposite(images[3])

# Mostrar la banda Pancromatica de la imagen 6
plotPAN(images[6])

# Imprimir Información de la imagen 6
printImageDataInfo(images[6])


# Mostrar Imágenes y Gráficas
plt.show()

