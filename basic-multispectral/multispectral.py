import numpy as np
import gdal as gd
from pathlib import Path

class Multispectral:

#********************************* Default Config ************************************

    validExtensions = ['sentinel', 'landsat']
    extensionsConfig = {
        'sentinel' : {
            'fileExtension' : 'jp2',
            'vnirBandsNames' : ['B02',  'B03', 'B04', 'B08']
        },
        'landsat' : {
            'fileExtension' : 'tif',
            'vnirBandsNames' : ['sr_band1',  'sr_band2', 'sr_band3', 'sr_band4']
        },
    }

    idealShape = (1280, 720)
    chache = True

#********************************* Constructor **************************************

    def __init__(self, path, idealShape = None, cache = None) :
        path_split = path.split('.')
        self.idealShape = idealShape if not (idealShape is None) else Multispectral.idealShape
        self.chache = cache if not (cache is None) else Multispectral.chache
        self.chache = self.chache and not (self.idealShape is None)
        self.extension = path_split[-1]
        if not(self.extension in Multispectral.validExtensions) :
            raise 'Invalid Path Extension'
        self.pathFolder = Path('.'.join(path_split[0:-1]))
        self.config = Multispectral.extensionsConfig[self.extension]
        self.namePatern = self.__findPathsPatern__(
            self.pathFolder.glob('**/*.' + self.config['fileExtension']))
        self.__openBands__()
        if self.chache:
            cacheForderName = str(self.idealShape[0])+ '_' + str(self.idealShape[1]) 
            self.pathCahe = self.pathFolder/'.multispectral/cache'/cacheForderName
        if not self.__loadCache__() :
            self.vnir = self.__loadAtShape__(self.vnirDataSets, self.idealShape)
            self.__saveCache__()
        self.__rgb__ = None

#**********************************  User Methods ***********************************

    def rgb(self):
        if self.__rgb__ is None:
            self.__rgb__ = np.zeros((self.vnir.shape[0], self.vnir.shape[1], 3))
            self.__rgb__[:,:,0] = self.__normaliceBand__(self.vnir[:,:,2])
            self.__rgb__[:,:,1] = self.__normaliceBand__(self.vnir[:,:,1])
            self.__rgb__[:,:,2] = self.__normaliceBand__(self.vnir[:,:,0])
        return self.__rgb__    

#******************************** Intern Methods ************************************

    def __normaliceBand__(self, band):
        b_min, b_max = np.min(band), np.max(band)
        return (band - b_min)/(b_max - b_min)

    def __openDataSets__(self, path_names):
        dataSets = []
        for path in path_names:
            dataSets.append(gd.Open(path)) 
        return dataSets

    def __openBands__(self):
        vnirBands = []
        for bandName in self.config['vnirBandsNames']:
            vnirBands.append(
                str(self.pathFolder) + 
                '/' + self.namePatern + bandName + 
                '.' + self.config['fileExtension'])
        self.vnirDataSets = self.__openDataSets__(vnirBands)
        
    def __findPathsPatern__(self, paths):
        paths = list(paths)
        patern = paths[0].name
        count = 0
        while count  < len(paths):
            count = 0
            patern = patern[0:-1]
            for path in paths :
                if patern in path.name:
                    count = count + 1 
                else:
                    break
        return patern
    
    def __loadAtShape__(self, dataSets, idealShape) :    
        inShape = np.array((dataSets[0].RasterYSize, dataSets[0].RasterXSize))
        if idealShape is None:
            out = np.zeros(inShape.tolist() + [len(dataSets)])
            for d in range(len(dataSets)) :
                out[:,:,d] = dataSets[d].ReadAsArray()
            return out
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

    def __loadCache__(self) :
        if not self.chache :
            return False
        if not (self.pathCahe/'vnir.npy').exists() :
            return False
        self.vnir = np.load(self.pathCahe/'vnir.npy')
        return True
        
    def __saveCache__(self) :
        if not self.chache :
            return False
        if not self.pathCahe.exists() : 
            self.pathCahe.mkdir(parents = True, exist_ok=True)
        np.save(self.pathCahe/'vnir.npy', self.vnir)
        return True
