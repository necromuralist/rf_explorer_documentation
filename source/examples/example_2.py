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
          + "Span: {} MHz".format(arguments.span_size)
          +  " - "
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

def main(arguments, communicator):
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
                StartFreq = min((StopFreq, arguments.scan_stop))
                StopFreq = StartFreq + SpanSize
    
                #Maximum stop/start frequency control
                if (StartFreq < StopFreq):
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

def add_arguments(parser):
    """adds the extra command-line arguments

    Args:
     parser (:py:class:`argparse.ArgumentParser`)

    Returns:
     :py:class:`argparse.ArgumentParser`: parser with extra arguments
    """
    parser.add_argument(
        "--span-size", default=84, type=float,
        help="Maximum value for MaxSpanSize (default=%(default)s)"),
    parser.add_argument(
        "--scan-start", default=2350, type=float,
        help="Frequency (MHz) to start the scan on (default=%(default)s)",
    ),
    parser.add_argument(
        "--scan-stop", default=2434, type=float,
        help="Frequency (MHz) to stop the scan on (default=%(default)s)"
    )
    return parser

if __name__ == "__main__":
    parser = argument_parser()
    parser = add_arguments(parser)
    arguments = parser.parse_args()
    with Communicator(arguments.serialport, arguments.baud_rate) as communicator:
        main(arguments, communicator)
