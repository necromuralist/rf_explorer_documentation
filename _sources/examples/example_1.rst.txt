===================================
RF-Explorer Example One - Max Value
===================================

    :Author: hades

.. contents::



1 Description
-------------

This is the first example that comes with the ``RFExplorer`` repository.
It will display the amplitude (in dBm) and the frequency (in MHz) of the maximum value in the sweep data. The *sweep* is one sweep from the lowest to the highest frequency. It is made up of indiviual *steps*.

The amount of stored sweep data is controlled by the length of time that it scans. By default, it samples ten times a second, so if you are comparing it to something that reports less frequently, you will need to aggregate it somehow.

2 Tangle
--------

.. code:: ipython

    <<imports>>

    <<line-formats>>

    <<print-peak>>
    <<get-data>>
    <<get-peak-step>>
    <<get-peak-amplitude>>
    <<get-peak-frequency>>
    <<get-peak-data>>

    <<global-variables>>

    <<communicator-exception>>

    <<communicator>>

        <<rfe-property>>
    
        <<context-management>>

        <<communicator-setup>>
            <<get-ports>>

            <<connect-port>>

            <<reset-explorer>>

            <<get-model>>

            <<analyzer-check>>

    <<main>>
            <<setup-communicator>>
            <<setup-loop>>
                <<process-string>>
                <<print-data>>
        <<end-main>>

    <<argument-parser>>
        <<serial-port>>
        <<baud-rate>>
        <<run-time>>
        <<csv-data>>
        <<return-arguments>>

    <<executable-block>>
        <<cleanup>>

3 Imports
---------

The only real requirement is the ``RFExplorer`` module - which, despite the name is a **module** not a class.

.. code:: ipython

    # python standard library
    import argparse
    import time
    from datetime import datetime, timedelta

    # from pypi
    import RFExplorer

4 Print Peak
------------

This is a helper function to get only the peak data from the sweep and print it to stdout.

4.1 Line Formats
~~~~~~~~~~~~~~~~

These are the output formats for each line.

.. code:: ipython

    CSV_LINE = "{0},{1},{2},{3}"
    HUMAN_LINE = "{0}, Sweep[{1}]: Peak: {2:.3f} MHz\t{3} dBm"

4.2 The Function Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython

    def print_peak(rf_explorer, csv_data=False):
        """This function prints the amplitude and frequency peak of the latest received sweep

        Args:
         rfe_explorer (`RFExplorer.RFECommunicator`): communicator to get data from
         csv_data (bool): if True, print as CSV output
        """

4.3 Get The Data
~~~~~~~~~~~~~~~~

*This is part of the print\_peak function,* it gets the current data-count from ``RFExplorer.RFECommunicator.SweepData.Count``, decrements it to get the current index, then gets the data from ``RFExplorer.RFECommunicator.SweepData.GetData``.

.. code:: ipython

    index = rf_explorer.SweepData.Count - 1
    sweep_data = rf_explorer.SweepData.GetData(index)

The ``sweep_data`` is an instance of ``RFExplorer.RFESweepData.RFESweepData``.

4.4 Get The Peak Data
~~~~~~~~~~~~~~~~~~~~~

In this case we aren't printing all the data, just the peak.

4.4.1 The Index
^^^^^^^^^^^^^^^

First we get the index of the step that had the highest value in the sweep and store it in the ``peak_step`` variable

.. code:: ipython

    peak_step = sweep_data.GetPeakStep()

4.4.2 The Amplitude
^^^^^^^^^^^^^^^^^^^

Next, we use the index stored in ``peak_step`` to get the amplitude that was recorded for that step.

.. code:: ipython

    peak_amplitude = sweep_data.GetAmplitude_DBM(peak_step)

4.4.3 Peak Frequency
^^^^^^^^^^^^^^^^^^^^

Now we get the frequency represented by the step - the one that had the greatest amplitude.

.. code:: ipython

    peak_frequency = sweep_data.GetFrequencyMHZ(peak_step)

4.4.4 Output
^^^^^^^^^^^^

Finally, we combine the values and print them to the screen

