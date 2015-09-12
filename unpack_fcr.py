import sys
import struct
from PIL import Image


def decompress_sfcr(data):
	comp_size = len(data) - 8
	uncomp_size = struct.unpack_from('<I', data, 4)[0]
	empty_size = uncomp_size - comp_size

	# create a work buffer
	padding = b'\0' * empty_size
	work = bytearray(padding + data[8:])

	# decompress things!
	src_pos = empty_size
	dest_pos = 0
	remaining = uncomp_size

	while remaining > 0:
		count = work[src_pos]
		src_pos += 1

		if count >= 0x80:
			# RLE copy mode
			count = 0x100 - count

			for i in range(count):
				work[dest_pos] = work[src_pos]
				src_pos += 1
				dest_pos += 1

				remaining -= 1
				if remaining <= 0:
					break

		else:
			# RLE fill mode
			fill_byte = work[src_pos]
			src_pos += 1

			for i in range(count):
				work[dest_pos] = fill_byte
				dest_pos += 1

				remaining -= 1
				if remaining <= 0:
					break

	return bytes(work)


path = sys.argv[1]
#path = 'D:\\crap\\networkq\\FILES\\CARDATA\\CAR5PIC.FCR'
with open(path, 'rb') as f:
	palette = f.read(3 * 256)
	data = f.read()

if data.startswith(b'SFCR'):
	data = decompress_sfcr(data)


def convert_palette(pal):
  result = []
  s = struct.Struct('<BBB')

  for i in range(len(pal) // 3):
    result.append(s.unpack_from(pal, i * 3))

  return result



# convert the thing
width = 256
height = len(data) // width
assert(len(data) == (height * width))

palette = convert_palette(palette)
img = Image.new('RGB', (width, height))
pix = img.load()
pos = 0
data = bytearray(data)

for y in range(height):
	for x in range(width):
		pix[x,y] = palette[data[pos]]
		pos += 1

img.save('test.png')

