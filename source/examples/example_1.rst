=======================
RF-Explorer Example One
=======================

.. contents::
   :depth: 2

1 Description
-------------

This is the first example that comes with the ``RFExplorer`` repository.
It will display the amplitude (in dBm) and the frequency (in MHz) of the frequency that had the highest amplitude in the sweep data. It runs until the amount of time allocated runs out.

2 Imports
---------

.. code:: python

    # python standard library
    import argparse
    import time
    from datetime import datetime, timedelta

    # from pypi
    import RFExplorer

3 Print Peak
------------

This is a helper function to get only the peak data from the sweep and print it to stdout.

3.1 Line Formats
~~~~~~~~~~~~~~~~

These are the output formats for each line.

.. code:: python

    CSV_LINE = "{0},{1},{2}"
    HUMAN_LINE = "Sweep[{0}]: Peak: {1:.3f} MHz\t{2} dBm"

.. code:: python

    def print_peak(rf_explorer, csv_data=False):
        """This function prints the amplitude and frequency peak of the latest received sweep

        Args:
         rfe_explorer (:py:class:`RFExplorer.RFECommunicator`): communicator to get data from
         csv_data (bool): if True, print as CSV output
        """

3.2 Get The Data
~~~~~~~~~~~~~~~~

This gets the current data-count from :py:attr:`RFExplorer.RFESweepDataCollection.RFESweepDataCollection.Count`, decrements it to get the current index, then gets the data from :py:meth:`RFExplorer.RFESweepDataCollection.RFESweepDataCollection.GetData`.

.. code:: python

    index = rf_explorer.SweepData.Count - 1
    sweep_data = rf_explorer.SweepData.GetData(index)

The ``sweep_data`` is an instance of :py:class:`RFExplorer.RFESweepData.RFESweepData`.

3.3 Get The Peak Data
~~~~~~~~~~~~~~~~~~~~~

In this case we aren't printing all the spectrum data, just the one with the highest amplitude.

 * :py:meth:`RFExplorer.RFESweepData.RFESweepData.GetPeakStep`
 * :py:meth:`RFExplorer.RFESweepData.RFESweepData.GetAmplitude_DBM`
 * :py:meth:`RFExplorer.RFESweepData.RFESweepData.GetFrequencyMHZ`

.. code:: python

    peak_step = sweep_data.GetPeakStep()      #Get index of the peak
    peak_amplitude = sweep_data.GetAmplitude_DBM(peak_step)    #Get amplitude of the peak
    peak_frequency = sweep_data.GetFrequencyMHZ(peak_step)   #Get frequency of the peak

    line = CSV_LINE if csv_data else HUMAN_LINE

    print(line.format(index, peak_frequency, peak_amplitude)) 
    return

4 Communicator Exception
------------------------

This is an error to raise if something goes wrong.

.. code:: python

    class CommunicatorException(Exception):
        """The Communicator should raise this if something bad happens"""

5 The Communicator
------------------


This is a class to hold the :py:class:`RFExplorer.RFECommunicator` object to make it easier to remember to close it (use :py3:ref:`with`).

.. code:: python

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

5.1 The RFE Instance
~~~~~~~~~~~~~~~~~~~~

This is the :py:class:`RFExplorer.RFECommunicator` instance.

.. code:: python

    @property
    def rf_explorer(self):
        """RFE Communicator

        Returns:
         :py:class:`RFExplorer.RFECommunicator`: the communicator
        """
        if self._rf_explorer is None:
            self._rf_explorer = RFExplorer.RFECommunicator()
        return self._rf_explorer

5.2 Context Management
~~~~~~~~~~~~~~~~~~~~~~

These are the methods that allow you to use this with a context manager.

.. code:: 

    with Communicator() as rfe:
        rfe.set_up()

When you leave :py3:ref:`with` it will close the RFECommunicator for you.

.. code:: python

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

