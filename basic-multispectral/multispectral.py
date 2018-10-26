import numpy as np
import gdal as gd
from pathlib import Path

class Multispectral:

#********************************* Default Config ************************************

    validExtensions = ['sentinel', 'landsat8']
    extensionsConfig = {
        'sentinel' : {
            'fileExtension' : 'jp2',
            'vnirBandsNames' : ['B02',  'B03', 'B04', 'B08']
        },
        'landsat8' : {
            'fileExtension' : 'tif',
            'vnirBandsNames' : ['sr_band1',  'sr_band2', 'sr_band3', 'sr_band4']
        },
    }

    idealShape = (1280, 720)
    chache = True
    vervose = False

    RGBDinamicRange = .94
    coloSpacePower = .3

#********************************* Constructor **************************************

    def __init__(self, path, idealShape = None, cache = None) :
        path_split = path.split('.')
        self.idealShape = idealShape if not (idealShape is None) else Multispectral.idealShape
        self.chache = cache if not (cache is None) else Multispectral.chache
        self.chache = self.chache and not (self.idealShape is None)
        self.extension = path_split[-1]
        if not(self.extension in Multispectral.validExtensions) :
            raise ValueError('Invalid Path Extension')
        self.pathFolder = Path('.'.join(path_split[0:-1]))
        if not self.pathFolder.exists() :
            raise FileNotFoundError('Data Folder Not Exist') 
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
            self.__rgb__ = self.__normaliceRGB__(
                np.dstack((self.vnir[:,:,2], self.vnir[:,:,1], self.vnir[:,:,0])))
        return self.__rgb__    

#******************************** Intern Methods ************************************

    def __print__(self, message):
        if Multispectral.vervose:
            print(message)

    def __colorSpace__(self, space):
        return 2 - 2/(space**Multispectral.coloSpacePower + 1)

    def __normalice__(self, img):
        _nan = max(-100, np.min(img))
        _min = np.min(img[img > _nan])
        _max = np.max(img)
        return np.clip((img - _min)/(_max - _min), 0,1 )

    def __maxDinamicRange__(self, img):        
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
        (0, 1 - Multispectral.RGBDinamicRange, Multispectral.RGBDinamicRange, 1))

    def __normaliceRGB__(self, img):
        _lin = np.linspace(0, 1, 100)
        _img = np.interp(self.__normalice__(img), _lin, self.__colorSpace__(_lin))
        return self.__maxDinamicRange__(_img)

    def __openDataSets__(self, path_names):
        dataSets = []
        for path in path_names:
            dataSets.append(gd.Open(path)) 
        if None in dataSets :
            raise ValueError('Invalid Data')
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
            self.__print__('Loading %s Original image from Dataset...' % (self.pathFolder.name))
            out = np.zeros(inShape.tolist() + [len(dataSets)])
            for d in range(len(dataSets)) :
                out[:,:,d] = dataSets[d].ReadAsArray()
            return out
        self.__print__('\nLoading %s Subsamble image from Dataset...' % (self.pathFolder.name))
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
            self.__print__('loaded ' + str((float(d + 1)/float(len(dataSets)))*100.0) + ' % ...')
        self.__print__('\n')
        return out

    def __loadCache__(self) :
        if not self.chache :
            return False
        if not (self.pathCahe/'vnir.npy').exists() :
            return False
        self.__print__('Loading %s image from Cache' % (self.pathFolder.name))
        self.vnir = np.load(self.pathCahe/'vnir.npy')
        return True
        
    def __saveCache__(self) :
        if not self.chache :
            return False
        if not self.pathCahe.exists() : 
            self.pathCahe.mkdir(parents = True, exist_ok=True)
        np.save(self.pathCahe/'vnir.npy', self.vnir)
        return True
