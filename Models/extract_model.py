import struct
import sys

path = 'D:\\crap\\networkq\\FILES\\CARDATA\\OBJWHL0'

with open(path, 'rb') as f:
	data = f.read()


def asdf(a):
	out = []
	for i,c in enumerate(a):
		out.append('%02x' % c)
		if i % 2 == 1:
			out.append(' ')
	return ''.join(out)

header = struct.unpack_from('<HHHHHHHHH', data, 0)
offset_2 = header[1]
offset_4 = header[2]
offset_shapeOffsets = header[3]
offset_shapes = header[4]
offset_vertices = header[5]
count_shapes = header[7]
count_vertices = header[8]

print('%d Shapes, %d Vertices' % (count_shapes, count_vertices))

objf = open('test.obj', 'w')

vertices = []
for i in range(count_vertices):
	offset = offset_vertices + (i * 12)
	v = struct.unpack_from('<iii', data, offset)
	vertices.append(v)

	objf.write('v %s\n' % ' '.join(map(lambda x: str(x / 1024.0), v)))

texture_height = 651
tc_index = 1

for i in range(count_shapes):
	offset_to_offset = offset_shapeOffsets + (i * 2)
	offset = struct.unpack_from('<H', data, offset_to_offset)[0]
	offset2 = struct.unpack_from('<H', data, offset_to_offset + 2)[0]
	offset += offset_shapes

	bits = struct.unpack_from('<HBBHHHHhhh', data, offset)
	vtx_count = bits[0]
	texture_page = bits[1]
	unk1 = bits[2]
	index = bits[3]
	unk2a = vertices[bits[4]]
	unk2b = vertices[bits[5]]
	unk2c = vertices[bits[6]]
	unk3a = bits[7]
	unk3b = bits[8]
	unk3c = bits[9]
	vtx_indices = struct.unpack_from('<%dH' % vtx_count, data, offset + 18)
	tex_left, tex_top, tex_right, tex_bottom = struct.unpack_from('<BBBB', data, offset + 18 + (2 * vtx_count))

	if unk1 == 3:
		continue

	printparams = (
			unk1,
			index,
			unk2a, unk2b, unk2c,
			unk3a, unk3b, unk3c,
			texture_page, tex_left, tex_top, tex_right, tex_bottom,
			)
	print('%d | %2d | %25s,%25s,%25s | %6d,%6d,%6d | %d: %3d,%3d - %3d,%3d' % printparams)
	print('   ', end='')
	for v in vtx_indices:
		print('%25s' % repr(vertices[v]), end='')
	print()

	objf.write('o obj%d\n' % index)

	# allocate texcoords
	tex_top += (texture_page * 256)
	tex_bottom += (texture_page * 256)
	tc_left = tex_left / 256.0
	tc_right = tex_right / 256.0
	tc_top = 1.0 - (tex_top / float(texture_height))
	tc_bottom = 1.0 - (tex_bottom / float(texture_height))
	objf.write('vt %f %f\n' % (tc_left, tc_top))
	objf.write('vt %f %f\n' % (tc_left, tc_bottom))
	objf.write('vt %f %f\n' % (tc_right, tc_bottom))
	objf.write('vt %f %f\n' % (tc_right, tc_top))

	objf.write('f')
	for inc, index in enumerate(vtx_indices):
		objf.write(' %d/%d' % (index + 1, tc_index + (inc % 4)))
	objf.write('\n')
	tc_index += 4

objf.close()

