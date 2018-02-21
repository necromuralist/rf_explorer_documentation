==================================
Example Two - Frequency Sub-ranges
==================================

    :Author: hades

.. contents::

This is an example taken from the RFExplorer for python repository. It extends example one by looking at sub-ranges of the spectrum and reporting the maximum value for each sub-range.

It will display amplitude in dBm and frequency in MHz for the maximum amplitude in the frequency range. It uses three main arguments

- ``scan-start``: The frequency to start the scan

- ``scan-end``: The frequency to end the scan

- ``span-size``: The amount of frequencies to include in the current measurement.

It starts at the ``scan-start`` frequency, then finds the highest value for the frequencies within the span (i.e. ``scan-start``, to ``scan-start + span-size``). Then moves up past the last frequency it used and finds the highest value for the next span, etc.

The defaults set in the argument parser should have it find the peaks for channels 1, 6, and 11, omitting the 5 frequencies that they aren't supposed to overlap. 

Changing the settings incurs kind of a lot of overhead so it wouldn't be practical to actually do it like this, but this shows you how to select a sub-set of frequencies to query.

0.1 What's that then?
~~~~~~~~~~~~~~~~~~~~~

So, my explanation of the parameters was probably clear as mud. Let's look at a picture.

\.. mage:: wifi\_channels.svg
   :align: center

This is a diagram for the older standards - 802.11 n uses channels that are 20 MHz, but this will be useful for my explanation, I hope. 

Since each channel is 22MHz wide, you subtract 11 MHz from each center frequency to find its left value and add 11 MHZ to the center value to find its right value. So, since the center of channel 1 is at 2412 MHz, its leftmost edge is at 2401 MHz and its rightmost edge is at 2423 MHz. So, to sweep all of channel 1, your settings would be:

.. table::

    +----------------+-------+
    | Parameter      | Value |
    +================+=======+
    | ``scan-start`` |  2401 |
    +----------------+-------+
    | ``scan-end``   |  2423 |
    +----------------+-------+
    | ``span-size``  |    22 |
    +----------------+-------+

If you wanted to scan the entire 2.4 GHz spectrum, the ``scan-end`` would be 2473 MHz, and using the 11 MHz span-size would cause the RF-Explorer to checck three sub-ranges within the total 2.4 GHz band.

1 Channel Reference
-------------------

These are the frequency ranges for the main channels (2.4 GHz) for 8O2.11n.

.. table::

    +--------+-----------+-----------+------------+
    | \      | Channel 1 | Channel 6 | Channel 11 |
    +========+===========+===========+============+
    | Center |      2412 |      2437 |       2462 |
    +--------+-----------+-----------+------------+
    | Span   |        20 |        20 |         20 |
    +--------+-----------+-----------+------------+
    | Start  |      2402 |      2427 |       2452 |
    +--------+-----------+-----------+------------+
    | End    |      2422 |      2447 |       2472 |
    +--------+-----------+-----------+------------+

2 Imports
---------

.. code:: ipython

    # python standard library
    import time

    # from pypi
    import RFExplorer

    # this folder
    from example_1 import (
        Communicator,
        argument_parser,
        print_peak,
    )

3 Settings Checker
------------------

This function checks that the settings the user chose are reasonable and then sets them on the rf-explorer.

.. code:: ipython

    def check_settings(rf_explorer, arguments):
        """This functions check user settings

        If a value is out of bounds it sets the value to the limit allowed
    
        Args:
         rfe_explorer: RFECommunicator instance
         arguments: object with the maximum setting values

        Returns:
         tuple: span-size, start-frequency, stop-frequency
        """
        #print user settings
        print("User settings:\n"
              + "Start freq: {} MHz".format(arguments.scan_start)
              + " - "
              + "Stop freq: {} MHz".format(arguments.scan_stop))

        #Control maximum span size

        if(rf_explorer.MaxSpanMHZ <= arguments.span_size):
            print("Max Span size: {} MHz, Given {} MHz (aborting)".format(
                rf_explorer.MaxSpanMHZ,
                arguments.span_size
            ))
            return None, None, None
        if(rf_explorer.MinFreqMHZ > arguments.scan_start):
            print("Min Start freq: {} MHz, Given: {} MHz(aborting)".format(
                rf_explorer.MinFreqMHZ,
                arguments.scan_start))
            return None, None, None
        if(rf_explorer.MaxFreqMHZ < arguments.scan_stop):
            print("Max Start freq: {} MHz, Given: {} MHz (aborting)".format(
                rf_explorer.MaxFreqMHZ,
                arguments.scan_stop))
            return None, None, None

        rf_explorer.SpanMHZ = arguments.span_size
        rf_explorer.StartFrequencyMHZ = arguments.scan_start

        limit = rf_explorer.StartFrequencyMHZ + rf_explorer.SpanMHZ
        if(limit > arguments.scan_stop):
            print(("Max Stop freq (START_SCAN_MHZ "
                   "+ SPAN_SIZE_MHZ): {} MHz, Given: {}").format(
                       arguments.scan_stop,
                       limit))
            stop_frequency = None
        else:
            stop_frequency = limit
    
        return rf_explorer.SpanMHZ, rf_explorer.StartFrequencyMHZ, stop_frequency

