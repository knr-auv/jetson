# File containing data parser class for TCM serial communication

from ast import Bytes
import imp
from select import select
from sys import byteorder
import struct

class TCMParser :

    # Dictionary for Okon TCM-board message types
    # For reference see TCM/Src/helpers/CommunicationProtocol/communication_protocol.h
    MSG_TYPE = {
        "MSG_OKON_REQUEST": 0x00,
        "MSG_OKON_SERVICE": 0x01,
        "MSG_OKON_STICKS": 0x02,
        "MSG_OKON_MODE": 0x03,
        "MSG_OKON_CL_STATUS": 0x04,
        "MSG_OKON_TYPE_COUNT": 0x05
    }


    # Default constructor
    def __init__(self) :
        print("Parser default constructor")


    # Method calculating CRC16 with given offset and lenght of the data
    # Returns checksum as an array of two bytes, firts is Most Significant Byte, second Last Significant Byte
    def calculateCheckSum(self, data : bytearray, offset, length) :

        if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data) :
            print("Invalid data, cannot calculate crc!")
            return 0

        crc16 = 0xFFFF

        for i in range(0, length):
            crc16 ^= data[offset + i] << 8

            for j in range(0,8):
                if (crc16 & 0x8000) > 0:
                    crc16 =(crc16 << 1) ^ 0x1021
                else:
                    crc16 = crc16 << 1

        crc16 = crc16 & 0xFFFF

        crc16_bytes = (crc16).to_bytes(2, byteorder='big')

        # For test purposes only
        # print(["0x%02x" % b for b in crc16_bytes])

        return crc16_bytes
    

    # Method parsing raw data to TCM compatible frame
    # Returns array of bytes which are ready to send
    # Input:
    # float_data - an array of floats to be converted
    # msg_type - string key for MSG_TYPE dictionary
    def parseData(self, float_data, msg_type) :

        floats_to_bytes = self.convertFloatsToBytes(float_data)

        if (floats_to_bytes == 0):
            print("Invalid bytes array, ending data parsing...")
            return 0

        data_length = (len(floats_to_bytes)).to_bytes(2, byteorder='big')

        length_MSB = data_length[0]
        length_LSB = data_length[1]

        parsed_data = bytearray()

        # Adding frame const header bytes
        parsed_data += bytes.fromhex('69')                            # Nice!
        parsed_data += bytes.fromhex('68')

        # Adding length bytes
        parsed_data += length_MSB.to_bytes(1, byteorder='big')
        parsed_data += length_LSB.to_bytes(1, byteorder='big')

        # Adding message type byte
        try:
            parsed_data += self.MSG_TYPE[msg_type].to_bytes(1, byteorder='big')
        except:
            print("Invalid message type, no i co ja mam tu wstawić???")
            return 0

        # Adding converted floats
        parsed_data += floats_to_bytes

        crc = self.calculateCheckSum(floats_to_bytes, 0, len(floats_to_bytes))

        # Adding checksum
        parsed_data += crc[0].to_bytes(1, byteorder='big')
        parsed_data += crc[1].to_bytes(1, byteorder='big')

        # For tests purposes only
        # print(["0x%02x" % b for b in parsed_data])

        return parsed_data


    # Method not implemented yet
    def compareCheckSum(self, recv_data) :
        print("Parser method")
        # calc_crc = self.calculateCheckSum(recv_data, 5, len(recv_data)-2)



    def convertFloatsToBytes(self, floats_array) :
        
        converted_floats = bytearray()

        if len(floats_array) == 0 :
            print("Empty array of floats, cannot convert to bytes!")
            return 0

        for float in floats_array:
            float_as_bytes = bytearray(struct.pack('f', float))
            converted_floats += float_as_bytes
        
        # For tests purposes only
        # print(["0x%02x" % b for b in converted_floats])

        return converted_floats