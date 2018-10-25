#********************************** Librerias ****************************************
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
    r_hist, interv = np.histogram(r[np.logical_and(r > 0, r < 1)] ,100)
    g_hist = np.histogram(g[np.logical_and(g > 0, g < 1)] ,100)[0]
    b_hist = np.histogram(b[np.logical_and(b > 0, b < 1)] ,100)[0]
    plt.plot(interv[:-1], r_hist/rgb.size, color='r')
    plt.plot(interv[:-1], g_hist/rgb.size, color='g')
    plt.plot(interv[:-1], b_hist/rgb.size, color='b')

# Muestra la banda NIR a escala de grises
def plotNIR(img):
    plt.figure()
    plt.title('Banda NIR a Escala de Grises')
    plt.imshow(img.vnir[:,:,3], cmap='gray')

# Imprime Información acerca de los datos contenidos en la imagen
def printImageDataInfo(img):
    print('\nDatos de imagen %s' % (img.pathFolder.name))
    print('Sensor: ', img.extension)
    print('Images Name Patern: ', img.namePatern)
    # Obtener array VNIR
    vnir = img.vnir
    print('VNIR Data Array Shape ', vnir.shape)


#******************************************************************************************



#************************* Programa de Ejemplo de Uso de Multispectral *******************

# Trabajar con images de tamaño máximo 800x800
Multispectral.idealShape = (800, 800)

# Trabajar con Imágenes Originales
#Multispectral.idealShape = None

# Habilitar modo informativo (Imprime los procedimientos que ejecuta)
Multispectral.vervose = True


# Rutas a las imágenes a cargar
imagesPaths = [
    '../sentinel-imagery/IMG_DATA_A004055_201715T152714.sentinel',
    '../landsat-imagery/LC080090562017121801T1-SC20181005111414.landsat8',
    '../sentinel-imagery/IMG_DATA_A010747_20170713T153113.sentinel',
    '../sentinel-imagery/IMG_DATA_A010747_20170713T153113.sentinel',
    '../sentinel-imagery/IMG_DATA_A013035_20171220T153107.sentinel'
] 

# Cargar Imágenes con Multispectral
images = []
for path in imagesPaths :
    images.append(Multispectral(path))

# Mostrar las Imagenes 1 y 3 a Color
plotRgbAndHistogram(images[3])
plotRgbAndHistogram(images[1])

# Mostrar la banda NIR se la imagen 0 a escala de grises
plotNIR(images[0])

# Imprimir Información de la imagen 1
printImageDataInfo(images[1])


# Mostrar Imágenes y Gráficas
plt.show()

