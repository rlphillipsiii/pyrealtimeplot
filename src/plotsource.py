'''
Created on Apr 23, 2017

@author: Robert Phillips III
'''

from PyQt5.QtCore import QThread
from PyQt5.QtCore import QMutex

import abc
import serial
import time
import struct
import platform

class DataSource(QThread):    
    def __init__(self):
        QThread.__init__(self)
        
        self.paused = False
        self.mutex  = QMutex()
        self.queue  = []
        
    def lock(self):
        self.mutex.lock()
        
    def unlock(self):
        self.mutex.unlock()
        
    def has_sample(self):
        self.lock()
        length = len(self.queue)
        self.unlock()
        
        return (length > 0)
        
    def get_sample(self):
        self.lock()
        val = self.queue.pop()
        self.unlock()
        
        return val
    
    def pause(self):
        self.lock()
        self.paused = True
        self.unlock()
        
    def is_running(self):
        self.lock()
        running = (self.paused == False)
        self.unlock()
        
        return running
        
    def stop(self):
        self.interrupt()
        
        self.quit()
        self.wait()
        
    @abc.abstractmethod
    def interrupt(self):
        raise NotImplementedError('users must def interrupt to use this base class')    
        
    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError('users must define __str__ to use this base class')
        
    @abc.abstractmethod
    def get_sources(self):
        raise NotImplementedError('users must define get_sources to use this base class')
        
    @abc.abstractmethod
    def set_source(self):
        raise NotImplementedError('users must define set_source to use this base class')
        
class SerialSource(DataSource):
    NAME = 'serial'
    
    def __init__(self, baud, size, stop, parity, ports):
        DataSource.__init__(self)
        
        self.baud   = baud
        self.size   = size
        self.stop   = stop
        self.parity = parity
        
        self.port   = ''
        self.comm   = None
        self.cancel = False
        self.packet = []
        self.datatypes = []
        
        self.sources = ports
        if self.sources is None: 
            self._auto_populate_sources()
            
        self.set_source(self.sources[0])
        
        self._init_comm()
        
    def _auto_populate_sources(self):
        if platform.os == 'Windows':
            self.sources = ['COM%s' % (i + 1) for i in range(10)]
        else:
            # TODO: populate the linux sources
            self.sources = [ ]
        
    def _init_comm(self):
        try:            
            self.comm = serial.Serial(port=self.port, baudrate=self.baud, bytesize=self.size, stopbits=self.stop, parity=self.parity)
            self.comm.flushInput()
        except:
            self.comm = None
        
    def _make_int(self, index, packet=None):
        if packet is None:
            packet = self.packet
            
        return packet[index] | (packet[index+1] << 8) | (packet[index+2] << 16) | (packet[index+3] << 24)
    
    def _make_float(self, index, packet=None):
        if packet is None:
            packet = self.packet
            
        return struct.unpack('f', ''.join([ chr(val) for val in packet[index:index+4] ]))[0]
    
    def received_stop(self):
        stop = 0x7FFFFFFF
        
        if len(self.packet) < 8:
            return False
       
        last = self.packet[-8:]
        return (self._make_int(0, packet=last) == stop) and (self._make_int(4, packet=last) == stop)
    
    def decode_data(self):
        packet = self.packet[:-8]
        packet = packet[len(packet)%5:]
        
        self.datatypes = []
        
        info = []
        for i in range(len(packet)/5):
            index = i * 5
            
            self.datatypes.append(packet[index])
            info.append((packet[index], self._make_float(index + 1, packet=packet)))
            
        self.packet = []        
        return info
    
    def append_queue(self, value):
        self.lock()
        self.queue.append(value)
        self.unlock()
        
    def get_interrupt_status(self):
        self.lock()
        status = self.cancel
        self.unlock()
        
        return status
    
    def run(self):       
        interrupt = self.get_interrupt_status()
        
        while not interrupt:
            if self.comm is None:
                time.sleep(0.001)
                self._init_comm()
                continue
                
            try:                
                self.packet.append(ord(self.comm.read()))
                
                if self.is_running() and self.received_stop():
                    payload = self.decode_data()
                    
                    self.append_queue(payload)
                
                interrupt = self.get_interrupt_status()
            except:
                import traceback
                traceback.print_exc()
                self.clean_serial()
            
    def clean_serial(self):
        try:
            if not self.comm is None:
                self.comm.close()
        except:
            pass
            
        self.comm = None
        
    def interrupt(self):
        self.lock()
        self.cancel = True
        self.unlock()
        
        self.comm.cancel_read()
        
    def set_source(self, source):
        if not self.comm is None:
            self.comm.close()
            
        self.port = source
        
    def get_sources(self):
        return self.sources
    
    def __str__(self):
        print 'SerialSource Object'
        
        
class FileSource(DataSource):
    NAME = 'file'
    
    def __init__(self, fname, mode):
        self.fname = fname
        self.mode  = mode
        self.index = 0
        
        self.packets = []
        with open(fname, 'r') as f:        
            for line in f.read().split('\n'):
                sample = line.rstrip().lstrip()
                if sample == '':
                    continue
                    
                packet = [ (float(ftype), float(data)) for ftype, data in [ data.split(':') for data in sample.split(' ') ] ]
                self.packets.append(packet)
                    
    def has_sample(self):
        return self.index < len(self.packets)
        
    def get_sample(self):
        packet = self.packets[self.index]
        
        self.index += 1
        if self.index == len(self.packets) and self.mode == 'loop':
            self.index = 0
            
        return packet
        
    def get_sources(self):
        return [ "Default" ]
        
    def run(self):
        pass
            
    def interrupt(self):
        pass
        
    def __str__(self):
        print 'FileSource Object'