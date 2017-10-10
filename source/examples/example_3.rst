=========================
RF-Explorer Example Three
=========================

.. contents::



1 Description
-------------

This is a variation on example one that dumps the entire spectrum instead of just the peak.

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

    <<executable-block>>

3 Imports
---------

.. code:: ipython

    # python standard library
    from datetime import datetime, timedelta

    # from this package
    from example_1 import (
        argument_parser,
        Communicator,
        )

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
        try:

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

As before, the thread needs to be prompted to inspect the string it has pulled from the serial port.

.. code:: ipython

    #Process all received data from device 
    rf_explorer.ProcessReceivedString(True)

4.4 Print The Data
~~~~~~~~~~~~~~~~~~

This checks the :attr:`SweepData.Count <RFExplorer.RFESweepDataCollection.RFESweepDataCollection.Count>` to see if it is new data and then, if it is, :meth:`Dumps <RFExplorer.RFESweepDataCollection.RFESweepDataCollection.Dump>` the data to the screen . This is the only part that differs from example 1.

.. code:: ipython

    #Print data if received new sweep only
    if (rf_explorer.SweepData.Count > last_index):
        print(rf_explorer.SweepData.Dump())
        last_index = rf_explorer.SweepData.Count          

4.5 End Main
~~~~~~~~~~~~

This is a leftover block to catch any exceptions that get raised.

.. code:: ipython

    except Exception as error:
        print("Error: ".format(error))
    return

5 The Executable Block
----------------------

.. code:: ipython

    if __name__ == "__main__":
        parser = argument_parser()
        arguments = parser.parse_args()

        with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
            main(arguments, communicator)
