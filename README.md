# AXIOME_AX-18B_multimeter_python_script
Simple Python script to read data from AXIOME AX-18B multimeter
## Introduction
The purpose of this software is to be able to log data from the meter or meters connected to the computer's serial port using the Python language. The program is very simple and should be treated as a base for further expansion, in accordance with the individual project requirements.
A similar meter and method is described here:
https://alexkaltsas.wordpress.com/2013/04/19/python-script-to-read-data-from-va18b-multimeter/
## Description of operation
The program reads data from the serial port via an optical USB cable. Communication is one-way, multimeter -> computer, and it is not possible to change the meter's operating parameters from the computer.

The biggest problem turned out to be decoding the data sent by the meter. Since this may be a hint for the future, they may help you connect other meters of this type, I will try to describe the entire process in quite detail.
### Step 1 Connect multimeter and install Drivers
This step is quite simple for this particular meter the drivers are included on the board. The system uses the CH340 converter and it will be visible in the device manager under this name.
### Step 2 Get proper Boudrate
This step may be a bit difficult, you need to determine the speed at which data is exchanged. Theoretically, you can try to take apart the adapter and measure the signals with an oscilloscope or even measure the signal speed at the output of the IR diode of the meter. 
In my case, however, it turned out to be much simpler. It turned out that the PCLINK application attached to the meter, after pressing the Start key, displays the baud rate in the lower left corner
![AXIO](https://github.com/user-attachments/assets/d80d81f6-7395-471e-861d-c633600bd1d3 )

The device therefore operates at a speed of 2400
### Step 3 Listen to the protocol
Once we have determined the baud rate, we can run the serial port monitor, e.g. putty, set the appropriate parameters and try to read data from the port. 
#### Remember to turn on transmission on the meter, it is turned off by default. The operation of the transmission is signaled on the screen!
Then we set the meter to measure voltage and connect its measurement inputs. This way the meter will output a stable 0V reading. It is important that at this stage the meter constantly sends the same data.
In order to find the length of the frame sent by the meter, it is a good idea to set the data display method as single bits. And then determine the length of the repeating string.
For this meter, the frame is 14 bytes
### Step 4 Data conversion

Once we know the frame length, we can start decoding individual bits. 
Data in this meter is sent in such a way that each bit represents one segment on the display. 
As picture below.
![Display_Encoding](https://github.com/user-attachments/assets/662f0678-1f7e-40e4-8b05-bc535a702a80)

In order to decode individual halves, it is a good idea to use a laboratory power supply. We set the voltages one by one and compare the resulting strings on the terminal. It is important to read several strings and make sure that they are the same for a given voltage. Any fluctuations can make our work very difficult.

By comparing individual strings for given voltages, we can calculate a given pixel as the difference between the digits. For example, the middle pixel of the digit will be the difference between 8 and 0 
In the image below you can see an example of how to calculate individual fields. 
I entered the bit numbers that differ in square brackets. By taking measurements for each digit, we can determine the correct order.
![Segments_descryption](https://github.com/user-attachments/assets/fae94e3c-0417-4b5d-9e67-d9bd39471a7a)


## Connecting the device
### Configuration

### Conections


## Mistakes and ideas for the future
