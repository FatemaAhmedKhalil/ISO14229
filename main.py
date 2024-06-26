###############################################################################################
###############################################################################################
################################### Author: Fatema Ahmed ######################################
###################################### ISO14229 Script ########################################
####################################### Version: 1.00 #########################################
###############################################################################################
###############################################################################################

import serial
import struct
import sys
from IntelHexParser import Parsing

verbose_mode = 1
Memory_Write_Active = 0

MaxNumOfBlockLength = 4
dataFormatIdentifier               = 0x00
addressAndLengthFormatIdentifier   = 0x44

''' Services '''
DiagnosticSessionControlServices  = 0x10
ECUResetServices                  = 0x11
SecurityAccessServices            = 0x27
TesterPresentServices             = 0x3E
ReadDataByIdentifierServices      = 0x22
WriteDataByIdentifierServices     = 0x2E
RequestDownloadServices           = 0x34
TransferDataServices              = 0x36
RequestTransferExitServices       = 0x37

''' Sub Functions '''
defaultSession          = 0x01
ProgrammingSession      = 0x02
hardReset               = 0x01
requestSeedLevel01      = 0x01
sendKeyLevel01          = 0x02
zeroSubFunction         = 0x00

''' Negative Responses '''
serviceNotSupported 			    	 =  0x11
subfunctionNotSupported 		    	 =  0x12
incorrectMessageLengthOrInvalidFormat    =  0x13
responseTooLong					    	 =  0x14
conditionsNotCorrect			    	 =  0x22
requestSequenceError 			    	 =  0x24
requestOutOfRange				    	 =  0x31
securityAccessDenied 			    	 =  0x33
invalidKey						    	 =  0x35
exceededNumberOfAttempts		    	 =  0x36
requiredTimeDelayNotExpired 	    	 =  0x37
uploadDownloadNotAccepted 		    	 =  0x70
transferDataSuspended			    	 =  0x71
generalProgrammingFailure		    	 =  0x72
wrongBlockSequenceCounter 		    	 =  0x73
voltageTooHigh					    	 =  0x92
voltageTooLow					    	 =  0x93

''' Lengths'''
RequestDownloadLength          =   0x0B
TransferDataLength             =   0x06
TransferExitLength             =   0x01

def Check_Serial_Ports():
    Serial_Ports = []
    
    if sys.platform.startswith('win'):
        Ports = ['COM%s' % (i + 1) for i in range(256)]
    else:
        raise EnvironmentError("Error !! Unsupported Platform \n")
    
    for Serial_Port in Ports:
        try:
            test = serial.Serial(Serial_Port)
            test.close()
            Serial_Ports.append(Serial_Port)
        except (OSError, serial.SerialException):
            pass
    
    return Serial_Ports

def Serial_Port_Configuration(Port_Number):
    global Serial_Port_Obj
    try:
        Serial_Port_Obj = serial.Serial(Port_Number, 115200, timeout = 2)
    except:
        print("\nError !! That was not a valid port")
    
        Port_Number = Check_Serial_Ports()
        if(not Port_Number):
            print("\nError !! No ports Detected")
        else:
            print("\nHere are some available ports on your PC. Try Again !!")
            print("\n   ", Port_Number)
        return -1
    
    if Serial_Port_Obj.is_open:
        print("Port Open Success \n")
    else:
        print("Port Open Failed \n")

def Write_Data_To_Serial_Port(Value, Length):
    _data = struct.pack('>B', Value)
    if(verbose_mode):
        Value = bytearray(_data)
        # print("   "+"0x{:02x}".format(Value[0]), end = ' ')
        if(Memory_Write_Active and (not verbose_mode)):
            print("#", end = ' ')
        Serial_Port_Obj.write(_data)

def Read_Serial_Port(Data_Len):
    Serial_Value = Serial_Port_Obj.read(Data_Len)
    Serial_Value_len = len(Serial_Value)
    while Serial_Value_len <= 0:
        Serial_Value = Serial_Port_Obj.read(Data_Len)
        Serial_Value_len = len(Serial_Value)
        print("\n Waiting Replay from the Bootloader")
    return Serial_Value

def Diagnostic(RequestBuffer):
    ''' Send Data '''
    for byte in RequestBuffer:
        Write_Data_To_Serial_Port(byte, 1)  # Length in 1 byte
    
    ''' Receive Data '''
    ResponseLength = Read_Serial_Port(1)[0]  # Read the first byte to get the response length
    ResponseData = Read_Serial_Port(ResponseLength)  # Read the actual response data

    # Combine the response length and data into the response buffer
    ResponseBuffer = [ResponseLength]
    ResponseBuffer.extend(ResponseData)
    
    # Check if Read Data from ID FA12
    if (RequestBuffer[1] == ReadDataByIdentifierServices) and (RequestBuffer[2] == 0xFA) and (RequestBuffer[3] == 0x12):
        # Print the data in ASCII format
        print("ISO14229 Response :", end=" ")
        print(hex(ResponseBuffer[0]), end=" ")
        print(hex(ResponseBuffer[1]), end=" ")
        print(hex(ResponseBuffer[2]), end=" ")
        print(hex(ResponseBuffer[3]), end=" ")
        for byte in ResponseBuffer[4:]:
            print(chr(byte), end=" ")
        print()  # Print a newline
    else:
        PrintResponse(ResponseBuffer)

