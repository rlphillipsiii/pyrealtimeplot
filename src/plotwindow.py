'''
Created on Apr 23, 2017

@author: Robert Phillips III
'''

import pyqtgraph as pg

import plotjson

from PyQt5.QtCore import QTimer

from PyQt5.Qt import QWidget
from PyQt5.Qt import QHBoxLayout

from plotwidgets import QPlotSideBar
from plotwidgets import QRealTimePlot

class PlotManager(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        src, spec = plotjson.get_configuration('../config.json')
        
        self.datasrc = src
        self.plots   = [ QRealTimePlot(config) for config in spec.get_plot_specs() ]
        self.active  = []
        
        pg.setConfigOptions(antialias=True)

        self.plotwindow = pg.GraphicsWindow(title=spec.get_title())
        
        self.plotconfig = QPlotSideBar(self)
        self.plotconfig.addSources(self.datasrc.get_sources())
        self.plotconfig.addSourceChangedCallback(self.datasrc.set_source)
        self.plotconfig.addAddPlotCallback(self.add_plot)
        self.plotconfig.addRemovePlotCallback(self.remove_plot)
        
        for plot in self.plots:
            self.plotconfig.addPlotType(plot.get_name())
            
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.plotwindow)
        self.layout.addWidget(self.plotconfig)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)
        
        self.setLayout(self.layout)
        
    def add_plot(self, name):
        count = len(self.active)
        for plot in self.plots:
            if plot.get_name() == name:
                self.active.append(plot)
                
                plot.add(self.plotwindow, count, 0)
                self.plotconfig.removePlotType(name)
                
    def remove_plot(self, name):
        self.plotwindow.clear()
    
        index = -1
        for i in range(len(self.active)):
            if self.active[i].get_name() == name:
                index = i
            else:
                row = i
                if index != -1:
                    row += 1
                    
                self.active[i].add(self.plotwindow, row, 0)
        
        if index != -1:
            self.plotconfig.addPlotType(name)
            
            self.active[index].remove()
            del self.active[index]
        
    def display(self):
        self.datasrc.start()
        
        self.show()
        
    def update(self):
        while self.datasrc.has_sample():        
            samples = self.datasrc.get_sample()
            
            for datatype, sample in samples:
                for plot in self.active:
                    if plot.get_data_type() == datatype:
                        plot.update(sample)