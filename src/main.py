'''
Created on Apr 23, 2017

@author: Robert Phillips III
'''

from PyQt5.QtWidgets import QApplication

from plotwindow import PlotManager
        
app = QApplication([])

window = PlotManager()
window.display()

app.exec_()
