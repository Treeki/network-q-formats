import sys, getopt
import struct
from PIL import Image

with open('FILES/GFX/FONTW33.BUN', 'rb') as f:
	data = f.read()
with open('FILES/GFX/MAIN.PAL', 'rb') as f:
	pal_data = f.read()

# read the file header (list of offsets)
first_offset = struct.unpack_from('<I', data, 0)[0]
image_count = first_offset // 4
offsets = []

for i in range(image_count):
	offsets.append(struct.unpack_from('<I', data, i * 4)[0])


def extract_image(data, offset, pal):
	width = data[offset + 2]
	height = data[offset + 3]
	if width == 0 or height == 0:
		return None

	img = Image.new('RGB', (width,height))
	pix = img.load()

	offset += 4
	for y in range(height):
		x = 0

		while True:
			if data[offset] == 0:
				# end of row
				offset += 1
				break

			block_width = data[offset]
			spacing_before = data[offset + 1]
			offset += 2

			x += spacing_before
			for _ in range(block_width):
				index = data[offset]
				r = pal[index * 3]
				g = pal[index * 3 + 1]
				b = pal[index * 3 + 2]
				pix[x,y] = (r,g,b)
				x += 1
				offset += 1

	return img


for i, offset in enumerate(offsets):
	img = extract_image(data, offset, pal_data)
	if img is not None:
		img.save('fontw33/%d.png' % i)

