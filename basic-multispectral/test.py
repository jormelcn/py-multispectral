import multispectral as multi
import matplotlib.pyplot as plt
import numpy as np
import gdal as gd   

mlt = multi.Multispectral('../sentinel-imagery/IMG_DATA_A004055_201715T152714.sentinel')
#mlt = multi.Multispectral('../landsat-imagery/LC080090562017121801T1-SC20181005111414.landsat')
print(mlt.vnir.shape)
rgb = mlt.rgb()
plt.imshow(rgb, cmap='gray')

plt.show()

