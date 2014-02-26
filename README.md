LabJack as a Joystick
=====================
**ljjoy microlibrary: Use a [LabJack](http://labjack.com) anywhere you would use a joystick.**

<br>
What is this?
-------------
Need a data acquisition or automation device to pretend to be a joystick? ljjoy lets you route any value on your [LabJack T7 measurement and automation device](http://labjack.com/t7) to virtual joystick output. For example, Use analog inputs as joystick axes or digital inputs as joystick buttons. With different scaling mechanisms and easy extendability, this micro-library let's you use a LabJack anywhere you would use a joystick. Games, commercial applications, expensive in-house stuff, hobby? Get ljjoy!

<br>
Author and License
------------------
Patches and extensions welcome! Please see the ["Develop and Extend"](https://github.com/Samnsparky/ljjoy#develop-and-extend-ljjoy) section.  

Released under the [GNU GPL v3](https://www.gnu.org/copyleft/gpl.html).  
Lead developer / contact: [Sam Pottinger](http://gleap.org).  
(c) 2014, [LabJack Corp.](http://labjack.com).  

<br>
Limitations
-----------
Even the best of us have our limits:

 - ljjoy currently only supports Windows XP and up.
 - Currently only the T7 is supported.

Sorry *nix / mac users and UD device owners, star the project and ping us in the issue tracker to let us know you are out there.

<br>
Installation
------------
We want a self-contained executable just as much as you do. However, until then, there are a few moving parts...

 - Download and install [Python](http://python.org/download/releases/2.7.6/).
 - Download and install [LJM Python module](http://labjack.com/support/ljm/examples/python).
 - Download and install [PyYAML](http://pyyaml.org/wiki/PyYAML).
 - Download and install [vjoy](http://vjoystick.sourceforge.net/site/index.php/download-a-install/72-download).
 - Run the vjoy device setup and configure which axes and buttons you want your joystick to have.
 - Download and extract ljjoy from our [GitHub repo](https://github.com/Samnsparky/ljjoy).

We are trying to guage our user base and interest. If you want a self-contained executable, star the project to let us know you are out there!

<br>
Running ljjoy
-------------
```python ljjoy.py ./examples/one_axis_one_button.yaml```  

Just execute Python on ljjoy and provide 1 command line argument: the path to the YAML configuration file (see [example](https://github.com/Samnsparky/ljjoy#example-configuration) and [API section](https://github.com/Samnsparky/ljjoy#api-reference) below).

<br>
Example configuration
---------------------
The following example configuration file

 - Opens a LabJack T7 over USB with the serial number 123456789.
 - Links the value of digital input FIO0 to joystick button 4.
 - Reports analog input AIN0 (from 0V to 10V) as joystick x axis position.
 - Reads from the device and updates ever 10 milliseconds.

```
mappings:
  - deviceRegister: AIN0
    joystickOutputChannel: axis:0
    outputStrategy:
      name: linear
      minDeviceVal: 0
      maxDeviceVal: 10
  - deviceRegister: FIO0
    joystickOutputChannel: button:4
    outputStrategy:
      name: binary
labjack:
  deviceType: T7
  connectionType: USB
  identifier: '123456789'
  refreshRate: 10
joystick:
  name: vJoy Device
  debug: yes
```  

<br>
API Reference
-------------
It's but a [YAML configuration file](http://www.yaml.org/). Check out our examples folder for a super-speedy start. Otherwise, for the whole API...

**Structure**
```
mappings:
  ...
labjack:
  ...
joystick:
  ...
```  

 - The **mappings** indicate which values from the LabJack should be routed as joystick input.
 - The **labjack** section indicates which device to use to get joystick values.
 - The **joystick** section indicates which joystick to pretend to be.

<br>
**mappings**  
```
mappings:
  - deviceRegister: AIN0
    joystickOutputChannel: axis:0
    outputStrategy:
      name: linear
      minDeviceVal: 0
      maxDeviceVal: 11
      minJoystickVal: 1
      maxJoystickVal: 32767
  - deviceRegister: FIO0
    joystickOutputChannel: button:4
    outputStrategy:
      name: binary
      activateThreshold: 0.5
```   
Mappings indicate which values ljjoy read from the LabJack device and how the virtual joystick should then report those values.

 - **deviceRegister** indicates which device value ljjoy should read.
 - **joystickOuputChannel** indicates where ljjoy should use the specified device value in the virutal joystick. Expects ```(axis|button)[\d+]``` or, in other words, "axis" or "button" followed by a colon and then the axis or button number. See the [axis map](https://github.com/Samnsparky/ljjoy#axes-index) section for more info.
 - **outputStrategy** tells ljjoy how to convert the device reading to joystick output. See the [scaling strategies](https://github.com/Samnsparky/ljjoy#scaling-strategies) section for more info.

<br>
**labjack**
```
labjack:
  deviceType: T7
  connectionType: USB
  identifier: '470010610'
  refreshRate: 10
```  
The labjack section indicates which LabJack device ljjoy should use.

 - **deviceType** indicates what type of LabJack device ljjoy should open. Currently the only valid option is T7.
 - **connectionType** tells ljjoy through which connection medium to open the device. Valid options include ALL, USB, ETHERNET, and WIFI.
 - **identifier** identifies the target device for ljjoy to use if more than one LabJack is available. Can be the device's serial number or, if connecting over the network, IP address (XXX.XXX.X.X). Can also pass ANY for opening the first found device over the specified connection type.
 - **refreshRate** indicates how frequently ljjoy should query the device for new values. The 10 in the above example tells ljjoy to query the device and update joystick output every 10 milliseconds.

<br>
**joystick**
```
joystick:
  name: vJoy Device
  debug: yes
```  
The joystick section tell ljjoy which joystick to manipulate. 

 - **name** indicates the system-level name of the joystick to control (vJoy Device should be used if unsure).
 - **debug** indicates the verbosity level. ljjoy will print joystick values to the terminal if yes and will remain quiet if no.

<br>
Scaling strategies
------------------
Scaling strategies indicate how ljjoy should convert values read from a LabJack to values reported by the virtual joystick.

**Linear Scaling**  
``` 
outputStrategy:
  name: linear
  minDeviceVal: 0
  maxDeviceVal: 5
  minJoystickVal: 0
  maxJoystickVal: 100
```  
Using ```name:linear```, ljjoy will create a linear equation to convert LabJack to joystick values. A device reading of 1 in the above example would output 20 to the virtual joystick.

 - **minDeviceVal** tells ljjoy the lowest value to expect from the device.
 - **maxDeviceVal** tells ljjoy the highest value to expect from the device.
 - **minJoystickVal** tells ljjoy the minimum value 
 to report to the virtual joystick. Optional, defaults to 1.
 - **maxJoystickVal** tells ljjoy the maximum value to report to the virtual joystick. Optional, defaults to 32767.

**Choosing min and max joystick values:** most axes and joystick configurations range from 1 (low) to 32767 (high).

<br>
**Binary Scaling**
```
outputStrategy:
  name: binary
  activateThreshold: 0.5
  inactiveValue: 0
  activeValue: 1
```  
With ```name: binary```, ljjoy will report an "active" value if a device reading meets or exceeds a certain threshold and will output an "inactive" value otherwise. This is frequently used with buttons. A value of 0.1 in the above example would report button off and a value of 0.7 would, for example, report an button being pressed.

 - **activeThreshold** tells ljjoy the minimum device value that should be reported before outputing the activeValue. Optional, defaults to 0.5.
 - **inactiveValue** tells ljjoy what value to report to the virtual joystick when the device value falls under under the activeThreshold. Optional, defaults to 0.
 - **inactiveValue** tells ljjoy what value to report to the virtual joystick when the device reading equals or execeeds the activeThreshold. Optional, defaults to 1.

<br>
Axes Index
----------  
We lifted our axes list right out of [vjoy](http://vjoystick.sourceforge.net/).

<table>
<thead>
    <tr>
        <th>ljjoy ID</th>
        <th>Human Axis Name</th>
        <th>Axis vjoy ID</th>
    </tr>
</thead>
<tbody>
    <tr>
        <td>0</td> <td>wAxisX</td> <td>0x30</td>
    </tr>
    <tr>
        <td>1</td> <td>wAxisY</td> <td>0x31</td>
    </tr>
    <tr>
        <td>2</td> <td>wAxisZ</td> <td>0x32</td>
    </tr>
    <tr>
        <td>3</td> <td>wAxisXRot</td> <td>0x33</td>
    </tr>
    <tr>
        <td>4</td> <td>wAxisYRot</td> <td>0x34</td>
    </tr>
    <tr>
        <td>5</td> <td>wAxisZRot</td> <td>0x35</td>
    </tr>
    <tr>
        <td>6</td> <td>wSlider</td> <td>0x36</td>
    </tr>
    <tr>
        <td>7</td> <td>wDial</td> <td>0x37</td>
    </tr>
    <tr>
        <td>8</td> <td>wWheel</td> <td>0x38</td>
    </tr>
</tbody>
</table>

<br>
Develop and Extend ljjoy
------------------------
Patches, feature requests, and bug reports are welcome!

**Running automated tests**  
Run tests:
```python test_ljjoy.py```

**Adding scaling strategies**  
All scaling strategies must implement the following ScalingStrategy interface.
```
class ScalingStrategy:
    """Semi-non-pythonic interface for LabJack to joystick device scaling.

    Somewhat non-pythonic interface for stratgies to scale a LabJack device
    value to a value to send to the joystick emulator.
    """

    def process(self):
        """Scale the LabJack device value to the appropriate joystick value.

        @param device_val: The value read from the device.
        @type device_val: float
        @return: The scaled joystick output value.
        @rtype: float
        """
        raise NotImplementedError
```  
To then add your strategy to ljjoy, add ```AVAILABLE_OUTPUT_STRATEGIES['name'] = YourScalingStrategy``` at the end of your class definition.

**Everything else**  
Engage us here on GitHub with the issue tracker. We do ask that patches please unit test when reasonable and follow the [epydoc docstring convention](http://epydoc.sourceforge.net/).
