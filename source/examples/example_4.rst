========================
RF-Explorer Example Four
========================

.. contents::



1 Description
-------------

This is an extension of example three that tries to pull the values one at a time instead of using the :meth:`Dump <RFExplorer.RFESweepDataCollection.RFESweepDataCollection.Dump>` method.

2 Tangle
--------

.. code:: ipython

    <<imports>>

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

.. code:: ipython

    # python standard library
    import argparse
    import time
    from datetime import datetime, timedelta

    # from pypi
    import RFExplorer

    # this project
    from example_1 import Communicator

4 The Main processing loop
--------------------------

.. code:: ipython

    def main(arguments, communicator):
        """Runs the example

        Args:
         arguments (argparse.Namespace): object with the settings
         communicator (Communicator): object with the RFECommunicator
        """
        rf_explorer = communicator.rf_explorer

4.1 Setup the Communicator
~~~~~~~~~~~~~~~~~~~~~~~~~~

This tells the communicator to do the basic setup.

.. code:: ipython

    communicator.set_up()

4.2 Setup the Loop
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

4.3 Process String
~~~~~~~~~~~~~~~~~~

As before, the thread needs to be prompted to inspect the string it has pulled from the serial port (using :meth:`RFExplorer.RFECommunicator.ProcessReceivedString`).

.. code:: ipython

    #Process all received data from device 
    rf_explorer.ProcessReceivedString(True)

4.4 Print The Data
~~~~~~~~~~~~~~~~~~

This checks the :attr:`RFECommunicator.SweepData.Count <RFExplorer.RFESweepDataCollection.RFESweepDataCollection.Count>` to see if it is new data and then, if it is, prints the data to the screen and then updates the ``last_index`` that we printed. The data is taken from the :meth:`RFExplorer.RFESweepData.RFESweepData.GetAmplitudeDBM` method.

.. code:: ipython

    #Print data if received new sweep only
    if (rf_explorer.SweepData.Count > last_index):
        # print_peak(rf_explorer, arguments.csv_data)
        for index in range(rf_explorer.SweepData.Count):
            data = rf_explorer.SweepData.m_arrData[index]
            try:
                output = ','.join(("{:04.1f}".format(data.GetAmplitudeDBM(step, None, False))
                                                     for step in range(data.TotalSteps)))
                print("{},{}".format(data.m_Time, output))
            except TypeError as error:
                print(error)
                print("Index: {}".format(index))
                print("Data: {}".format(data))
                raise
        last_index = rf_explorer.SweepData.Count          

4.5 End Main
~~~~~~~~~~~~

This is a leftover block to catch any exceptions that get raised. Disabled for now because it catches too  much.

.. code:: ipython

    return

5 The Argument Parser
---------------------

This creates the parser for the command-line arguments. It doesn't parse the arguments because example-two uses it after adding more arguments.

.. code:: ipython

    def argument_parser():
        """Builds the argument parser
    
        Returns:
         ArgumentParser: object to parse the arguments
        """
        parser = argparse.ArgumentParser("RF Explorer Example One")

5.1 Serial Port
~~~~~~~~~~~~~~~

If the :meth:`RFExplorer.RFECommunicator.ConnectPort` isn't given a serial port it will try all the likely ports until it does or doesn't connect. If this doesn't work then pass in a specific port (e.g. ``/dev/ttyUSB0``).

.. code:: ipython

    parser.add_argument(
        "--serialport", type=str,
        help="Path to the serial-port file (e.g. '/dev/ttyUSB0') - Default=%(default)s")

5.2 Baud Rate
~~~~~~~~~~~~~

The baud-rate should be 500,000. Don't change it unless you know something changed.

.. code:: ipython

    parser.add_argument(
        "--baud-rate", type=int, default=500000,
        help="Baud-rate for the serial port (default=%(default)s)")

5.3 Run-Time
~~~~~~~~~~~~

This is the number of seconds to collect data before quitting.

.. code:: ipython

    parser.add_argument(
        "--run-time", type=int, default=10,
        help="Seconds to collect data (default=%(default)s)"
    )


5.5 Return The parser
~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython

    return parser

6 The Executable Block
----------------------

.. code:: ipython

    if __name__ == "__main__":
        parser = argument_parser()
        arguments = parser.parse_args()

        with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
            main(arguments, communicator)
