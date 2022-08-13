from __future__ import print_function
from TCMParser import TCMParser

Parser = TCMParser()

data = [10.5, 11.5, 5.0, 0.778]

parsed_data = Parser.parseData(data, "MSG_OKON_STICKS")

print(["0x%02x" % b for b in parsed_data])