.. code:: ipython

    line = CSV_LINE if csv_data else HUMAN_LINE

    print(line.format(datetime.now().strftime("%c"), index, peak_frequency,
                      peak_amplitude))
    return

5 Communicator Exception
------------------------

This is an error to raise if something goes wrong.

.. code:: ipython

    class CommunicatorException(Exception):
        """The Communicator should raise this if something bad happens"""

6 The Communicator
------------------

This is a class to hold the rfe-object to take care of some common actions.

.. code:: ipython

    class Communicator(object):
        """holds the communication object

        Args:
         serial_port (string|None): the name of the USB file
         baud_rate (int): the signaling rate for the serial connection
         settle_time (float): Seconds to wait after resetting
        """
        def __init__(self, serial_port=None, baud_rate=500000, settle_time=3):
            self.serial_port = serial_port
            self.baud_rate = baud_rate
            self.settle_time = settle_time
            self._rf_explorer = None
            return

6.1 The RFE Instance
~~~~~~~~~~~~~~~~~~~~

This is the ``RFExplorer.RFECommunicator`` instance.

.. code:: ipython

    @property
    def rf_explorer(self):
        """RFE Communicator

        Returns:
         :py:class:`RFExplorer.RFECommunicator`: the communicator
        """
        if self._rf_explorer is None:
            self._rf_explorer = RFExplorer.RFECommunicator()
        return self._rf_explorer

6.2 Context Management
~~~~~~~~~~~~~~~~~~~~~~

These are the methods that allow you to use this with a context manager. e.g. -

::

    with Communicator() as rfe:
        rfe.set_up()

When you leave the ``with`` statement it will close the RFECommunicator for you.