def FileTransfer(FileName):
    State, ParsedData = Parsing(FileName)
    if State == 0:
        for Index, Data in enumerate(ParsedData):
            print("\nRequest Download Processing... ")
            Write_Data_To_Serial_Port(RequestDownloadLength, 1) # Send Length
            Write_Data_To_Serial_Port(RequestDownloadServices, 1)
            Write_Data_To_Serial_Port(dataFormatIdentifier, 1)
            Write_Data_To_Serial_Port(addressAndLengthFormatIdentifier, 1)
            MemoryAddress = int(Data[0],16)
            Write_Data_To_Serial_Port((MemoryAddress>>24), 1)
            MemoryAddress = MemoryAddress << 8
            MemoryAddress = MemoryAddress & 0xFFFFFFFF
            Write_Data_To_Serial_Port((MemoryAddress>>24), 1)
            MemoryAddress = MemoryAddress << 8 
            MemoryAddress = MemoryAddress & 0xFFFFFFFF
            Write_Data_To_Serial_Port((MemoryAddress>>24), 1)
            MemoryAddress = MemoryAddress << 8
            MemoryAddress = MemoryAddress & 0xFFFFFFFF
            Write_Data_To_Serial_Port((MemoryAddress>>24), 1)

            MemoryLength = int(Data[1],16)
            Write_Data_To_Serial_Port((MemoryLength>>24), 1)
            MemoryLength = MemoryLength << 8
            MemoryLength = MemoryLength & 0xFFFFFFFF
            Write_Data_To_Serial_Port((MemoryLength>>24), 1)
            MemoryLength = MemoryLength << 8
            MemoryLength = MemoryLength & 0xFFFFFFFF
            Write_Data_To_Serial_Port((MemoryLength>>24), 1)
            MemoryLength = MemoryLength << 8
            MemoryLength = MemoryLength & 0xFFFFFFFF
            Write_Data_To_Serial_Port((MemoryLength>>24), 1)
            ''' Receive Data '''
            ResponseLength = Read_Serial_Port(1)[0]  # Read the first byte to get the response length
            ResponseData = Read_Serial_Port(ResponseLength)  # Read the actual response data
            # Combine the response length and data into the response buffer
            ResponseBuffer = [ResponseLength]
            ResponseBuffer.extend(ResponseData)

            if ResponseBuffer[1] == (RequestDownloadServices+0x40):
                print("\nTransfer Data Processing... ")
                TransferDataCounter = 1
                for Blocks in range(2,len(Data),MaxNumOfBlockLength):
                    Write_Data_To_Serial_Port(TransferDataLength, 1) # Send Length
                    Write_Data_To_Serial_Port(TransferDataServices, 1)
                    Write_Data_To_Serial_Port(TransferDataCounter, 1)
                    # Iterate over each element in the Data array and write it to the serial port
                    for byte in Data[Blocks:Blocks+MaxNumOfBlockLength]:
                        Write_Data_To_Serial_Port(int(byte,16), 1)
                    TransferDataCounter += 1
                    if TransferDataCounter > 0xFF:
                        TransferDataCounter = 0x00
                    ''' Receive Data '''
                    ResponseLength = Read_Serial_Port(1)[0]  # Read the first byte to get the response length
                    ResponseData = Read_Serial_Port(ResponseLength)  # Read the actual response data
                    # Combine the response length and data into the response buffer
                    ResponseBuffer = [ResponseLength]
                    ResponseBuffer.extend(ResponseData)
                    PrintResponse(ResponseBuffer)

            print("\nExit Transfer Data Processing... ")
            Write_Data_To_Serial_Port(TransferExitLength, 1) # Send Length
            Write_Data_To_Serial_Port(RequestTransferExitServices, 1)
            ''' Receive Data '''
            ResponseLength = Read_Serial_Port(1)[0]  # Read the first byte to get the response length
            ResponseData = Read_Serial_Port(ResponseLength)  # Read the actual response dat
            # Combine the response length and data into the response buffer
            ResponseBuffer = [ResponseLength]
            ResponseBuffer.extend(ResponseData)
            PrintResponse(ResponseBuffer)

def PrintResponse(ResponseBuffer):
    # Print the data in hexadecimal format
        print("ISO14229 Response:", end=" ")
        for byte in ResponseBuffer:
            print(hex(byte), end=" ")
        print()  # Print a newline

SerialPortName = input("Enter the Port Name of your device(Ex: COM9):")
Serial_Port_Configuration(SerialPortName)
 
while True:
    print("\nSTM32F401CCU6 ISO14229")
    print("==============================")
    print(" List of Supported Services  --> 1")
    print(" Transfer File Services      --> 2")

    inputData = int(input("Choose your Option: "))
    if inputData == 1:
        print("   DiagnosticSessionControlServices  --> 0x10")
        print("   ECUResetServices                  --> 0x11")
        print("   SecurityAccessServices            --> 0x27")
        print("   TesterPresentServices             --> 0x3E")
        print("   ReadDataByIdentifierServices      --> 0x22")
        print("   WriteDataByIdentifierServices     --> 0x2E")
        Data = input("\nEnter the Requst Formate (Length   Service   Subfunction(if have)  RemaningRequest(if have):\n")
        Bytes = Data.split() # Split the input string into individual bytes
        RequestBuffer = [int(byte, 16)for byte in Bytes] # Convert to integers
        Diagnostic(RequestBuffer)

    elif inputData == 2:
        print("   RequestDownloadServices          --> 0x34")
        print("   TransferDataServices             --> 0x36")
        print("   RequestTransferExitServices      --> 0x37")
        FileName = input("Enter the FileName: ")
        FileTransfer(FileName)
    
    input("\nPlease press any key to continue ...")
    Serial_Port_Obj.reset_input_buffer()