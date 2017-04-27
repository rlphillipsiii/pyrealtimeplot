'''
Created on Apr 23, 2017

@author: Robert Phillips III
'''

import pyqtgraph as pg

import plotjson

from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QApplication

from PyQt5.Qt import QFileDialog
from PyQt5.Qt import QAction
from PyQt5.Qt import QWidget
from PyQt5.Qt import QMainWindow
from PyQt5.Qt import QHBoxLayout

from plotwidgets import QPlotSideBar
from plotwidgets import QRealTimePlot

class PlotManager(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        src, spec = plotjson.get_configuration('../config.json')
        
        self.datasrc = src
        self.datasrc.start()
        
        self.plots   = [ QRealTimePlot(config) for config in spec.get_plot_specs() ]
        self.active  = []
        
        pg.setConfigOptions(antialias=True)

        parent.setWindowTitle(spec.get_title())
                
        self.plotwindow = pg.GraphicsWindow()
        
        self.plotconfig = QPlotSideBar(self)
        self.plotconfig.addSources(self.datasrc.get_sources())
        self.plotconfig.addSourceChangedCallback(self.datasrc.set_source)
        self.plotconfig.addAddPlotCallback(self.add_plot)
        self.plotconfig.addRemovePlotCallback(self.remove_plot)
        
        for plot in self.plots:
            self.plotconfig.addPlotType(plot.get_name())
            
        for plot in self.plots:
            if plot.get_state():
                self.add_plot(plot.get_name())
                
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
        
    def save_setup(self, fname):
        settings = { 'source' : self.datasrc.get_active_source(), 'plots' : [ plot.get_name() for plot in self.active ]}
        plotjson.write_configuration(fname, settings)
        
    def recall_setup(self, fname):
        self.plotwindow.clear()
        for plot in self.active:
            plot.remove()
            
        self.active = []
        
        src, plots = plotjson.get_recall_settings(fname)
        for plot in plots:
            self.add_plot(plot)
            
        self.plotconfig.setSource(src)
        
    def display(self):
        self.datasrc.start()
        
        self.show()
        
    def __del__(self):
        print 'Destroyed'
        
    def cleanup(self):
        self.datasrc.cleanup()
        
    def update(self):
        while self.datasrc.has_sample():        
            samples = self.datasrc.get_sample()
            
            for datatype, sample in samples:
                for plot in self.active:
                    if plot.get_data_type() == datatype:
                        plot.update(sample)
                        
class QPlotWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.window = PlotManager(self)
        self.setCentralWidget(self.window)
        
        self.resize(1000, 600)
        
        rect = self.geometry()
        rect.moveCenter(QApplication.desktop().availableGeometry().center())
        self.setGeometry(rect)
    
        self._init_menu()
        
    def _init_menu(self):
        menu = self.menuBar()
        filemenu = menu.addMenu('&File')
        
        save = QAction('Save Setup', self)
        save.setShortcut('Ctrl+S')
        save.triggered.connect(self.save_setup)
        
        recall = QAction('Recall Setup', self)
        recall.setShortcut('Ctrl+R')
        recall.triggered.connect(self.recall_setup)
        
        stop = QAction('Exit', self)
        stop.triggered.connect(self.exit)
        
        filemenu.addAction(save)
        filemenu.addAction(recall)
        filemenu.addAction(stop)
        
    def save_setup(self):
        fname = QFileDialog.getSaveFileName(self, caption='Save Setup File', filter='*.set')
        if fname:
            self.window.save_setup(str(fname[0]) + '.set')
            
    def recall_setup(self):
        fname = QFileDialog.getOpenFileName(self, caption='Recall Setup File', filter='*.set')
        if fname:
            self.window.recall_setup(str(fname[0]))
            
    def cleanup(self):
        self.window.cleanup()
        
    def exit(self):
        pass