4 Main Function
---------------

.. code:: ipython

    def main(arguments, communicator, clean=False):
        """Runs the example

        Args:
         arguments (:py:class:`argparse.Namespace`): thing with parameters
         communicator (``Communicator``): holder of the RFECommunicator
        """
        rf_explorer = communicator.rf_explorer
        try:
            communicator.set_up()
            #Control settings
            SpanSize, StartFreq, StopFreq = check_settings(rf_explorer, arguments)
            if(SpanSize and StartFreq and StopFreq):
                #set new frequency range
                print("Updating Device Configuration: {}, {}".format(StartFreq, StopFreq))
                rf_explorer.UpdateDeviceConfig(StartFreq, StopFreq)
                if clean:
                    rf_explorer.SweepData.CleanAll()
                print("updated")
                LastStartFreq = 0
                nInd = 0
                while (StopFreq<=arguments.scan_stop and StartFreq < StopFreq): 
                    #Process all received data from device 
                    print("Waiting for data")
                    while (rf_explorer.SweepData.Count < 1):
                        rf_explorer.ProcessReceivedString(True)
    
                    #Print data if received new sweep and a different start frequency 
                    if(StartFreq != LastStartFreq):
                        nInd += 1
                        print("Freq range[{}]: {} - {} MHz".format(nInd, StartFreq, StopFreq))
                        print_peak(rf_explorer)
                        LastFreqStart = StartFreq
    
                    #set new frequency range
                    StartFreq = min((StopFreq + arguments.offset, arguments.scan_stop))
                    StopFreq = StartFreq + SpanSize

                    #Maximum stop/start frequency control
                    if (StartFreq < StopFreq and StopFreq<=arguments.scan_stop):
                        print("Updating device config")
                        rf_explorer.UpdateDeviceConfig(StartFreq, StopFreq)
                        #Wait for new configuration to arrive (as it will clean up old sweep data)
                        sweep_data = None
                        print("Waiting for sweep_data update")
                        while ((sweep_data is None) or sweep_data.StartFrequencyMHZ != StartFreq):
                            if rf_explorer.SweepData.IsFull():
                                print("Sweep Data Collection is Full")
                            rf_explorer.ProcessReceivedString(True)
                            if (rf_explorer.SweepData.Count > 0):
                                sweep_data = rf_explorer.SweepData.GetData(rf_explorer.SweepData.Count-1)

        except Exception as error:
            print("Error: {}".format(error))
        return

5 Adding Arguments
------------------

This adds the arguments unique to this example. The span-size used is the maximum that the rf-explorer will allow.

.. code:: ipython

    def add_arguments(parser):
        """adds the extra command-line arguments

        Args:
         parser (:py:class:`argparse.ArgumentParser`)

        Returns:
         :py:class:`argparse.ArgumentParser`: parser with extra arguments
        """
        parser.add_argument(
            "--scan-start", default=2402, type=float,
            help="Frequency (MHz) to start the scan on (default=%(default)s)",
        ),
        parser.add_argument(
            "--scan-stop", default=2477, type=float,
            help="Frequency (MHz) to stop the scan on (default=%(default)s)"
        )
        parser.add_argument(
            "--span-size", default=20, type=float,
            help="Span of each measurement (default=%(default)s)")
        parser.add_argument(
            "--reset-time", default=3, type=float,
            help="Time to wait after sending the reset command (default=%(default)s)")
        parser.add_argument(
            "--offset", default=5, type=int,
            help="Amount to add to the last frequency in the range when finding the low-end for the next range (default=%(default)s)"
        )
        return parser

6 Running the Code
------------------

.. code:: ipython

    if __name__ == "__main__":
        parser = argument_parser()
        parser = add_arguments(parser)
        arguments = parser.parse_args()
        with Communicator(arguments.serialport,
                          arguments.baud_rate,
                          settle_time=arguments.reset_time) as communicator:
            main(arguments, communicator)

7 The Tangle
------------

.. code:: ipython

    <<imports>>

    <<check-settings>>

    <<main-function>>

    <<add-arguments>>

    <<executable-section>>

8 Sample Output
---------------

8.1 Trial 1
~~~~~~~~~~~

