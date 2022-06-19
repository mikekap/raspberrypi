import struct

BIT_MARK = 562500
ONE_SPACE = 3 * BIT_MARK
ZERO_SPACE = BIT_MARK


def encode_duration(duration):
  """Encodes the given duration as a sequence of bytes understood by Broadlink devices.
  Args:
    duration: The duration in microseconds.
  Returns:
    The encoded duration.
  """
  bl_duration = duration * 269 // 8192000
  if bl_duration > 0xff:
    return [0x00] + list(struct.pack(">H", bl_duration))
  return [bl_duration]

def nec_to_broadlink(nec_code):
  code = []
  def add_byte(b):
    b = b & 0xFF
    for i in range(8):
      bit = b & (1 << i)
      code.extend(encode_duration(BIT_MARK))
      code.extend(encode_duration(ONE_SPACE if bit else ZERO_SPACE))

  code.extend(encode_duration(BIT_MARK * 16))
  code.extend(encode_duration(BIT_MARK * 8))

  add_byte(nec_code >> 8)
  add_byte(~(nec_code >> 8))
  add_byte(nec_code)
  add_byte(~nec_code)

  code.extend(encode_duration(BIT_MARK))

  final_code = [0x26, 0x00] + list(struct.pack("<H", len(code))) + code
  return b''.join(x.to_bytes(1, 'big') for x in final_code)


def necx_to_broadlink(nec_code):
  code = []
  def add_byte(b):
    b = b & 0xFF
    for i in range(8):
      bit = b & (1 << i)
      code.extend(encode_duration(BIT_MARK))
      code.extend(encode_duration(ONE_SPACE if bit else ZERO_SPACE))

  code.extend(encode_duration(BIT_MARK * 16))
  code.extend(encode_duration(BIT_MARK * 8))

  add_byte(nec_code >> 16)
  add_byte(nec_code >> 8)
  add_byte(nec_code)
  add_byte(~nec_code)

  code.extend(encode_duration(BIT_MARK))

  final_code = [0x26, 0x00] + list(struct.pack("<H", len(code))) + code
  return b''.join(x.to_bytes(1, 'big') for x in final_code)

