import smbus

#bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

DEVICE_ADDRESS = 0x38     #7 bit address (will be left shifted to add the read write bit)

RELAY8_INPORT_REG_ADD = 0x00
RELAY8_OUTPORT_REG_ADD = 0x01
RELAY8_POLINV_REG_ADD = 0x02
RELAY8_CFG_REG_ADD = 0x03

relayMaskRemap = [0x01, 0x04, 0x02, 0x08, 0x40, 0x10, 0x20, 0x80] 
relayChRemap = [0, 2, 1, 3, 6, 4, 5, 7]


def relayToIO(relay):
	val = 0
	for i in range(0, 8):
		if (relay & (1 << i)) != 0:
			val = val + relayMaskRemap[i]
	return val
  
def IOToRelay(iov):
	val = 0
	for i in range(0, 8):
		if (iov & relayMaskRemap[i]) != 0:
			val = val + (1<< i)
	return val

def check(bus, add):
	cfg = bus.read_byte_data(add, RELAY8_CFG_REG_ADD)
	if(cfg != 0):
		bus.write_byte_data(add, RELAY8_CFG_REG_ADD, 0)
		bus.write_byte_data(add, RELAY8_OUTPORT_REG_ADD, 0)
	return bus.read_byte_data(add, RELAY8_INPORT_REG_ADD)


def set(stack, relay, value):
	bus = smbus.SMBus(1)
	if stack < 0 or stack > 7:
		raise ValueError('Invalid stack level')
  
	stack = 0x07 ^ stack;
	if relay < 1:
		raise ValueError('Invalid relay number')
	if relay > 8:
		raise ValueError('Invalid relay number')
	oldVal = check(bus, DEVICE_ADDRESS + stack)
	oldVal = IOToRelay(oldVal)
	if value == 0:
		oldVal = oldVal & (~(1 << (relay - 1)))
		oldVal = relayToIO(oldVal)
		bus.write_byte_data(DEVICE_ADDRESS + stack, RELAY8_OUTPORT_REG_ADD, oldVal)
	else:
		oldVal = oldVal | (1 << (relay - 1))
		oldVal = relayToIO(oldVal)
		bus.write_byte_data(DEVICE_ADDRESS + stack, RELAY8_OUTPORT_REG_ADD, oldVal)
	bus.close()

		
def set_all(stack, value):
	bus = smbus.SMBus(1)
	if stack < 0 or stack > 7:
		raise ValueError('Invalid stack level')
	stack = 0x07 ^ stack  
	if value > 255 :
		raise ValueError('Invalid relay value')
	if value < 0:
		raise ValueError('Invalid relay value')
	oldVal = check(bus, DEVICE_ADDRESS + stack)	
	value = relayToIO(value)
	bus.write_byte_data(DEVICE_ADDRESS + stack, RELAY8_OUTPORT_REG_ADD, value)
	bus.close()


	
def get(stack, relay):
	bus = smbus.SMBus(1)
	if stack < 0 or stack > 7:
		raise ValueError('Invalid stack level')
	stack = 0x07 ^ stack  
	if relay < 1:
		raise ValueError('Invalid relay number')
	if relay > 8:
		raise ValueError('Invalid relay number')
	val = check(bus, DEVICE_ADDRESS + stack)
	val = IOToRelay(val) 
	val = val & (1 << (relay - 1))
	bus.close()
	if val == 0:
		return 0
	else:
		return 1
		
		
	
def get_all(stack):
	bus = smbus.SMBus(1)
	if stack < 0 or stack > 7:
		raise ValueError('Invalid stack level')
	stack = 0x07 ^ stack
	val = check(bus, DEVICE_ADDRESS + stack)
	val = IOToRelay(val) 
	bus.close()
	return val
