import numpy as np
import gdal as gd
from pathlib import Path

def findPathsPatern(paths):
    count = 0
    patern = paths[0].name
    while count < len(paths):
        count = 0
        patern = patern[0:-1]
        for i in range(len(paths)):
            if patern in paths[i].name:
                count = count + 1 
            else:
                break
    return patern

class Multispectral:
    
    workShape = (1280, 720)
    validTypes = ['sentinel', 'landsat']

    def __init__(self, path) :
        path_split = path.split('.')
        self.type = path_split[-1]
        self.path_folder = '.'.join(path_split[0:-1])
        if not(self.type in Multispectral.validTypes) :
             raise 'Invalid Path'
        self.path = Path(self.path_folder)
        if self.type == 'sentinel' :
            files = list(self.path.glob('**/*.jp2'))
            self.name_patern = findPathsPatern(files)
            self.openSentinelBands()
        elif self.type == 'landsat' :
            files = list(self.path.glob('**/*.tif'))
            self.name_patern = findPathsPatern(files)
            self.openLandsatBands()
        self.vnir = self.loadAtShape(self.vnir_dataSets, self.workShape)
        self._rgb = None
    
    def rgb(self):
        if self._rgb == None:
            self._rgb = np.zeros((self.vnir.shape[0], self.vnir.shape[1], 3))
            self._rgb[:,:,0] = self.vnir[:,:,2]
            self._rgb[:,:,1] = self.vnir[:,:,1]
            self._rgb[:,:,2] = self.vnir[:,:,0]
            self._rgb = self.rgb/np.max(self._rgb)
        return self._rgb

    def openDataSets(self, path_names):
        dataSets = []
        for path in path_names:
            dataSets.append(gd.Open(path)) 
        return dataSets

    def openSentinelBands(self):
        vnir = [
            self.path_folder + '/' + self.name_patern + 'B02.jp2',
            self.path_folder + '/' + self.name_patern + 'B03.jp2',
            self.path_folder + '/' + self.name_patern + 'B04.jp2',
            self.path_folder + '/' + self.name_patern + 'B08.jp2',
        ]
        self.vnir_dataSets = self.openDataSets(vnir)
        

    def openLandsatBands(self):
        vnir = [
            self.path_folder + '/' + self.name_patern + 'sr_band1.tif',
            self.path_folder + '/' + self.name_patern + 'sr_band2.tif',
            self.path_folder + '/' + self.name_patern + 'sr_band3.tif',
            self.path_folder + '/' + self.name_patern + 'sr_band4.tif',
        ]
        self.vnir_dataSets = self.openDataSets(vnir)
        
    
    def loadAtShape(self, dataSets, idealShape) :
        #inShape = np.array((dataSets[0].RasterXSize, dataSets[0].RasterYSize))
        inShape = np.array((dataSets[0].RasterYSize, dataSets[0].RasterXSize))
        div = int(max(int(np.max(inShape/np.array(idealShape))) + 1, 1))
        w_pix = int(min(4000, 400000/div**2))
        out = np.zeros(np.floor(inShape/div).astype(int).tolist() + [len(dataSets)])
        for d in range(len(dataSets)) :
            xoff = yoff = int(0)
            while yoff < out.shape[1] :
                width = int(min(inShape[1]- xoff * div, div * w_pix))
                w = dataSets[d].ReadAsArray(yoff * div, xoff * div, div, width)
                steps = int(width/div)
                for i in range(steps):
                    out[xoff + i, yoff, d] = np.mean(w[i*div:i*div + div, :])
                xoff = xoff + w_pix
                if xoff >= out.shape[0] : 
                    xoff, yoff = 0, yoff + 1
        return out

    def rgb(self):
        pass


