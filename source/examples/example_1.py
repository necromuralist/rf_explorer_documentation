# python standard library
import argparse
import time
from datetime import datetime, timedelta

# from pypi
import RFExplorer

CSV_LINE = "{0},{1},{2}"
HUMAN_LINE = "Sweep[{0}]: Peak: {1:.3f} MHz\t{2} dBm"

def PrintPeak(rf_explorer, csv_data=False):
    """This function prints the amplitude and frequency peak of the latest received sweep

    Args:
     rfe_explorer (`RFExplorer.RFECommunicator`): communicator to get data from
     csv_data (bool): if True, print as CSV output
    """
    index = rf_explorer.SweepData.Count - 1
    sweep_data = rf_explorer.SweepData.GetData(index)
    peak_step = sweep_data.GetPeakStep()      #Get index of the peak
    peak_amplitude = sweep_data.GetAmplitude_DBM(peak_step)    #Get amplitude of the peak
    peak_frequency = sweep_data.GetFrequencyMHZ(peak_step)   #Get frequency of the peak
    
    line = CSV_LINE if csv_data else HUMAN_LINE
    
    print(line.format(index, peak_frequency, peak_amplitude)) 
    return


class Communicator(object):
    """holds the communication object
    """
    def __init__(self):
        self._rfe = None
        return

    @property
    def rfe(self):
        """RFE Communicator
        Returns:
         :py:class:`RFExplorer.RFECommunicator`: the communicator
        """
        if self._rfe is None:
            self._rfe = RFExplorer.RFECommunicator()
        return self._rfe

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
         calls `RFExplorer.RFECommunicator.Close`
        """
        if self._rfe is not None:
            self.rfe.Close()
            self._rfe = None
        return

def main(arguments, communicator):
    """Runs the example

    Args:
     arguments (argparse.Namespace): object with the settings
     communicator (Communicator): object with the RFECommunicator
    """
    rf_explorer = communicator.rfe
    try:
        # get candidate serial ports and print out what you discovered
        rf_explorer.GetConnectedPorts()

        #Connect to available port
        if (not rf_explorer.ConnectPort(arguments.serialport, arguments.baud_rate)):
            print("Not Connected")
            return

        #Reset the unit to start fresh
        print("sending the Reset Command")
        rf_explorer.SendCommand("r")
        
        #Wait for unit to notify reset completed
        print("Waiting until the device resets")
        while(rf_explorer.IsResetEvent):
            pass
        
        #Wait for unit to stabilize
        print("Reset, sleeping for 3 seconds")
        time.sleep(3)

        #Request RF Explorer configuration
        print("requesting the configuration data")
        rf_explorer.SendCommand_RequestConfigData()
        #Wait to receive configuration and model details
        print("Waiting for the model to not be None")
        while(rf_explorer.ActiveModel == RFExplorer.RFE_Common.eModel.MODEL_NONE):
            rf_explorer.ProcessReceivedString(True)    #Process the received configuration
        
        print("Model is set")

        #If object is an analyzer, we can scan for received sweeps
        if (not rf_explorer.IsAnalyzer()):     
            print("Error: Device connected is a Signal Generator. "
                  "\nPlease, connect a Spectrum Analyzer")
            return

        print("Receiving data...")
        #Process until we complete scan time
        last_index = 0
        start = datetime.now()
        total = timedelta(seconds=arguments.run_time)
        end = start + total
        
        if arguments.csv_data:
            print("index,frequency (MHz), amplitude (dBm)")
        while (datetime.now() < end):
            #Process all received data from device 
            rf_explorer.ProcessReceivedString(True)
            #Print data if received new sweep only
            if (rf_explorer.SweepData.Count > last_index):
                PrintPeak(rf_explorer, arguments.csv_data)
                last_index = rf_explorer.SweepData.Count          
    except Exception as obEx:
        print("Error: " + str(obEx))
    return

def parse_arguments():
    parser = argparse.ArgumentParser("RF Explorer Example One")
    parser.add_argument(
        "--serialport", type=str,
        help="Path to the serial-port file (e.g. '/dev/ttyUSB0') - Default=%(default)s")
    parser.add_argument(
        "--baud-rate", type=int, default=500000,
        help="Baud-rate for the serial port (default=%(default)s)")
    parser.add_argument(
        "--run-time", type=int, default=10,
        help="Seconds to collect data (default=%(default)s)"
    )
    parser.add_argument(
        "--csv-data", action="store_true",
        help="Output csv-formatted data",
    )
    return parser.parse_args()

if __name__ == "__main__":
    arguments = parse_arguments()
    with Communicator() as communicator:        
        main(arguments, communicator)