.. code:: ipython

    def __enter__(self):
        """returns this object"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return

    def __del__(self):
        """closes the RFECommunicator"""
        self.close()

    def close(self):
        """Closes the RFECommunicator
    
        Side-Effect:
         calls `RFExplorer.RFECommunicator.Close` and removes the instance
        """
        if self._rf_explorer is not None:
            self.rf_explorer.Close()
            self._rf_explorer = None
        return

6.3 The ``set_up`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~

This method runs the things that need to be done before doing a sweep of the spectrum.

.. code:: ipython

    def set_up(self):
        """Sets up the rf-explorer for scanning

        Raises:
         CommunicatorException: the setup failed
        """

6.3.1 Get the ports
^^^^^^^^^^^^^^^^^^^

The ``RFExplorer.RFECommunicator.GetConnectedPorts`` will gather what it thinks are possible ports that the RF-Explorer might be attached to. As a side-effect it will print the ports it found to stdout.

.. code:: ipython

    # get candidate serial ports and print out what you discovered
    self.rf_explorer.GetConnectedPorts()

6.3.2 Connect to the RFExplorer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``RFExplorer.RFECommunicator.ConnectPort`` will try to connect to the RFExplorer. If ``serial_port`` is ``None`` then it will try each candidate port in order. On my desktop this currently fails (I think because it tries ``/dev/ttyS4`` first) so I have to pass in ``/dev/ttyUSB0`` explicitly to make it work.

.. code:: ipython

    #Connect to available port
    if (not self.rf_explorer.ConnectPort(self.serial_port, self.baud_rate)):
        raise CommunicatorException("Unable to connect: port={}, baud={}".format(
            self.serial_port,
            self.baud_rate))

6.3.3 Reset The Device
^^^^^^^^^^^^^^^^^^^^^^

This sends the reboot command ("r") using ``RFExplorer.RFECommunicator.SendCommand``, then waits forever for the ``RFExplorer.RFECommunicator.IsResetEvent`` attribute to change to False. Once the device indicates that it is out of the reset-state it sleeps for three seconds to let things settle down.

.. code:: ipython

    print("Sending the Reset Command")
    self.rf_explorer.SendCommand("r")

    print("Waiting until the device resets")
    while(self.rf_explorer.IsResetEvent):
        pass

    print("Reset, sleeping for {} seconds to let the device settle".format(
        self.settle_time))
    time.sleep(self.settle_time)

6.3.4 The Model And Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the methods you want to use assume that the configuration has been set up. This loop makes the request to set it up and then waits forever for the model to be set (waits for ``RFExplorer.RFECommunicator.ActiveModel`` to not equal ``RFExplorer.RFE_Common.eModel.MODEL_NONE``). The ``RFExplorer`` has to be prompted to process the information that the thread is reading off the serial port so in between checking if the model is set it calls ``RFExplorer.RFECommunicator.ProcessReceivedString`` to tell it to do so. Once the model is set, we can assume that we're talking to the RF Explorer.

.. code:: ipython

    print("requesting the RF Explorer configuration")
    self.rf_explorer.SendCommand_RequestConfigData()

    print("Waiting for the model to not be None")
    while(self.rf_explorer.ActiveModel == RFExplorer.RFE_Common.eModel.MODEL_NONE):
        self.rf_explorer.ProcessReceivedString(True)

    print("Model is set")

6.3.5 Analyzer Check
^^^^^^^^^^^^^^^^^^^^

The ``RFExplorer`` can talk to both spectrum analyzers and signal generators, but this code will only work with the spectrum analyzer, so use the ``RFExplorer.RFECommunicator.IsAnalyzer`` method to make sure that's what this is

.. code:: ipython

    #If object is an analyzer, we can scan for received sweeps
    if (not self.rf_explorer.IsAnalyzer()):     
        raise CommunicatorError("Error: Device connected is a Signal Generator. "
                                "\nPlease, connect a Spectrum Analyzer")
    return

7 The Main processing loop
--------------------------

.. code:: ipython

    def main(arguments, communicator):
        """Runs the example

        Args:
         arguments (argparse.Namespace): object with the settings
         communicator (Communicator): object with the RFECommunicator
        """
        rf_explorer = communicator.rf_explorer
        try:

7.1 Setup the Communicator
~~~~~~~~~~~~~~~~~~~~~~~~~~

This tells the communicator to do the basic setup.

.. code:: ipython

    communicator.set_up()

7.2 Setup the Loop
~~~~~~~~~~~~~~~~~~

The loop will run continually until we run out of time. This sets up the time variables as well as a ``last_index`` variable that will make sure that we only print the value if it has been updated.

.. code:: ipython

    print("Receiving data...")
    #Process until we complete scan time
    last_index = 0
    start = datetime.now()
    total = timedelta(seconds=arguments.run_time)
    end = start + total

    if arguments.csv_data:
        print("index,frequency (MHz), amplitude (dBm)")
    while (datetime.now() < end):

7.3 Process String
~~~~~~~~~~~~~~~~~~

As before, the thread needs to be prompted to inspect the string it has pulled from the serial port.

.. code:: ipython

    #Process all received data from device 
    rf_explorer.ProcessReceivedString(True)

7.4 Print The Data
~~~~~~~~~~~~~~~~~~

This checks the ``RFExplorer.RFECommunicator.SweepData.Count`` to see if it is new data and then, if it is, calls the ``print_peak`` function (defined above) to print the data to the screen and then updates the ``last_index`` that we printed.

.. code:: ipython

    #Print data if received new sweep only
    if (rf_explorer.SweepData.Count > last_index):
        print_peak(rf_explorer, arguments.csv_data)
        last_index = rf_explorer.SweepData.Count          

7.5 End Main
~~~~~~~~~~~~

This is a leftover block to catch any exceptions that get raised.

.. code:: ipython

    except Exception as error:
        print("Error: {}".format(error))
    return

8 The Argument Parser
---------------------

This creates the parser for the command-line arguments. It doesn't parse the arguments because example-two uses it after adding more arguments.

.. code:: ipython

    def argument_parser():
        """Builds the argument parser
    
        Returns:
         ArgumentParser: object to parse the arguments
        """
        parser = argparse.ArgumentParser("RF Explorer Example One")

8.1 Serial Port
~~~~~~~~~~~~~~~

If the \`RFExplorer.RFECommunicator.ConnectPort\` isn't given a serial port it will try all the likely ports until it does or doesn't connect. If this doesn't work then pass in a specific port (e.g. ``/dev/ttyUSB0``).

.. code:: ipython

    parser.add_argument(
        "--serialport", type=str,
        default="/dev/ttyUSB0",
        help="Path to the serial-port file (e.g. '/dev/ttyUSB0') - Default=%(default)s")

8.2 Baud Rate
~~~~~~~~~~~~~

The baud-rate should be 500,000. Don't change it unless you know something changed.

.. code:: ipython

    parser.add_argument(
        "--baud-rate", type=int, default=500000,
        help="Baud-rate for the serial port (default=%(default)s)")

8.3 Run-Time
~~~~~~~~~~~~

This is the number of seconds to collect data before quitting.

.. code:: ipython

    parser.add_argument(
        "--run-time", type=int, default=10,
        help="Seconds to collect data (default=%(default)s)"
    )

8.4 CSV Data
~~~~~~~~~~~~

This tells the code to print a CSV format instead of the usual (human-readable) format.

.. code:: ipython

    parser.add_argument(
        "--csv-data", action="store_true",
        help="Output csv-formatted data",
    )

8.5 Return The parser
~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython

    return parser

9 The Executable Block
----------------------

.. code:: ipython

    if __name__ == "__main__":
        parser = argument_parser()
        arguments = parser.parse_args()

        with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
            main(arguments, communicator)

10 Sample output
----------------

10.1 Default
~~~~~~~~~~~~

This is an example of the default output.

**Warning:** you have to be a member of the ``dialout`` group to have access to the serial port (which you need to run this).

.. code:: ipython

    from example_1 import (
        argument_parser,
        main,
        Communicator,
        )
    parser = argument_parser()
    arguments = parser.parse_args(["--run-time", "3", "--serialport", "/dev/ttyUSB0"])
    with Communicator(arguments.serialport, arguments.baud_rate) as communicator:
        main(arguments, communicator)

::

    Detected COM ports:
      * /dev/ttyS0
      * /dev/ttyUSB0
    /dev/ttyS0 is a valid available port.
    /dev/ttyUSB0 is a valid available port.
    RF Explorer Valid Ports found: 2 - /dev/ttyS0 /dev/ttyUSB0 
    User COM port: /dev/ttyUSB0
    Connected: /dev/ttyUSB0, 500000 bauds
    Sending the Reset Command
    Waiting until the device resets
    Reset, sleeping for 3 seconds to let the device settle
    requesting the RF Explorer configuration
    Waiting for the model to not be None
    Received RF Explorer device model info:#C2-M:004,255,01.11
    New Freq range - buffer cleared.

    RF Explorer 23-Apr-13 01.04.05 01.11
    Model is set
    Receiving data...
    Sun Feb 18 18:00:15 2018, Sweep[3]: Peak: 2407.000 MHz	-55.5 dBm
    Received RF Explorer device model info:#C2-M:004,255,01.11
    Sun Feb 18 18:00:16 2018, Sweep[4]: Peak: 2465.750 MHz	-94.0 dBm
    Sun Feb 18 18:00:16 2018, Sweep[5]: Peak: 2445.125 MHz	-94.5 dBm
    Sun Feb 18 18:00:16 2018, Sweep[6]: Peak: 2455.125 MHz	-93.0 dBm
    Sun Feb 18 18:00:16 2018, Sweep[7]: Peak: 2458.875 MHz	-91.5 dBm
    Sun Feb 18 18:00:16 2018, Sweep[8]: Peak: 2470.125 MHz	-88.0 dBm
    Sun Feb 18 18:00:16 2018, Sweep[9]: Peak: 2402.000 MHz	-92.5 dBm
    Sun Feb 18 18:00:16 2018, Sweep[10]: Peak: 2463.875 MHz	-89.5 dBm
    Sun Feb 18 18:00:17 2018, Sweep[11]: Peak: 2463.250 MHz	-87.5 dBm
    Sun Feb 18 18:00:17 2018, Sweep[12]: Peak: 2463.250 MHz	-86.0 dBm
    Sun Feb 18 18:00:17 2018, Sweep[13]: Peak: 2463.250 MHz	-88.0 dBm
    Sun Feb 18 18:00:17 2018, Sweep[14]: Peak: 2461.375 MHz	-83.5 dBm
    Sun Feb 18 18:00:17 2018, Sweep[15]: Peak: 2460.750 MHz	-82.5 dBm
    Sun Feb 18 18:00:17 2018, Sweep[16]: Peak: 2460.750 MHz	-81.5 dBm
    Sun Feb 18 18:00:17 2018, Sweep[17]: Peak: 2460.125 MHz	-80.0 dBm
    Sun Feb 18 18:00:17 2018, Sweep[18]: Peak: 2458.250 MHz	-82.0 dBm
    Sun Feb 18 18:00:17 2018, Sweep[19]: Peak: 2458.875 MHz	-81.5 dBm
    Sun Feb 18 18:00:17 2018, Sweep[20]: Peak: 2467.625 MHz	-81.5 dBm
    Sun Feb 18 18:00:18 2018, Sweep[21]: Peak: 2468.875 MHz	-83.0 dBm
    Disconnected.

There are two things to notice:

1. There doesn't appear to have been much activity.

2. The three second cutoff didn't grab all the samples for the final second.

It looks like the three seconds is an absolute value, so even thought it shows 18:00:16 as the start, it probably started at some point within that second and ended at the start of the 18:00:18 second. So if you try and aggregate things into seconds , you'll have to take that into consideration - maybe trim off the ends.

10.2 CSV
~~~~~~~~

Here's the version where I try to create a comma-separated output.

.. code:: ipython

    arguments = parser.parse_args(["--run-time", "3", "--csv-data", "--serialport", "/dev/ttyUSB0"])
    with Communicator(arguments.serialport, arguments.baud_rate) as communicator:
        main(arguments, communicator)

::

    Detected COM ports:
      * /dev/ttyS0
      * /dev/ttyUSB0
    /dev/ttyS0 is a valid available port.
    /dev/ttyUSB0 is a valid available port.
    RF Explorer Valid Ports found: 2 - /dev/ttyS0 /dev/ttyUSB0 
    User COM port: /dev/ttyUSB0
    Connected: /dev/ttyUSB0, 500000 bauds
    Sending the Reset Command
    Waiting until the device resets
    Reset, sleeping for 3 seconds to let the device settle
    requesting the RF Explorer configuration
    Waiting for the model to not be None
    Received RF Explorer device model info:#C2-M:004,255,01.11
    New Freq range - buffer cleared.

    RF Explorer 23-Apr-13 01.04.05 01.11
    Model is set
    Receiving data...
    index,frequency (MHz), amplitude (dBm)
    Sun Feb 18 18:05:44 2018,2,2428.25,-94.5
    Received RF Explorer device model info:#C2-M:004,255,01.11
    Sun Feb 18 18:05:45 2018,3,2407.625,-93.5
    Sun Feb 18 18:05:45 2018,4,2418.25,-90.0
    Sun Feb 18 18:05:45 2018,5,2468.25,-81.0
    Sun Feb 18 18:05:45 2018,6,2467.625,-81.0
    Sun Feb 18 18:05:45 2018,7,2416.375,-86.0
    Sun Feb 18 18:05:46 2018,8,2415.75,-80.5
    Sun Feb 18 18:05:46 2018,9,2415.75,-79.0
    Sun Feb 18 18:05:46 2018,10,2415.75,-79.5
    Sun Feb 18 18:05:46 2018,11,2414.5,-79.5
    Sun Feb 18 18:05:46 2018,12,2413.875,-78.5
    Sun Feb 18 18:05:46 2018,13,2413.875,-79.0
    Sun Feb 18 18:05:46 2018,14,2415.125,-76.5
    Sun Feb 18 18:05:46 2018,15,2413.25,-75.5
    Sun Feb 18 18:05:46 2018,16,2413.25,-75.5
    Sun Feb 18 18:05:46 2018,17,2412.625,-76.5
    Sun Feb 18 18:05:47 2018,18,2412.625,-76.0
    Sun Feb 18 18:05:47 2018,19,2412.625,-74.0
    Sun Feb 18 18:05:47 2018,20,2410.75,-75.5
    Sun Feb 18 18:05:47 2018,21,2411.375,-77.0
    Sun Feb 18 18:05:47 2018,22,2410.125,-75.5
    Disconnected.

The values are a little higher, so maybe there was more going on.
