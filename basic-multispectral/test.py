from multispectral import Multispectral
import matplotlib.pyplot as plt

img1 = Multispectral('../sentinel-imagery/IMG_DATA_A004055_201715T152714.sentinel')
print(img1.vnir.shape)

img2 = Multispectral('../landsat-imagery/LC080090562017121801T1-SC20181005111414.landsat')
print(img2.vnir.shape)


plt.imshow(img1.rgb())
plt.figure()
plt.imshow(img2.rgb())

plt.show()

