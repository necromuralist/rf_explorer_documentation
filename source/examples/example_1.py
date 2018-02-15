# python standard library
import argparse
import time
from datetime import datetime, timedelta

# from pypi
import RFExplorer

CSV_LINE = "{0},{1},{2},{3}"
HUMAN_LINE = "{0}, Sweep[{1}]: Peak: {2:.3f} MHz\t{3} dBm"

def print_peak(rf_explorer, csv_data=False):
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
    
    print(line.format(datetime.now().strftime("%c"), index, peak_frequency,
                      peak_amplitude))
    return



class CommunicatorException(Exception):
    """The Communicator should raise this if something bad happens"""

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

    @property
    def rf_explorer(self):
        """RFE Communicator
    
        Returns:
         :py:class:`RFExplorer.RFECommunicator`: the communicator
        """
        if self._rf_explorer is None:
            self._rf_explorer = RFExplorer.RFECommunicator()
        return self._rf_explorer
    
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

    def set_up(self):
        """Sets up the rf-explorer for scanning
    
        Raises:
         CommunicatorException: the setup failed
        """
        # get candidate serial ports and print out what you discovered
        self.rf_explorer.GetConnectedPorts()

        #Connect to available port
        if (not self.rf_explorer.ConnectPort(self.serial_port, self.baud_rate)):
            raise CommunicatorException("Unable to connect: port={}, baud={}".format(
                self.serial_port,
                self.baud_rate))

        print("Sending the Reset Command")
        self.rf_explorer.SendCommand("r")
        
        print("Waiting until the device resets")
        while(self.rf_explorer.IsResetEvent):
            pass
        
        print("Reset, sleeping for {} seconds to let the device settle".format(
            self.settle_time))
        time.sleep(self.settle_time)

        print("requesting the RF Explorer configuration")
        self.rf_explorer.SendCommand_RequestConfigData()
        
        print("Waiting for the model to not be None")
        while(self.rf_explorer.ActiveModel == RFExplorer.RFE_Common.eModel.MODEL_NONE):
            self.rf_explorer.ProcessReceivedString(True)
        
        print("Model is set")

        #If object is an analyzer, we can scan for received sweeps
        if (not self.rf_explorer.IsAnalyzer()):     
            raise CommunicatorError("Error: Device connected is a Signal Generator. "
                                    "\nPlease, connect a Spectrum Analyzer")
        return

def main(arguments, communicator):
    """Runs the example

    Args:
     arguments (argparse.Namespace): object with the settings
     communicator (Communicator): object with the RFECommunicator
    """
    rf_explorer = communicator.rf_explorer
    try:
        communicator.set_up()
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
                print_peak(rf_explorer, arguments.csv_data)
                last_index = rf_explorer.SweepData.Count          
    except Exception as error:
        print("Error: {}".format(error))
    return

def argument_parser():
    """Builds the argument parser
    
    Returns:
     ArgumentParser: object to parse the arguments
    """
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
    return parser

if __name__ == "__main__":
    parser = argument_parser()
    arguments = parser.parse_args()

    with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
        main(arguments, communicator)
