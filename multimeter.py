import signal
import sys
import time
import serial
import io
import getopt

class Multimeter:
    def __init__(self, interface, model, baudrate=2400):
        self.interface = interface
        self.baudrate = baudrate
        self.model = model
        self.port = None

    def get_description(self):
        return f"Com port '{self.interface}', baudrate {self.baudrate}, model name {self.model}."

    def connect(self):
        try:
            self.port = serial.Serial(
                self.interface,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE,
                timeout=5.0
            )
            if not self.port.isOpen():
                self.port.open()
        except IOError:
            print("No COM connected")
            sys.exit(1)

    def get_bytes(self):
        try:
            # Every packet is 14 bytes long.
            substr = ''
            for _ in range(15):
                byte = self.port.read(1)
                if not byte:
                    raise IOError("Failed to read byte from serial port.")
                # converting every byte to binary format keeping the low nibble.
                substr += '{0:08b}'.format(ord(byte))[4:]
            return substr
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            if self.port:
                self.port.flushInput()
                self.port.close()
            sys.exit(0)
            return None

    def signal_handler(self, signal, frame):
        sys.stderr.write('\n\nYou pressed Ctrl+C!\n\n')
        if self.port:
            self.port.flushInput()
            self.port.close()
        sys.exit(0)

    def match_pattern(self,input_string):
        # Define the pattern dictionary
        pattern_dict = {
            "1111011": "0",
            "0001010": "1",
            "1011101": "2",
            "1001111": "3",
            "0101110": "4",
            "1100111": "5",
            "1110111": "6",
            "1001010": "7",
            "1111111": "8",
            "1101111": "9",
            "0110001":"L",
            "1110101":"E",
            "1000101":"F",
            "0000100": "-",
            "0000000": ""
        }
        # Match the input string with the pattern dictionary
        if input_string in pattern_dict:
            return pattern_dict[input_string]
        else:
            return ""

    def stream_decode_new(self,substr):
        # Extract flags and dot positions
        auto, dc, ac, minus = int(substr[1]), int(substr[2]), int(substr[3]), int(substr[7])
        dot1, dot2, dot3 = int(substr[15]), int(substr[23]), int(substr[31])

        # Extract digits using list comprehensions
        digit_positions = [
            [4, 5, 6, 8, 9, 10, 11],
            [12, 13, 14, 16, 17, 18, 19],
            [20, 21, 22, 24, 25, 26, 27],
            [28, 29, 30, 32, 33, 34, 35]
        ]
        digits = [''.join(substr[pos] for pos in positions) for positions in digit_positions]

        # Extract additional symbols
        symbols = {
            'micro': int(substr[39]), 'cap': int(substr[47]), 'nano': int(substr[38]),
            'diotst': int(substr[36]), 'lowbat': int(substr[48]), 'kilo': int(substr[37]),
            'mili': int(substr[43]), 'percent': int(substr[42]), 'mega': int(substr[41]),
            'contst': int(substr[40]), 'ohm': int(substr[46]), 'rel': int(substr[45]),
            'hold': int(substr[44]), 'amp': int(substr[51]), 'volts': int(substr[50]),
            'hertz': int(substr[49]), 'ncv': int(substr[52]), 'fahrenh': int(substr[55]),
            'celcius': int(substr[54])
        }

        # Construct the value string
        value = ("-" if minus else "") + \
                str(self.match_pattern(digits[0])) + ("." if dot1 else "") + \
                str(self.match_pattern(digits[1])) + ("." if dot2 else "") + \
                str(self.match_pattern(digits[2])) + ("." if dot3 else "") + \
                str(self.match_pattern(digits[3]))

        # Construct flags and units strings
        flags = " ".join([name for name, present in {
            "AC": ac, "DC": dc, "Auto": auto, "Diode test": symbols['diotst'],
            "Conti test": symbols['contst'], "Capacity": symbols['cap'], "Rel": symbols['rel'],
            "Hold": symbols['hold'], "ncv": symbols['ncv'], "LowBat": symbols['lowbat']
        }.items() if present])

        units = "".join([symbol for symbol, present in {
            "n": symbols['nano'], "u": symbols['micro'], "k": symbols['kilo'],
            "m": symbols['mili'], "M": symbols['mega'], "%": symbols['percent'],
            "Ohm": symbols['ohm'], "Amp": symbols['amp'], "Volt": symbols['volts'],
            "Hz": symbols['hertz'], "F": symbols['fahrenh'], "C": symbols['celcius']
        }.items() if present])

        return value + " " + flags + " " + units
    

if __name__ == "__main__":
    meter1 = Multimeter("COM38", "AX-18B")
    meter1.connect()

    # Set up the signal handler
    signal.signal(signal.SIGINT, meter1.signal_handler)
    
    try:
        while True:
            result = meter1.get_bytes()
            print(meter1.stream_decode_new(result))


    except KeyboardInterrupt:
        meter1.signal_handler(None, None)

