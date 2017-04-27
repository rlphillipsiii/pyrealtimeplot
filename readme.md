# PyRealTime Plot
PyRealTime Plot is a Python based tool that leverages the QT framework to plot data <br />
in real time.  It is fully configurable by the user in terms of the data source for <br />
plots and which plots are on and plotting data.  The data can be sent in packets of <br />
any length and plotted on any one of the 255 user-definable plot types.

## Installation
This project is developed for Python 2.7 (x64).  It requires the following <br />
dependencies to run:
- numpy
- pyqtgraph
- PyQt5

## Usage
In order to open up the GUI, simply run the command 'python main.py'. <br /><br />

The GUI is meant to be flexible and allow the user to configure the plots available <br />
via the file config.json.  The configuration file allows the user to specify the types <br />
of plots that are available, the properties of each plot and the data source for the <br />
plots.  Each plot described in the config file can be added or removed at runtime and <br />
has a data type.  The data type is the a unique identifier that is used to determine, <br />
which numbers from the data source are to go to each plot. Check the config.example <br />
file for more details on how each plot and data source can be configured. <br /><br />

In order to start plotting data, the data sent via the data source must adhere to a <br />
certain format.  The data sent via the data source is expected to be any number of 4 <br />
byte floats accompanied by one byte indicating the data type, and an 8 byte stop <br />
signal, which is the float binary representation of NaN sent indicating the end of a <br />
packet.  The number of bytes in the payload of the packet (every byte except for the <br />
8 byte stop signal) must be a multiple of 5 as the payload is made up of 4 byte floats <br />
and their 1 byte data types.  The displayed plots are updated each time a packet is <br />
received.  Each float should be sent least significant byte first.  In the following <br />
example, the bytes are transmitted from left to right. <br /><br />

Float transmission format example: <br />
0xTT 0xNN 0xNN 0xNN 0xNN <br />
0xTT => byte corresponding to the data type <br />
0xNN => byte corresponding to the float representation of the transmitted number <br /><br />

In order to send the number -0.0027 with data type 0x00, the transmission would be: <br />
0x00 0x7c 0xf2 0x30 0xbb <br /><br />

-0.0027 is stored as 0xbb30f27c, so notice that the float is transmitted with the <br />
least significant byte FIRST. <br /><br />

After sending the floats and their data types, two NaNs must be sent to signal that <br />
the end of the packet has been reached and the plots should be updated: <br /><br />

NaN transmission: <br />
0xff 0xff 0xff 0x7f 0xff 0xff 0xff 0x7f <br /><br />

Here's what transmitting -0.0027 with data type 0x00 and -0.0433 with data type <br />
0x01 in the same packet would look like: <br />
0x00 0x7c 0xf2 0x30 0xbb 0x01 0x57 0x5b 0x31 0xbd 0xff 0xff 0xff 0x7f 0xff 0xff 0xff 0x7f <br />

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History
This tool was originally developed in order to plot data coming from a <br />
microcontroller over a serial port.  Specifically, it was developed to plot IMU <br />
sensor data in real time to analyze noise that was caused by motor vibrations on <br />
a drone.  Even though it was made with that purpose in mind, it was designed to <br />
general enough that it can plot any sequence of floats coming from a file or from <br />
a serial port.

## Future Improvements
- Different data sources for each plot
- Socket based data source
- Different y-axis types (i.e. log)

## License

