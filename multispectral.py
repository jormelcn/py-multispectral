import numpy as np
import gdal as gd
from pathlib import Path

class Multispectral:

#********************************* Default Config ************************************

    validExtensions = ['sentinel2', 'landsat8']
    extensionsConfig = {
        'sentinel2' : {
            'bandsExtension' : 'jp2',
            'nameSeparator' : '_',
            'bandsPrefixes' : ['band', 'b', 'B', 'BAND', 'B0', 'BAND0'],
            'vnirBands' : ['2', '3', '4', '8'],
            'ublueBand' : '1',
        },
        'landsat8' : {
            'bandsExtension' : 'tif',
            'nameSeparator' : '_',
            'bandsPrefixes' : ['band', 'b', 'B', 'BAND', 'B0', 'BAND0'],
            'vnirBands' : ['2', '3', '4', '5'],
            'ublueBand' : '1',
            'panBand' : '8',
        },
    }

    resizeFactor = 8
    cache = True
    verbose = False

    RGBDinamicRange = .93
    colorSpacePower = .5

    linearSpace = np.linspace(0, 1, 100)
    colorSpace = 2 - 2/(linearSpace**colorSpacePower + 1)

#********************************* Constructor **************************************

    def __init__(self, path, resizeFactor = None, cache = None) :
        path_split = path.split('.')
        self.resizeFactor = resizeFactor if not resizeFactor is None else Multispectral.resizeFactor
        self.cache = cache if not (cache is None) else Multispectral.cache
        self.cache = self.cache and not self.resizeFactor is None
        self.extension = path_split[-1]
        if not(self.extension in Multispectral.validExtensions) :
            raise ValueError('Invalid Path Extension')
        self.pathFolder = Path('.'.join(path_split[0:-1]))
        if not self.pathFolder.exists() :
            raise FileNotFoundError('Data Folder Not Exist') 
        self.config = Multispectral.extensionsConfig[self.extension]
        self.__selectBandsFiles__()
        self.__openAllBandsGroups__()
        cacheFolderName = str(self.resizeFactor)
        self.pathCahe = self.pathFolder/'.multispectral/cache'/cacheFolderName
        self.__rgb__  = None
        self.__vnir__ = None
        self.__ublue__ = None
        self.__pan__ = None
        self.__bands__ = {}

#**********************************  User Methods ***********************************

    def band(self, band):
        band = str(band)
        if not band in self.__bands__ :
            ds = self.__openBandsGroup__([band])
            self.__bands__[band] = self.__loadDataGroup__('band' + band, ds)[:,:,0] 
        return self.__bands__[band]

    def pan(self):
        if self.__pan__ is None :
            self.__pan__ = self.__loadDataGroup__('pan', self.panDataset)[:,:,0] 
        return self.__pan__

    def ublue(self):
        if self.__ublue__ is None :
            self.__ublue__ = self.__loadDataGroup__('ublue', self.ublueDataset)[:,:,0] 
        return self.__ublue__

    def vnir(self):
        if self.__vnir__ is None :
            self.__vnir__ = self.__loadDataGroup__('vnir', self.vnirDatasets)
        return self.__vnir__

    def rgb(self, cache = True):
        if self.__rgb__ is None or not cache:
            vnir = self.vnir()
            self.__rgb__ = Multispectral.composite(vnir[:,:,2], vnir[:,:,1], vnir[:,:,0])   
        return self.__rgb__
    
    @staticmethod
    def color(reflectance):
        _img = np.interp(
            Multispectral.__normalice__(reflectance), 
            Multispectral.linearSpace, 
            Multispectral.colorSpace)
        return Multispectral.__maxDinamicRange__(_img)

    @staticmethod
    def composite(r, g, b):
        _img = np.interp(
            Multispectral.__normalice__(np.dstack((r, g, b))), 
            Multispectral.linearSpace, 
            Multispectral.colorSpace)
        return Multispectral.__maxDinamicRange__(_img)


