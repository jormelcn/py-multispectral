import numpy as np
import gdal as gd
from pathlib import Path

class Multispectral:

#********************************* Default Config ************************************

    validExtensions = ['sentinel', 'landsat8']
    extensionsConfig = {
        'sentinel' : {
            'fileExtension' : 'jp2',
            'vnirBandsNames' : ['B02',  'B03', 'B04', 'B08'],
            'ublueBandName' : 'B01'
        },
        'landsat8' : {
            'fileExtension' : 'tif',
            'vnirBandsNames' : ['BAND2',  'BAND3', 'BAND4', 'BAND5'],
            'ublueBandName' : 'BAND1',
            'panBandName' : 'BAND8'
        },
    }

    idealShape = (1280, 720)
    cache = True
    vervose = False

    RGBDinamicRange = .93
    colorSpacePower = .5

    linearSpace = np.linspace(0, 1, 100)
    colorSpace = 2 - 2/(linearSpace**colorSpacePower + 1)

#********************************* Constructor **************************************

    def __init__(self, path, idealShape = None, cache = None) :
        path_split = path.split('.')
        self.idealShape = idealShape if not (idealShape is None) else Multispectral.idealShape
        self.cache = cache if not (cache is None) else Multispectral.cache
        self.cache = self.cache and not (self.idealShape is None)
        self.extension = path_split[-1]
        if not(self.extension in Multispectral.validExtensions) :
            raise ValueError('Invalid Path Extension')
        self.pathFolder = Path('.'.join(path_split[0:-1]))
        if not self.pathFolder.exists() :
            raise FileNotFoundError('Data Folder Not Exist') 
        self.config = Multispectral.extensionsConfig[self.extension]
        self.__findPathsPatern__()
        self.__openBands__()
        cacheForderName = str(self.idealShape[0])+ '_' + str(self.idealShape[1]) 
        self.pathCahe = self.pathFolder/'.multispectral/cache'/cacheForderName
        self.__rgb__  = None
        self.__vnir__ = None
        self.__ublue__ = None
        self.__pan__ = None
#**********************************  User Methods ***********************************

    def pan(self):
        if self.__pan__ is None :
            self.__pan__ = self.__loadDataGroup__('pan', self.panDataSet, np.multiply(self.idealShape, 2))[:,:,0] 
        return self.__pan__

    def ublue(self):
        if self.__ublue__ is None :
            self.__ublue__ = self.__loadDataGroup__('ublue', self.ublueDataSet, self.idealShape)[:,:,0] 
        return self.__ublue__

    def vnir(self):
        if self.__vnir__ is None :
            self.__vnir__ = self.__loadDataGroup__('vnir', self.vnirDataSets, self.idealShape)
        return self.__vnir__

    def rgb(self, cache = True):
        if self.__rgb__ is None or not cache:
            vnir = self.vnir()
            self.__rgb__ = Multispectral.composite(vnir[:,:,2], vnir[:,:,1], vnir[:,:,0])   
        return self.__rgb__
    
    @staticmethod
    def composite(r, g, b):
        _img = np.interp(
            Multispectral.__normalice__(np.dstack((r, g, b))), 
            Multispectral.linearSpace, 
            Multispectral.colorSpace)
        return Multispectral.__maxDinamicRange__(_img)


#******************************** Intern Methods ************************************
 
    def __loadDataGroup__(self, cachePathFile, datasetGroup, shape):
        dataGroup = None
        if self.cache :
            dataGroup = self.__loadFromCache__(cachePathFile)
        if dataGroup is None:
            if None in datasetGroup : return None
            self.__print__('Loading %s %s image from Dataset...' % (self.pathFolder.name, cachePathFile))
            dataGroup = self.__loadAtShape__(datasetGroup, shape)
            if self.cache :
                self.__saveCache__(cachePathFile, dataGroup)
        return dataGroup

    def __print__(self, message, end = '\n'):
        if Multispectral.vervose:
            print(message, end=end)

    @staticmethod
    def __normalice__(img):
        _nan = max(-100, np.min(img))
        _min = np.min(img[img > _nan])
        _max = np.max(img)
        return np.clip((img - _min)/(_max - _min), 0,1 )

    @staticmethod
    def __maxDinamicRange__(img):        
        mins = np.zeros(img.shape[2])
        maxs = np.zeros(img.shape[2])
        for i in range(img.shape[2]):
            relevant = img[:,:,i][img[:,:,i] > 0]
            mins[i] = np.quantile(relevant , 1 - Multispectral.RGBDinamicRange)
            maxs[i] = np.quantile(relevant, Multispectral.RGBDinamicRange)
        _min = np.min(mins)
        _max = np.max(maxs)
        return np.interp(img, 
        (0, _min, _max, np.max(img)), 
        (0, .1, .9, 1))

    @staticmethod
    def __openDataSets__(path_names):
        dataSets = []
        for path in path_names:
            dataSets.append(gd.Open(path)) 
        return dataSets

    def __openBands__(self):
        vnirBands = []
        basePath = str(self.pathFolder) + '/' + self.namePatern
        for bandName in self.config['vnirBandsNames']:
            vnirBands.append(basePath + bandName + '.' + self.config['fileExtension'])
        self.vnirDataSets = Multispectral.__openDataSets__(vnirBands)
        ublueBand = basePath + self.config['ublueBandName'] + '.' + self.config['fileExtension']
        self.ublueDataSet = Multispectral.__openDataSets__([ublueBand])
        if 'panBandName' in self.config :
            panBand = basePath + self.config['panBandName'] + '.' + self.config['fileExtension']
            self.panDataSet = Multispectral.__openDataSets__([panBand])
        
    def __findPathsPatern__(self):
        paths = list(self.pathFolder.glob('**/*.' + self.config['fileExtension']))
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
        self.namePatern = patern
    
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
            loaded = d/len(dataSets)
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
                    loaded = loaded + (1/out.shape[1])*(1/len(dataSets))
                    self.__print__('  loaded {:.0f} %'.format(loaded*100.0), end = '\r')
        self.__print__('\n')
        return out

    def __loadFromCache__(self, filePath) :
        if not (self.pathCahe/(filePath + '.npy')).exists() :
            return None
        self.__print__('Loading %s %s data from Cache' % (self.pathFolder.name, filePath))
        return np.load(self.pathCahe/(filePath + '.npy'))
        
    def __saveCache__(self, filePath, data) :
        if not self.pathCahe.exists() : 
            self.pathCahe.mkdir(parents = True, exist_ok=True)
        np.save(self.pathCahe/(filePath + '.npy'), data)
