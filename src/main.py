'''
Created on Apr 23, 2017

@author: Robert Phillips III
'''

import sys

from PyQt5.QtWidgets import QApplication

from plotwindow import QPlotWindow
        
app = QApplication([])

window = QPlotWindow()
window.show()

app.aboutToQuit.connect(window.cleanup)

sys.exit(app.exec_())