#******************************** Intern Methods ************************************
 
    def __loadDataGroup__(self, cachePathFile, datasetGroup):
        dataGroup = None
        if self.cache :
            dataGroup = self.__loadFromCache__(cachePathFile)
        if dataGroup is None:
            if None in datasetGroup : raise ValueError('Not dataset found for all solicited data, verify data files')
            self.__print__('Loading %s %s image from Dataset...' % (self.pathFolder.name, cachePathFile))
            dataGroup = self.__loadAtFactor__(datasetGroup, self.resizeFactor)
            if self.cache :
                self.__saveCache__(cachePathFile, dataGroup)
        return dataGroup

    def __print__(self, message, end = '\n'):
        if Multispectral.verbose:
            print(message, end=end)

    @staticmethod
    def __normalice__(img):
        _nan = max(-100, np.min(img))
        _min = np.min(img[img > _nan])
        _max = np.max(img)
        return np.clip((img - _min)/(_max - _min), 0,1 )

    @staticmethod
    def __maxDinamicRange__(img): 
        if len(img.shape) == 3:
            mins = np.zeros(img.shape[2])
            maxs = np.zeros(img.shape[2])
            for i in range(img.shape[2]):
                relevant = img[:,:,i][img[:,:,i] > 0]
                mins[i] = np.quantile(relevant , 1 - Multispectral.RGBDinamicRange)
                maxs[i] = np.quantile(relevant, Multispectral.RGBDinamicRange)
            _min = np.min(mins)
            _max = np.max(maxs)
        else :
            relevant = img[img > 0]
            _min = np.quantile(relevant , 1 - Multispectral.RGBDinamicRange)
            _max = np.quantile(relevant, Multispectral.RGBDinamicRange)
        return np.interp(img, 
        (0, _min, _max, np.max(img)), 
        (0, .1, .9, 1))

    def __openBandsGroup__(self, bands):
        datasets = []
        for band in bands:
            bandPath = self.__findBandPathFile__(band)
            if bandPath is None:
                self.__print__('Warning: %s band %s not Found...' % (self.pathFolder.name, band))
                datasets.append(None)
            else :
                datasets.append(gd.Open(str(self.pathFolder/bandPath) )) 
        return datasets

    def __openAllBandsGroups__(self):
        if 'vnirBands' in self.config:
            self.vnirDatasets = self.__openBandsGroup__(self.config['vnirBands'])
        else :
            self.vnirDatasets = None
        if 'ublueBand' in self.config:
            self.ublueDataset = self.__openBandsGroup__([self.config['ublueBand']])
        else :
            self.ublueDataset = None
        if 'panBand' in self.config:
            self.panDataset = self.__openBandsGroup__([self.config['panBand']])
        else :
            self.panDataset = None

    def __selectBandsFiles__(self):
        filesNames = []
        self.bandsFilesExtension = self.config['bandsExtension']
        paths = list(self.pathFolder.glob('**/*.' + self.bandsFilesExtension))
        if len(paths) == 0:
            self.bandsFilesExtension = self.config['bandsExtension'].upper()
            paths = list(self.pathFolder.glob('**/*.' + self.bandsFilesExtension))
        if len(paths) == 0:
            raise ValueError('Bands Files Not found')
        for path in paths:
            filesNames.append(path.name.split('.')[0])
        self.bandsFilesNames = filesNames

    def __findBandPathFile__(self, bandName):
        filesBands = []
        for fileName in self.bandsFilesNames:
            filesBands.append(fileName.split(self.config['nameSeparator'])[-1])
        for prefix in self.config['bandsPrefixes'] :
            try: return self.bandsFilesNames[ filesBands.index(prefix + bandName) ] + '.' + self.bandsFilesExtension
            except : pass
        return None

    def __loadAtFactor__(self, datasets, factor) :
        for ds in datasets : 
            if not ds is None : break
        inSize = np.array((ds.RasterYSize, ds.RasterXSize))
        outSize = inSize if factor is None else np.floor(inSize/factor).astype(int)
        out = np.full(outSize.tolist() + [len(datasets)], np.nan)
        w_pix = None if factor is None else int(min(5000, 500000/factor**2))
        for d in range(len(datasets)) :
            loaded = d/len(datasets)
            if factor is None:
                out[:,:,d] = datasets[d].ReadAsArray()
                continue
            xoff = yoff = int(0)
            while yoff < out.shape[1] : 
                width = int(min(inSize[0]- xoff * factor, factor * w_pix))
                w = datasets[d].ReadAsArray(yoff * factor, xoff * factor, factor, width)
                steps = int(width/factor)
                for i in range(steps):
                    out[xoff + i, yoff, d] = np.mean(w[i*factor:i*factor + factor, :])
                xoff = xoff + w_pix
                if xoff >= out.shape[0] : 
                    xoff, yoff = 0, yoff + 1
                    loaded = loaded + (1/out.shape[1])*(1/len(datasets))
                    self.__print__('  loaded {:.0f} %'.format(loaded*100.0), end = '\r')
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