This will use the defaults to sweep all the channels for 4 seconds.

.. code:: ipython

    from example_1 import  (
        argument_parser,
        print_peak,
        Communicator,
    )
    from example_2 import (
        add_arguments,
        main,
        )

    def sample(clean=False):
        parser = argument_parser()
        parser = add_arguments(parser)
        arguments = parser.parse_args("--serialport /dev/ttyUSB0 --run-time 1 --reset-time 4".split())
        with Communicator(arguments.serialport,
                          arguments.baud_rate,
                          settle_time=arguments.reset_time) as communicator:
            main(arguments, communicator, clean)
    sample()

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
    Reset, sleeping for 4.0 seconds to let the device settle
    requesting the RF Explorer configuration
    Waiting for the model to not be None
    Received RF Explorer device model info:#C2-M:004,255,01.11
    New Freq range - buffer cleared.

    RF Explorer 23-Apr-13 01.04.05 01.11
    Model is set
    User settings:
    Start freq: 2402 MHz - Stop freq: 2477 MHz
    Updating Device Configuration: 2402, 2422
    updated
    Waiting for data
    Freq range[1]: 2402 - 2422 MHz
    Mon Feb 19 13:30:09 2018, Sweep[3]: Peak: 2405.214 MHz	-100.0 dBm
    Updating device config
    Waiting for sweep_data update
    Received RF Explorer device model info:#C2-M:004,255,01.11
    New Freq range - buffer cleared.
    New Freq range - buffer cleared.
    New Freq range - buffer cleared.
    Waiting for data
    Freq range[2]: 2427 - 2447 MHz
    Mon Feb 19 13:30:10 2018, Sweep[0]: Peak: 2433.071 MHz	-67.5 dBm
    Updating device config
    Waiting for sweep_data update
    New Freq range - buffer cleared.
    Waiting for data
    Freq range[3]: 2452 - 2472 MHz
    Mon Feb 19 13:30:10 2018, Sweep[1]: Peak: 2457.179 MHz	-98.5 dBm
    Disconnected.

At least one of the times when I ran this, the first peak was outside of the range that had been set.

::

    Freq range[1]: 2402 - 2422 MHz
    Mon Feb 19 13:20:26 2018, Sweep[3]: Peak: 2465.036 MHz	-92.5 dBm

To try and make this less likely, I added calling the ``RFExplorer.RFESweepDataCollection.CleanAll`` method. I don't know if that's really the fix, but it's something that has to be looked into.


.. code:: ipython

    sample(clean=True)

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
    Reset, sleeping for 4.0 seconds to let the device settle
    requesting the RF Explorer configuration
    Waiting for the model to not be None
    Received RF Explorer device model info:#C2-M:004,255,01.11
    New Freq range - buffer cleared.

    RF Explorer 23-Apr-13 01.04.05 01.11
    Model is set
    User settings:
    Start freq: 2402 MHz - Stop freq: 2477 MHz
    Updating Device Configuration: 2402, 2422
    updated
    Waiting for data
    Received RF Explorer device model info:#C2-M:004,255,01.11
    New Freq range - buffer cleared.
    New Freq range - buffer cleared.
    Freq range[1]: 2402 - 2422 MHz
    Mon Feb 19 13:30:45 2018, Sweep[0]: Peak: 2405.214 MHz	-99.5 dBm
    Updating device config
    Waiting for sweep_data update
    New Freq range - buffer cleared.
    Waiting for data
    Freq range[2]: 2427 - 2447 MHz
    Mon Feb 19 13:30:45 2018, Sweep[1]: Peak: 2428.786 MHz	-76.5 dBm
    Updating device config
    Waiting for sweep_data update
    New Freq range - buffer cleared.
    Waiting for data
    Freq range[3]: 2452 - 2472 MHz
    Mon Feb 19 13:30:46 2018, Sweep[2]: Peak: 2459.500 MHz	-101.0 dBm
    Disconnected.

The six lines we really care about here are:

::

    Freq range[1]: 2402 - 2422 MHz
    Mon Feb 19 13:30:45 2018, Sweep[0]: Peak: 2405.214 MHz	-99.5 dBm
    Freq range[2]: 2427 - 2447 MHz
    Mon Feb 19 13:30:45 2018, Sweep[1]: Peak: 2428.786 MHz	-76.5 dBm
    Freq range[3]: 2452 - 2472 MHz
    Mon Feb 19 13:30:46 2018, Sweep[2]: Peak: 2459.500 MHz	-101.0 dBm

Well, the three we really care about are the actual Peaks. It seems kind of suspicious to me that the peak value for channel 11 was -101 dBm (and channel 1 looks suspicious too). But this is an exploration, so we'll have to see how things progress.
