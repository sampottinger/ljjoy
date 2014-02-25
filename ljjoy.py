"""Microlibrary that makes a LabJack look like a vjoy virtual joystick device.

Microlibrary and command line interface that binds LabJack T7 registers to
vjoy virtual joystick output.

@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""
import sys
import time

import yaml

#from fsscript import joystick
from labjack import ljm

DEFAULT_MIN_DEVICE_VAL = 0
DEFAULT_MAX_DEVICE_VAL = 5
DEFAULT_OUTPUT_STRATEGY = 'binary'
CHANNEL_OUTPUT_NUM_NOT_INT_ERROR = 'Expected channel number. Got: %s'
USAGE_STR = 'USAGE: python ljjoy.py [path to configuration file]'

AVAILABLE_OUTPUT_STRATEGIES = {}


class InputMapping:
    """Info about a mapping from a LabJack register to joystick output."""
    
    def __init__ (self, device_register, joystick_output_channel):
        """Create a new mapping from a LabJack register to joystick output.

        @param device_register: The name or number of the register to bind.
        @type device_register: int or str
        @param joystick_output_channel: The joystick output to bind the register
            to. Should be of form (axis|button):\d+.
        @type joystick_output_channel: str
        """
        self.device_register = device_register
        joystick_channel_parts = joystick_output_channel.split(':')
        self.joystick_output_type = joystick_channel_parts[0]
        self.joystick_output_num = try_parse_int(
            joystick_channel_parts[1],
            CHANNEL_OUTPUT_NUM_NOT_INT_ERROR
        )

        self.output_strategy = BinaryOutputStrategy()

    def set_output_strategy(self, strategy):
        """Set the strategy to convert a device value to a joystick value.

        @param strategy: The conversion strategy to take a device value and
            provide a joystick value. Object must have process method that
            takes a single parameter: the value read from the device.
        @type strategy: Object
        """
        self.output_strategy = strategy

    def run_mapping(self, vjoy_device, device_value):
        """Set the joystick value given the device value for this mapping.

        @param vjoy_device: The virtual joystick device to update values for.
        @type vjoy_device: vjoy.vjoy
        @param device_value: The value read from the device.
        @type device_value: float, str, or int
        """
        output_value = self.output_strategy.process(device_value)
        if self.joystick_output_type == 'axis':
            vjoy_device.setAxis(self.joystick_output_num, output_value)
        else:
            vjoy_device.setButton(self.joystick_output_num, output_value)


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


class BinaryOutputStrategy:
    """Strategy that uses an activation threshold to ouput binary high / low.

    ScalingStrategy that uses a threshold to output a joystick value, outputting
    a high value if at or over a threshold and a low value if under the
    threshold.
    """

    def __init__(self, spec=None):
        """Create a new binary output strategy.

        @keyword spec: The information about the binary output strategy to
            build. May have activateThreshold (defaults to 0.5), inactiveValue
            (defaults to 0), and activeValue (defaults to 1)
        @type spec: dict
        """
        if not spec:
            spec = {}

        self.activate_threshold = spec.get('activateThreshold', 0.5)
        self.inactive_value = spec.get('inactiveValue', 0)
        self.active_value = spec.get('activeValue', 1)

    def process(self, device_value):
        """Scale the LabJack device value to the appropriate joystick value.

        @param device_val: The value read from the device.
        @type device_val: float
        @return: The scaled joystick output value.
        @rtype: float
        """
        if device_value >= self.activate_threshold:
            return self.active_value
        else:
            return self.inactive_value 

AVAILABLE_OUTPUT_STRATEGIES['binary'] = BinaryOutputStrategy


class LinearOutputStrategy:
    """ScalingStrategy that scales a LabJack value to a joystick value linearly.

    Strategy that uses a linear equation to scale a device read from a LabJack
    to a device for joystick output.
    """

    def __init__(self, spec):
        """Create a new linear output strategy.

        @param spec: Information about the linear output strategy to build.
            Should have attributes minDeviceVal (float), maxDeviceVal (float),
            minJoystickVal (float or int), and maxJoystickVal(float or int).
        @type spec: dict

        """
        require_spec_attr(spec, 'minDeviceVal')
        require_spec_attr(spec, 'maxDeviceVal')
        require_spec_attr(spec, 'minJoystickVal')
        require_spec_attr(spec, 'maxJoystickVal')

        min_device_val = spec['minDeviceVal']
        max_device_vals = spec['maxDeviceVal']
        min_joystick_val = spec['minJoystickVal']
        max_joystick_val = spec['maxJoystickVal']

        joystick_range = max_joystick_val - min_joystick_val
        device_range = max_device_vals - min_device_val
        slope = float(joystick_range) / device_range
        offset = -slope * min_device_val + min_joystick_val

        self.slope = slope
        self.offset = offset

    def process(self, device_val):
        """Scale the LabJack device value to the appropriate joystick value.

        @param device_val: The value read from the device.
        @type device_val: float
        @return: The scaled joystick output value.
        @rtype: float
        """
        return device_val * self.slope + self.offset

AVAILABLE_OUTPUT_STRATEGIES['linear'] = LinearOutputStrategy


class JoystickDecorator:

    def __init__(self, target):
        self.vals = {}

    def setAxis(self, joystick_output_num, output_value):
        key = 'axis:' + str(joystick_output_num)
        last_val = self.vals.get(key, None)
        if output_value != last_val:
            print "set axis %s to %f" % (joystick_output_num, output_value)
        self.vals[key] = output_value

    def setButton(self, joystick_output_num, output_value):
        key = 'button:' + str(joystick_output_num)
        last_val = self.vals.get(key, None)
        if output_value != last_val:
            print "set button %s to %f" % (joystick_output_num, output_value)
        self.vals[key] = output_value


def try_parse_int(target_value, error_template):
    """Attempt to parse an integer from a string.

    @param target_value: The value to convert to an integer.
    @type target_value: str
    @param error_template: The string template for the error message to display
        if the integer cannot be parsed.
    @type error_template: str
    """
    try:
        return int(target_value)
    except ValueError:
        raise ValueError(error_template % target_value)


def require_spec_attr(spec, name):
    """Ensure that a dictionary has a value.

    @param spec: The dictionary to check.
    @type spec: str
    @param name: The key to check for.
    @type name: str
    @raise ValueError: Raised if key (name) is not in the dictionary.
    """
    if not name in spec:
        raise ValueError(name + ' must be in mapping spec: ' + str(spec))


def create_mapping(mapping_spec):
    """Create a single InputMapping given a spec for that mapping.

    Creates a new single InputMapping given a spec for that mapping loaded from
    a YAML file or equivalent.

    @param mapping_spec: The specification that dictates how an InputMapping
        should be created.
    @type mapping_spec: dict
    @return: InputMapping made from provided specification.
    @rtype: dict
    """
    # Check all mapping specification attributes are present
    require_spec_attr(mapping_spec, 'outputStrategy')
    require_spec_attr(mapping_spec, 'deviceRegister')
    require_spec_attr(mapping_spec, 'joystickOutputChannel')

    # Create mapping with simple properties
    device_register = mapping_spec['deviceRegister']
    joystick_output_channel = mapping_spec['joystickOutputChannel']
    new_mapping = InputMapping(device_register, joystick_output_channel)
    
    # Add output strategy
    output_strategy_spec = mapping_spec['outputStrategy']
    strategy_name = output_strategy_spec['name']
    if not strategy_name in AVAILABLE_OUTPUT_STRATEGIES:
        raise ValueError(strategy_name + ' not a known output strategy.')
    else:
        strategy_class = AVAILABLE_OUTPUT_STRATEGIES[strategy_name]
        strategy = strategy_class(output_strategy_spec)
        new_mapping.output_strategy = strategy

    return new_mapping


def get_mappings_by_device_register(mappings):
    """Organize an iterable over InputMapping by device register.

    Organize an iterable collection of InputMappings into a dictionary by that
    mapping's device register.

    @param mappings: Collection of InputMappings to organize.
    @type mappings: iterable
    """
    ret_dict = {}
    for mapping in mappings:
        ret_dict[mapping.device_register] = mapping
    return ret_dict


def load_mappings(raw_input_map):
    """Load a mapping from a YAML specification file.

    @param raw_input_map: The register mappings as read from the YAML spec.
        Each mapping should have deviceRegister (str name of the device register
        to bind), joystickOutputChannel (str name of the joystick output to
        emulate), and outputStrategy.
    @type raw_input_map: dict
    @return: Mapping from device register to InputMapping for that device
        register.
    @rtype: dict
    """
    decorated_map = map(create_mapping, raw_input_map)
    return get_mappings_by_device_register(decorated_map)


def read_device_values(device, registers):
    """Read a set of values from the device.

    @param device: The device to read the values from.
    @type device: LJM handle
    @param registers: List of register names to read.
    @type registers: list of str
    @return: Mapping from register name to that register's value as read from
        the device.
    @rtype: dict (str to float)
    """
    ret_dict = {}
    values = ljm.eReadNames(device, len(registers), registers)
    return dict(zip(registers, values))


def run_mappings(device, mappings_by_device_register, vjoy_device):
    """Read from the device and execute those mappings.

    @param mappings_by_device_register: InputMapping by that mapping's device
        register whose target joystick values should be updated.
    @type mappings_by_device_register: dict
    @param vjoy_device: The virtual joystick device to update values for.
    @type vjoy_device: vjoy.vjoy
    """
    dev_registers = mappings_by_device_register.keys()
    values_by_register = read_device_values(device, dev_registers)
    for (register, value) in values_by_register.items():
        mapping = mappings_by_device_register[register]
        mapping.run_mapping(vjoy_device, value)


def load_labjack(device_spec):
    """Load labjack to bind to.

    @param device_spec: Information about the device to open. Should be dict
        with keys deviceType, connectionType, and identifier that correspond
        to the same parameters in the ljm open call.
    @type device_spec: dict
    @return: LabJack device that will be bound to.
    @rtype: LJM handle
    """
    return ljm.openS(
        device_spec['deviceType'],
        device_spec['connectionType'],
        device_spec['identifier']
    )


def load_vjoy(vjoy_spec):
    """Load the vjoy joystick for emulation.

    @param vjoy_spec: Information about the joystick that should be loaded.
        For most machines, this is simply the string name of the joystick.
    @type vjoy_spec: str or dict
    @return: Virtual joystick.
    @rtype: vjoy.vjoy
    """
    return JoystickDecorator(vjoy_spec)


def main(spec_loc):
    """Main script to run if python script invoked from CMD.

    @param spec_loc: The location of the YAML ItemMappings specification.
    @type spec_loc: str
    """

    with open(spec_loc) as f:
        raw_spec = yaml.load(f)

    require_spec_attr(raw_spec, 'mappings')
    require_spec_attr(raw_spec, 'labjack')
    require_spec_attr(raw_spec, 'joystick')

    mappings = load_mappings(raw_spec['mappings'])
    device = load_labjack(raw_spec['labjack'])
    vjoy_device = load_vjoy(raw_spec['joystick'])
    refresh_rate = raw_spec['labjack']['refreshRate']

    # Mainloop
    while True:
        start_time = time.time()
        run_mappings(device, mappings, vjoy_device)
        elapsed_time = time.time() - start_time
        time_to_sleep = (refresh_rate - elapsed_time) / 1000
        time.sleep(time_to_sleep)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print USAGE_STR
    else:
        main(sys.argv[1])
