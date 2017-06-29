'''
Created on Apr 25, 2017

@author: Robert Phillips III
'''

import numpy as np

from PyQt5.Qt import QWidget
from PyQt5.Qt import QFrame
from PyQt5.Qt import QVBoxLayout
from PyQt5.Qt import QPushButton
from PyQt5.Qt import QListWidget
from PyQt5.Qt import QComboBox
from PyQt5.Qt import QLabel

from PyQt5.QtCore import Qt

class QHorizontalLine(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        
class QPlotList(QWidget):
    def __init__(self, label, btntext, parent=None):
        QWidget.__init__(self, parent=parent)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn = QPushButton()
        self.btn.setText(btntext)
        self.btn.clicked.connect(self.forwardClickEvt)

        self.list = QListWidget()
        self.list.currentTextChanged.connect(self.listItemSelected)
        
        self.label = QLabel()
        self.label.setText(label)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.btn)
        
        self.btnclicked = None
        self.selected = None
        
    def listItemSelected(self, label):
        self.selected = label
        
    def forwardClickEvt(self):
        if self.selected is None or self.btnclicked is None:
            return
        
        self.btnclicked(self.selected)
        
    def onClick(self, slot):
        self.btnclicked = slot
        
    def addPlotSelection(self, plot):
        self.list.addItem(plot)
    
    def removePlotSelection(self, plot):
        items = self.list.findItems(plot, Qt.MatchExactly)
        if len(items) == 0:
            return
        
        self.list.takeItem(self.list.row(items[0]))
        
class QPlotSideBar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
                
        self.srclabel = QLabel()
        self.srclabel.setText('Plot Data Source:')
        
        self.datasrc = QComboBox()
        self.datasrc.currentIndexChanged.connect(self.onSourceChanged)
        self.datasrc_callbacks = []
        
        self.off = QPlotList('Available Plots:', 'Add Plot', self)
        self.off.onClick(self.onAddPlot)
        self.off_callbacks = []
        
        self.on = QPlotList('Active Plots:', 'Remove Plot', self)
        self.on.onClick(self.onRemovePlot)
        self.on_callbacks = []
        
        self.layout.addWidget(self.srclabel)
        self.layout.addWidget(self.datasrc)
        self.layout.addWidget(QHorizontalLine())
        self.layout.addWidget(self.off)
        self.layout.addWidget(QHorizontalLine())
        self.layout.addWidget(self.on)
        
        self.setLayout(self.layout)

    def addSource(self, source):
        self.datasrc.addItem(source)
        
    def addSources(self, sources):
        for src in sources:
            self.addSource(src)
            
    def setSource(self, source):
        index = -1
        for i in range(self.datasrc.count()):
            if self.datasrc.itemText(i) == source:
                index = i
                
        if index != -1:
            self.datasrc.setCurrentIndex(index)
            
    def addPlotType(self, ptype):
        self.off.addPlotSelection(ptype)
        self.on.removePlotSelection(ptype)
        
    def removePlotType(self, ptype):
        self.on.addPlotSelection(ptype)
        self.off.removePlotSelection(ptype)
        
    def addSourceChangedCallback(self, callback):
        self.datasrc_callbacks.append(callback)
        
    def addAddPlotCallback(self, callback):
        self.off_callbacks.append(callback)
        
    def addRemovePlotCallback(self, callback):
        self.on_callbacks.append(callback)
        
    def onSourceChanged(self, index):
        source = self.datasrc.itemText(index)
        
        for function in self.datasrc_callbacks:
            function(source)
            
    def onAddPlot(self, plot):
        for function in self.off_callbacks:
            function(plot)
            
    def onRemovePlot(self, plot):
        for function in self.on_callbacks:
            function(plot)
            

class QRealTimePlot(object):
    def __init__(self, spec):
        self.xvals = []
        self.yvals = []
        
        self.yvals_filtered = []
        
        self.type    = spec.get_type()
        self.name    = spec.get_name()
        self.reclen  = spec.get_reclen()        
        self.period  = spec.get_period()        
        self.ylimits = spec.get_ybounds()
        self.taps    = spec.get_taps()
        
        self.defaulton = spec.get_state()
        
        self.curve  = None
        self.window = None
        
    def add(self, parent, row, col):
        self.window = parent.addPlot(title=self.name, row=row, col=col)
        self.curve  = self.window.plot(self.xvals, self.yvals, pen='r')
        self.window.disableAutoRange()
        self.window.setXRange(0, self.period * self.reclen)
        self.window.setYRange(self.ylimits[0], self.ylimits[1])
        
        self.row = row
        self.col = col
        
    def remove(self):
        self.window = None
        self.curve  = None
    
    def update(self, value):
        if self.curve is None:
            return
        
        size = len(self.yvals)
        if size == self.reclen:
            self.yvals.pop()
        else:
            self.xvals.append((size + 1) * self.period)
            
        self.yvals.insert(0, value)
        self.curve.setData(self.xvals, self.yvals)
        
        if not self.taps is None:
            self.yvals_filtered.append(self.filter())
            
    def fft(self):
        sp = np.fft.fft(self.yvals)
        x  = np.fft.fftfreq(len(sp.real), self.period)
        
        n = len(self.yvals)
        self.fft = (x[:n/2], np.abs(sp.real)[:n/2])
        
    def set_taps(self, taps):
        self.taps = taps
        
    def filter(self):
        if len(self.taps) > len(self.yvals):
            return 0.0
        
        avg = 0.0
        for i in range(len(self.taps)):
            avg += (self.taps[i] * self.yvals[i])
        
        return avg 
    
    def pk_to_pk(self):
        if len(self.values) == 0:
            return 0.0
        
        minval = self.values[0]
        maxval = self.values[0]
        
        for val in self.values:
            if val > maxval:
                maxval = val
            elif val < minval:
                minval = val
                
        return (maxval - minval)
        
    def get_data_type(self):
        return self.type
    
    def get_name(self):
        return self.name
    
    def get_state(self):
        return self.defaulton