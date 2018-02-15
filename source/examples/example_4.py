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
            for index in range(rf_explorer.SweepData.Count):
                data = rf_explorer.SweepData.GetData(index)
                try:
                    output = ','.join(("{:04.1f}".format(data.GetAmplitudeDBM(step, None, False))
                                                         for step in range(data.TotalSteps)))
                    print("{},{}".format(data.CaptureTime, output))
                except TypeError as error:
                    print(error)
                    print("Index: {}".format(index))
                    print("Data: {}".format(data))
                    raise
            last_index = rf_explorer.SweepData.Count          
    return

if __name__ == "__main__":
    parser = argument_parser()
    arguments = parser.parse_args()

    with Communicator(arguments.serialport, arguments.baud_rate) as communicator:        
        main(arguments, communicator)