5.3 The ``set_up`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~

This method runs the things that need to be done before doing a sweep of the spectrum.

.. code:: python

    def set_up(self):
        """Sets up the rf-explorer for scanning

        Raises:
         CommunicatorException: the setup failed
        """

5.4 Get the ports
~~~~~~~~~~~~~~~~~

The :py:meth:`RFExplorer.RFECommunicator.GetConnectedPorts` method will gather what it thinks are possible ports that the RF-Explorer might be attached to. As a side-effect it will print the ports it found to stdout.

.. code:: python

    # get candidate serial ports and print out what you discovered
    self.rf_explorer.GetConnectedPorts()

5.5 Connect to the RFExplorer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :py:meth:`RFExplorer.RFECommunicator.ConnectPort` will try to connect to the RFExplorer. If ``serial_port`` is ``None`` then it will try each candidate port in order. On my desktop this currently fails (I think because it tries ``/dev/ttyS4`` first) so I have to pass in ``/dev/ttyUSB0`` explicitly to make it work.

.. code:: python

    #Connect to available port
    if (not self.rf_explorer.ConnectPort(self.serial_port, self.baud_rate)):
        raise CommunicatorException("Unable to connect: port={}, baud={}".format(
            self.serial_port,
            self.baud_rate))

5.6 Reset The Device
~~~~~~~~~~~~~~~~~~~~

This sends the reset command ("r") using :py:meth:`RFExplorer.RFECommunicator.SendCommand`, then waits forever for the :py:attr:`RFExplorer.RFECommunicator.IsResetEvent` attribute to change to False. Once the device indicates that it is out of the reset-state it sleeps for three seconds to let things settle down.

.. code:: python

    print("Sending the Reset Command")
    self.rf_explorer.SendCommand("r")

    print("Waiting until the device resets")
    while(self.rf_explorer.IsResetEvent):
        pass

    print("Reset, sleeping for {} seconds to let the device settle".format(
        self.settle_time))
    time.sleep(self.settle_time)

5.7 The Model And Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of the methods you want to use assume that the configuration has been set up. This loop makes the request to set it up and then waits forever for the model to be set (waits for :py:attr:`RFExplorer.RFECommunicator.ActiveModel` to not equal :py:obj:`RFExplorer.RFE_Common.eModel.MODEL_NONE`). The ``RFExplorer`` has to be prompted to process the information that the thread is reading off the serial port so in between checking if the model is set it calls :py:meth:`RFExplorer.RFECommunicator.ProcessReceivedString` to tell it to do so (passing in ``True`` tells it to process all the strings it has, not just one).

.. code:: python

    print("requesting the RF Explorer configuration")
    self.rf_explorer.SendCommand_RequestConfigData()

    print("Waiting for the model to not be None")
    while(self.rf_explorer.ActiveModel == RFExplorer.RFE_Common.eModel.MODEL_NONE):
        self.rf_explorer.ProcessReceivedString(True)

    print("Model is set")

5.8 Analyzer Check
~~~~~~~~~~~~~~~~~~

The ``RFExplorer`` can talk to both spectrum analyzers and signal generators, but this code will only work with the spectrum analyzer, so use the :py:meth:`RFExplorer.RFECommunicator.IsAnalyzer` method to make sure that's what this is.

.. code:: python

    #If object is an analyzer, we can scan for received sweeps
    if (not self.rf_explorer.IsAnalyzer()):     
        raise CommunicatorError("Error: Device connected is a Signal Generator. "
                                "\nPlease, connect a Spectrum Analyzer")
    return

6 The Main processing loop
--------------------------

.. code:: python

    def main(arguments, communicator):
        """Runs the example

        Args:
         arguments (argparse.Namespace): object with the settings
         communicator (Communicator): object with the RFECommunicator
        """
        rf_explorer = communicator.rf_explorer
        try:

6.1 Setup the Communicator
~~~~~~~~~~~~~~~~~~~~~~~~~~

This tells the communicator to do the basic setup.

.. code:: python

    communicator.set_up()

6.2 Setup the Loop
~~~~~~~~~~~~~~~~~~

The loop will run continually until we run out of time. This sets up the time variables as well as a ``last_index`` variable that will make sure that we only print the value if it has been updated.

.. code:: python

    print("Receiving data...")
    #Process until we complete scan time
    last_index = 0
    start = datetime.now()
    total = timedelta(seconds=arguments.run_time)
    end = start + total

    if arguments.csv_data:
        print("index,frequency (MHz), amplitude (dBm)")
    while (datetime.now() < end):

6.3 Process String
~~~~~~~~~~~~~~~~~~

As before, the thread needs to be prompted to inspect the string it has pulled from the serial port.

.. code:: python

    #Process all received data from device 
    rf_explorer.ProcessReceivedString(True)

6.4 Print The Data
~~~~~~~~~~~~~~~~~~

This checks the :py:attr:`SweepData <RFExplorer.RFESweepDataCollection.RFESweepDataCollection.Count>` to see if it is new data and then, if it is, calls the ``print_peak`` function (defined above) to print the data to the screen, and then updates the ``last_index`` that we printed.

.. code:: python

    #Print data if received new sweep only
    if (rf_explorer.SweepData.Count > last_index):
        PrintPeak(rf_explorer, arguments.csv_data)
        last_index = rf_explorer.SweepData.Count          

6.5 End Main
~~~~~~~~~~~~

This is a leftover block to catch any exceptions that get raised.

.. code:: python

    except Exception as error:
        print("Error: ".format(error))
    return

7 The Argument Parser
---------------------

This creates the command-line interface for the example using :py:class:`argparse <argparse.ArgumentParser>`.

.. code:: python

    def parse_arguments():
        """Builds the argument parser
    
        Returns:
        ArgumentParser: object to parse the arguments
        """
        parser = argparse.ArgumentParser("RF Explorer Example One")

7.1 Serial Port
~~~~~~~~~~~~~~~

If the :py:meth:`RFExplorer.RFECommunicator.ConnectPort` isn't given a serial port it will try all the likely ports until it does or doesn't connect. If this doesn't work then pass in a specific port (e.g. ``/dev/ttyUSB0``).

.. code:: python

    parser.add_argument(
        "--serialport", type=str,
        help="Path to the serial-port file (e.g. '/dev/ttyUSB0') - Default=%(default)s")

7.2 Baud Rate
~~~~~~~~~~~~~

The baud-rate should be 500,000, but if it's not, then you can change it here.

.. code:: python

    parser.add_argument(
        "--baud-rate", type=int, default=500000,
        help="Baud-rate for the serial port (default=%(default)s)")

7.3 Run-Time
~~~~~~~~~~~~

This is the number of seconds to collect data before quitting.

.. code:: python

    parser.add_argument(
        "--run-time", type=int, default=10,
        help="Seconds to collect data (default=%(default)s)"
    )

7.4 CSV Data
~~~~~~~~~~~~

This tells the code to print a CSV format instead of the usual (human-readable) format.

.. code:: python

    parser.add_argument(
        "--csv-data", action="store_true",
        help="Output csv-formatted data",
    )

7.5 Return The Parser
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    return parse

8 The Executable Block
----------------------

This puts the calling of the code into a block so that things can be imported to other files if needed.

.. code:: python

    if __name__ == "__main__":
        parser = argument_parser()
        arguments = parser.parse_args()

        with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
            main(arguments, communicator)
