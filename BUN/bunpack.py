#!/usr/bin/env python

import struct, sys
from PIL import Image

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

def main(argv):
  import argparse, string
  import os.path
  
  parser = argparse.ArgumentParser(description='Converts Network Q .BUN files into .PNG')
  parser.add_argument('input', metavar='infile', type=str, nargs=1, help='the input file (.BUN)')
  parser.add_argument('-p', '--pal', type=str, help='optional palette file (.PAL)')
  args = parser.parse_args()
  
  path,ext = os.path.splitext(args.input[0])
  try:
    palpath = args.input[1]
  except:
    palpath = path
  
  if ext != '.BUN':
    print 'File does not have .BUN extension!'
    return
  
  filename = os.path.split(path)
  
  try:
    f = open(path + '.BUN', 'rb')
  except IOError as e:
    print 'Unable to open BUN file!'
    return
  else:
    data = f.read()
    f.close()
  
  try:
    f = open(palpath + '.PAL', 'rb')
  except IOError as e:
    print 'Unable to open PAL file!'
    return
  else:
    pal_data = f.read()
    f.close()

  # read the file header (list of offsets)
  first_offset = struct.unpack_from('<I', data, 0)[0]
  image_count = first_offset // 4
  offsets = []

  for i in range(image_count):
    offsets.append(struct.unpack_from('<I', data, i * 4)[0])


  for i, offset in enumerate(offsets):
    img = extract_image(data, offset, pal_data)
    if img is not None:
      img.save(filename + '/%d.png' % i)

if __name__ == "__main__":
  main(sys.argv[1:])
