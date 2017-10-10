# python standard library
import argparse
import time
from datetime import datetime, timedelta

# from pypi
import RFExplorer

# this project
from example_1 import Communicator

def main(arguments, communicator):
    """Runs the example

    Args:
     arguments (argparse.Namespace): object with the settings
     communicator (Communicator): object with the RFECommunicator
    """
    rf_explorer = communicator.rf_explorer
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
