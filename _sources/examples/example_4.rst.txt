==================================================================
RF-Explorer Example Four - Whole spectrum, without ``Dump`` method
==================================================================

    :Author: brunhilde

.. contents::



1 Description
-------------

This is an extension of example three that tries to pull the values one at a time instead of using the ``Dump`` method before printing to the screen. This is probably the preferred way to do it, since it doesn't get all the extra artifacts.

2 Tangle
--------

.. code:: python

    <<imports>>

    <<main>>
    <<setup-communicator>>
    <<setup-loop>>
    <<process-string>>
    <<print-data>>
    <<end-main>>

    <<executable-block>>
        <<cleanup>>

3 Imports
---------

.. code:: python

    # python standard library
    import argparse
    import time
    from datetime import datetime, timedelta

    # from pypi
    import RFExplorer

    # this project
    from example_1 import (
        argument_parser,
        Communicator,
        )

4 The Main processing loop
--------------------------

.. code:: python

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

.. code:: python

    communicator.set_up()

4.2 Setup the Loop
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

4.3 Process String
~~~~~~~~~~~~~~~~~~

As before, the thread needs to be prompted to inspect the string it has pulled from the serial port.

.. code:: python

    #Process all received data from device 
    rf_explorer.ProcessReceivedString(True)

4.4 Print The Data
~~~~~~~~~~~~~~~~~~

This checks the ``RFExplorer.RFECommunicator.SweepData.Count`` to see if it is new data and then, if it is, calls the ``print_peak`` function (defined above) to print the data to the screen and then updates the ``last_index`` that we printed.

.. code:: python

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

.. code:: python

    return

5 The Executable Block
----------------------

.. code:: python

    if __name__ == "__main__":
        parser = argument_parser()
        arguments = parser.parse_args()

        with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
            main(arguments, communicator)
