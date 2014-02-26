ljjoy is LabJack as a Joystick
============================
Use a [LabJack](http://labjack.com) anywhere you would use a joystick.

<br>
Motivation
----------
Need a data acquisition or automation device to pretend to be a joystick? ljjoy lets you route any value on your [LabJack T7 measurement and automation device](http://labjack.com/t7) to virtual joystick output. With different scaling mechanisms and easy extendability, this micro-library let's you use a LabJack anywhere you would use a joystick. Use analog inputs as joystick axes or digital inputs as joystick buttons. Games, commercial applications, expensive in-house stuff, hobby? Get ljjoy!

<br>
Limitations
-----------
Even the best of us have our limits:

 - ljjoy currently only supports Windows XP and up.
 - Currently only the T7 is supported.

Sorry *nix / mac users and UD device owners, star the project and let us know in the issue tracker to let us know you are out there.

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

We are trying to guage our user base and interest. If you are out there and want a self-contained executable, star the project to let us know you are out there!

<br>
Configuration
-------------
Ain't nothin' but a [YAML configuration file](http://www.yaml.org/). Check out our examples folder for a super-speedy start. Otherwise...

<br>
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
Mappings indicate which values should be read from the LabJack device and how those values should be used in the virtual joystick.

 - **deviceRegister** indicates which value from the device should be read.
 - **joystickOuputChannel** indicates where ljjoy should use the specified device value in the virutal joystick. Should be either axis or button followed by a colon and then the axis number. See the axis map section for more info.
 - **outputStrategy** tells ljjoy how to convert the device value to the joystick value. See the output strategies section for more info.

<br>
**labjack**
```
labjack:
  deviceType: T7
  connectionType: USB
  identifier: '470010610'
  refreshRate: 10
```  
The labjack section indicates which LabJack device ljjoy should use. This device's values will be used in creating the values for the virtual joystick.

 - **deviceType** indicates what type of LabJack device ljjoy should open. Currently the only valid option is T7.
 - **connectionType** tells ljjoy which connection medium to open the device through. Valid options include ALL, USB, ETHERNET, and WIFI.
 - **identifier** tells ljjoy which device serial number or, if connecting over the nextwork, IP address (XXX.XXX.X.X) to look for. Can also pass ANY for opening the first found device over the specified connection type.
 - **refreshRate** indicates how frequently ljjoy should query the device for new values. The 10 in the above example tells ljjoy to query the device very 10 milliseconds.

<br>
**joystick**
```
joystick:
  name: vJoy Device
  debug: yes
```  
The joystick section indicates which joystick should be used by ljjoy. The **name** attribute indicates the system-level name of the joystick to control (vJoy Device should be used if unsure). ljjoy will print joystick values to the terminal if **debug** is yes and will remain quiet if debug is no.

<br>
Running ljjoy
-------------
```python ljjoy.py ./examples/one_axis_one_button.yaml```  
Just execute Python on ljjoy and provide 1 command line argument: the path to your YAML configuration file.

<br>
Scaling strategies
------------------
Scaling strategies indicate how ljjoy should convert values read from a LabJack to values reported by the virtual joystick.

<br>
**Linear Scaling**  
``` 
outputStrategy:
  name: linear
  minDeviceVal: 0
  maxDeviceVal: 5
  minJoystickVal: 0
  maxJoystickVal: 2147483647
```  
ljjoy, given a minimum / maximum expected device value and a minimum / maximum joystick value, creates a linear equation to scale device to joystick values.

 - **minDeviceVal** tells ljjoy the lowest value to expect from the device.
 - **maxDeviceVal** tells ljjoy the highest value to expect from the device.
 - **minJoystickVal** tells ljjoy the minimum value 
 to report to the virtual joystick.
 - **maxJoystickVal** tells ljjoy the maximum value to report to the virtual joystick.

<br>
**Binary Scaling**
```
outputStrategy:
  name: binary
  activateThreshold: 0.5
  inactiveValue: 0
  activeValue: 1
```  
ljjoy will report inactive if the value read from the device is below a threshold and ljjoy will report active if the value read from the device is above that threshold.

 - **activeThreshold** tells ljjoy the minimum device value that should be reported before outputing the activeValue.
 - **inactiveValue** tells ljjoy what value to report to the virtual joystick when the device value falls under under the activeThreshold.
 - **inactiveValue** tells ljjoy what value to report to the virtual joystick when the device value equals or execeeds the activeThreshold.

<br>
Axes Index
----------  
We lifted our axes list right out of [vjoy](http://vjoystick.sourceforge.net/).

<table>
<thead>
    <tr>
        <th>ljjoy Index</th>
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