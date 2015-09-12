#!/usr/bin/env python

import struct, sys
from PIL import Image

u8 = struct.Struct('<B')

def convert_palette(pal):
  result = []
  s = struct.Struct('<BBB')

  for i in range(len(pal) // 3):
    result.append(s.unpack_from(pal, i * 3))

  return result

def extract_image(data, offset, pal):
  width = u8.unpack_from(data, offset + 2)[0]
  height = u8.unpack_from(data, offset + 3)[0]
  if width == 0 or height == 0:
    return None

  colours = convert_palette(pal)
  img = Image.new('RGB', (width,height))
  pix = img.load()

  offset += 4
  for y in range(height):
    x = 0

    while True:
      block_width = u8.unpack_from(data, offset)[0]
      if block_width == 0:
        # end of row
        offset += 1
        break

      spacing_before = u8.unpack_from(data, offset + 1)[0]
      offset += 2

      x += spacing_before
      for _ in range(block_width):
        index = u8.unpack_from(data, offset + 1)[0]
        pix[x,y] = colours[index]
        x += 1
        offset += 1

  return img

def main(argv):
  import argparse, string
  import os.path
  
  parser = argparse.ArgumentParser(description='Converts Network Q .BUN files into .PNG')
  parser.add_argument('input', metavar='infile', type=str, nargs=1, help='the input file (.BUN)')
  parser.add_argument('-p', '--pal', type=str, help='optional palette file (.PAL)', dest='pal')
  args = parser.parse_args()
  
  path,ext = os.path.splitext(args.input[0])
  try:
    palpath = os.path.splitext(args.pal)[0]
  except:
    palpath = path
  
  if ext != '.BUN':
    print('File does not have .BUN extension!')
    return
  
  filename = os.path.split(path)[1]
  
  try:
    f = open(path + '.BUN', 'rb')
  except IOError as e:
    print('Unable to open BUN file!')
    return
  else:
    data = f.read()
    f.close()
  
  try:
    f = open(palpath + '.PAL', 'rb')
  except IOError as e:
    print('Unable to open PAL file!')
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

  if not os.path.exists(filename):
    try:
      os.mkdir(filename)
    except:
      print('Unable to create path ' + filename + '!')
      return
    
  for i, offset in enumerate(offsets):
    img = extract_image(data, offset, pal_data)
    if img is not None:
      img.save(filename + '/%d.png' % i)

if __name__ == "__main__":
  main(sys.argv[1:])
