# CONST
EARTH_GRAVITY_MS2   = 9.80665
PIN_ADXL_INT1 = 21
PIN_ADXL_INT2 = 20
# +--------------------------+
# |     ADRESY REJESTRÓW     |
# +--------------------------+
REG_DEV_ID      = 0x00
REG_BW_RATE     = 0x2C
REG_POWER_CTL   = 0x2D
REG_INT_ENABLE  = 0x2E
REG_INT_MAP     = 0x2F
REG_INT_SOURCE  = 0x30
REG_DATA_FORMAT = 0x31
REG_DATAX0      = 0x32
REG_DATAX1      = 0x33
REG_DATAY0      = 0x34
REG_DATAY1      = 0x35
REG_DATAZ0      = 0x36
REG_DATAZ1      = 0x37
REG_FIFO_CTL    = 0x38
REG_FIFO_STATUS = 0x39
REG_MEASURE     = 0x08
REG_AXES_DATA   = 0x32



#REG_BW_RATE bits (0x2C)
# +----+----+----+------+----+----+----+----+
# | D7 | D6 | D5 |  D4  | D3 | D2 | D1 | D0 |
# +----+----+----+------+----+----+----+----+
# | 0  | 0  | 0  |lowPWR|  R   A    T    E  |
# +----+----+----+------+----+----+----+----+
BW_RATE_lowPowerOn  = 0x10  #stan wysoki oznacza włączenie
BW_RATE_lowPowerOff = 0x00
BW_RATE_3200HZ      = 0x0F
BW_RATE_1600HZ       = 0x0E
BW_RATE_800HZ       = 0x0D
BW_RATE_400HZ       = 0x0C
BW_RATE_200HZZ       = 0x0B

#REG_POWER_CTL bits (0x2D)
# +----+----+----+---------+--------+-----+----+----+
# | D7 | D6 | D5 |  D4     |   D3   | D2  | D1 | D0 |
# +----+----+----+---------+--------+-----+----+----+
# | 0  | 0  |link|autoSleep| Measure|Sleep| Wakeup  |
# +----+----+----+---------+--------+-----+----+----+
POWER_CTL_WAKEUP_8HZ           =0x00
POWER_CTL_WAKEUP_4HZ           =0x01
POWER_CTL_WAKEUP_2HZ           =0x02
POWER_CTL_WAKEUP_1HZ           =0x03
POWER_CTL_SLEEP                =0x04
POWER_CTL_MEASURE              =0x08
POWER_CTL_STANDBY              =0x00
POWER_CTL_AUTO_SLEEP           =0x10
POWER_CTL_ACT_INACT_SERIAL     =0x20
POWER_CTL_ACT_INACT_CONCURRENT =0x00

#POWER_CTLMAT bits (0x31)
# +----+----+----+----------+----+--------+--------+----+----+
# | D7      | D6 | D5       | D4 | D3     | D2     | D1 | D0 |
# +---------+----+----------+----+--------+--------+----+----+
# |self_test|SPI |int_invert| 0  |full_res| justify| range   |
# +---------+----+----------+----+--------+--------+----+----+
DATA_FORMAT_RANGE_2G    = 0x00
DATA_FORMAT_RANGE_4G    = 0x01
DATA_FORMAT_RANGE_8G    = 0x02
DATA_FORMAT_RANGE_16G   = 0x03
DATA_FORMAT_JUST_LEFT   = 0x04
DATA_FORMAT_JUST_RIGHT  = 0x00
DATA_FORMAT_10BIT       = 0x00
DATA_FORMAT_FULL_RES    = 0x08
DATA_FORMAT_INT_LOW     = 0x20
DATA_FORMAT_INT_HIGH    = 0x00
DATA_FORMAT_SPI3WIRE    = 0x40
DATA_FORMAT_SPI4WIRE    = 0x00
DATA_FORMAT_SELF_TEST   = 0x80

# +-------------------------+
# |     INTERRUPTS          |
# +-------------------------+

# REG_INT_SOURCE (0x30)
# +----------+----------+----------+----------+----------+----------+----------+----------+
# |D7        |D6        |D5        |D4        |D3        |D2        |D1        |D0        |
# +----------+----------+----------+----------+----------+----------+----------+----------+
# |DATA_READY|SINGLE_TAP|DOUBLE_TAP| ACTIVITY |INACTIVITY|FREE_FALL |WATERMARK |OVERRUN   |
# +----------+----------+----------+----------+----------+----------+----------+----------+
#Bit values in INT_ENABLE, INT_MAP, and INT_SOURCE are identical
#  use these bit values to read or write any of these registers.
INT_OVERRUN      =0x01
INT_WATERMARK    =0x02
INT_FREEFALL     =0x04
INT_INACTIVITY   =0x08
INT_ACTIVITY     =0x10
INT_DOUBLETAP    =0x20
INT_SINGLETAP    =0x40
INT_DATAREADY    =0x80

# REG_INT_MAP (0x2F)
# +----------+----------+----------+----------+----------+----------+----------+----------+
# |D7        |D6        |D5        |D4        |D3        |D2        |D1        |D0        |
# +----------+----------+----------+----------+----------+----------+----------+----------+
# |DATA_READY|SINGLE_TAP|DOUBLE_TAP| ACTIVITY |INACTIVITY|FREE_FALL |WATERMARK |OVERRUN   |
# +----------+----------+----------+----------+----------+----------+----------+----------+

# REG_INT_ENABLE (0x2E)
# +----------+----------+----------+----------+----------+----------+----------+----------+
# |D7        |D6        |D5        |D4        |D3        |D2        |D1        |D0        |
# +----------+----------+----------+----------+----------+----------+----------+----------+
# |DATA_READY|SINGLE_TAP|DOUBLE_TAP| ACTIVITY |INACTIVITY|FREE_FALL |WATERMARK |OVERRUN   |
# +----------+----------+----------+----------+----------+----------+----------+----------+