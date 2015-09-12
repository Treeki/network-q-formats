The .BUN image format
=====================

### Credits:
  * Ninji (@_Ninji) for doing the heavy-lifting
  * Svetlana (@lana_chan_) for writing this documentation

Description
-----------

 This is a document describing the .BUN image format found in the data files for
the  1996 DOS game  *Network Q RAC Rally Championship*  by  Magnetic Fields Ltd.

 We believe the BUN extension is named after BUNdle, since each file can contain
several slices within itself.  This format seems to be used  mostly in the menus
of the game, if not entirely.

Format
------

### 1. Header

 .BUN does not have a header,  however, it starts out with several file offsets,
each of which relates to a different  image slice.  Each image slice can only be
up to 200 by 200  pixels in size.  The number of offsets  (and therefore slices)
can be inferred by the very first offset, which points to the first slice. Since
all data before said slice are offsets, dividing that number by the size of each
offset (4-byte integers) gives us the offset count.

 Note:  Not all .BUN files are necessarily pictures.  Some of the files found in
the original game are font files,  where each image slice is a single character.

  ```18 00 00 00 AC 9E 00 00 48 3D 01 00 BC D8 01 00 16 20 02 00 78 67 02 00```

 In this example, the first offset is 0x18 (24 in decimal), which, divided by 4,
gives us 6 offsets: 0x18, 0x9EAC, 0x13D48, 0x1D8BC, 0x22016 and 0x26778.

### 2. Slices

 Each slice starts with 4 bytes of data.  The first 2 bytes are only non-zero in
font bundles,  but their purpose isn't  entirely known yet,  they could refer to
spacing and kerning of each character slice in the font bundle.  The following 2
bytes specify the width and height of the current slice, 1 byte each.

 After that, rows are encoded with a RLE-like compression. The row begins with 2
bytes,  one specifying the length of non-empty pixels  while the other specifies
the length of empty pixels directly to the left, meaning when you're writing the
image,  you jump the number of empty pixels  then output the length of non-empty
pixels to the image. This step is looped until the length of non-empty pixels is
read as 00,  meaning the end of the row.  What directly follows is the next row,
remembering that you must read as many rows as the height of the image slice.

  ```00 00 C8 C8 C4 04```
  
 In this example of the first 6 bytes of an image slice, the first two bytes are
blank,  meaning this is not a font character.  The width and height of the slice
are 0xC8 (200 in decimal),  meaning there are 200 rows that are 200 pixels wide.
At the start of the first row, the bytes 0xC4 0x04 mean there are 4 empty pixels
followed by 196 non-empty pixels. The empty pixels seem to be interpreted in the
game as a transparency mask.

### 3. Palettes

 The palette format is very straight-forward. Each .BUN file is accompanied by a
.PAL file.  Usually the palette file  will have the same name as the image file,
but that is not always the case. Inside the palette file, the only data there is
are RGB tuples with one byte for each value. Each palette consists of 256 colors
(768 bytes) and each palette file can have more than one palette in it,  with no
header or separator between them.

 This is loaded in memory when  decoding the image,  and each non-empty pixel of
data is actually a palette index.  Basically,  the palette index is a 0-counting
value that, when multiplied by three,  gives the offset for the palette file for
the R, G and B values (one byte each) of that pixel.

### 4. Usage of the Python tool

 The bunpack.py file provided is a command line decoder for the .BUN files found
in the game,  working with the principles described in this document.  The usage
is as follows:

  ```bunpack.py [-p palfile] [-i index] bunfile```
  
  * **bunfile** - path of the .BUN file
  * **palfile (optional)** - path of the .PAL file, in case the filename differs
  * **index (optional)** - the palette index offset, starting at 0