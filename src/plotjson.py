'''
Created on Apr 25, 2017

@author: Robert Phillips III
'''

import json

from plotsource import SerialSource
from plotsource import FileSource

class PlotSpec():
    def __init__(self, config, spec):
        self.name    = spec[PlotConfig.NAME]
        self.type    = int(spec[PlotConfig.TYPE], 16)
        self.period  = float(spec[PlotConfig.PERIOD]) if PlotConfig.PERIOD in spec else float(config[PlotConfig.GLOBAL_PERIOD])
        self.reclen  = int(spec[PlotConfig.RECLEN]) if PlotConfig.RECLEN in spec else int(config[PlotConfig.GLOBAL_RECLEN])
        
        taps = None
        if PlotConfig.TAPS in spec:
            taps = spec[PlotConfig.TAPS]
        elif PlotConfig.GLOBAL_TAPS in config:
            taps = config[PlotConfig.GLOBAL_TAPS]

        self.taps = None if taps is None else [ float(tap) for tap in taps ]
        
        ybounds = spec[PlotConfig.YBOUNDS] if PlotConfig.YBOUNDS in spec else config[PlotConfig.GLOBAL_YBOUNDS]
        self.ybounds = [ float(bound) for bound in ybounds ]
        
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.type
    
    def get_period(self):
        return self.period
    
    def get_reclen(self):
        return self.reclen
    
    def get_ybounds(self):
        return self.ybounds

    def get_taps(self):
        return self.taps
    
    
class PlotConfig():
    TITLE = 'title'
    PLOTS = 'plots'
    GLOBAL_TAPS = 'taps'
    GLOBAL_PERIOD = 'period'
    GLOBAL_RECLEN = 'reclen'
    GLOBAL_YBOUNDS = 'ybounds'
    
    NAME = 'name'
    TYPE = 'type'
    PERIOD = 'period'
    RECLEN = 'reclen'
    YBOUNDS = 'ybounds'
    TAPS = 'taps'

    def __init__(self, config):
        self.title  = config[PlotConfig.TITLE]
            
        self.plots   = [ PlotSpec(config, spec) for spec in config[PlotConfig.PLOTS] ] 
    
    def get_title(self):
        return self.title
    
    def get_plot_specs(self):
        return self.plots
    
class DataSrcConfig():
    SOURCES = 'sources'
    ACTIVE = 'active'
    CONFIGS = 'configurations'
    NAME = 'name'
    CONFIG = 'config'
    
    SERIAL_BAUD = 'baud'
    SERIAL_PORTS = 'ports'
    SERIAL_BYTESIZE = 'bytesize'
    SERIAL_STOPBITS = 'stopbits'
    SERIAL_PARITY = 'parity'
    
    FILE_PATH = 'path'
    FILE_MODE = 'mode'
    
    def __init__(self, config):
        srctype = config[DataSrcConfig.ACTIVE]
                
        settings = None
        for setting in config[DataSrcConfig.CONFIGS]:
            if setting[DataSrcConfig.NAME] == srctype:
                settings = setting
                        
        if srctype == 'serial':
            self.setup_serial_source(settings)
        elif srctype == 'file':
            self.setup_file_source(settings)
            
    def setup_serial_source(self, config):
        settings = config[DataSrcConfig.CONFIG]
        
        baud     = int(settings[DataSrcConfig.SERIAL_BAUD])
        bytesize = int(settings[DataSrcConfig.SERIAL_BYTESIZE])
        stopbits = float(settings[DataSrcConfig.SERIAL_STOPBITS])
        parity   = settings[DataSrcConfig.SERIAL_PARITY]
        
        ports = config[DataSrcConfig.SERIAL_PORTS] if DataSrcConfig.SERIAL_PORTS in config else None
        
        self.src = SerialSource(baud, bytesize, stopbits, parity, ports)
        
    def setup_file_source(self, config):
        fname = config[DataSrcConfig.FILE_PATH]
        mode  = config[DataSrcConfig.FILE_MODE]
        
        self.src = FileSource(fname, mode)
    
    def get_source(self):
        return self.src
     
class RecallConfig():
    SOURCE = 'source'
    PLOTS = 'plots'
    
    def __init__(self, config):
        self.source = config[RecallConfig.SOURCE]
        self.plots  = config[RecallConfig.PLOTS]
    
    def get_source(self):
        return self.source
    
    def get_plots(self):
        return self.plots
        
def write_configuration(fname, settings):
    with open(fname, 'w') as f:
        f.write(json.dumps(settings))
        
def get_recall_settings(fname):
    with open(fname, 'r') as data:
        config = json.load(data)
        
        recalled = RecallConfig(config)
        
        return (recalled.get_source(), recalled.get_plots())
    
    return None

def get_configuration(fname):    
    with open(fname, 'r') as data:
        config = json.load(data)
        
        src  = DataSrcConfig(config[DataSrcConfig.SOURCES]).get_source()
        plot = PlotConfig(config)
    
        return src, plot
    
    return None