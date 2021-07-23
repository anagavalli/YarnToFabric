import numpy as np
'''
	Tiles a yarn model num_strands times.

	filename: name of yarn model file
	num_strands: number of periods to tile yarn 
	z_step_size: step size of z-axis of yarn file (taken from config file)
	z_step_num: number of z-steps across the yarn (taken from config file)
'''
def tileYarn(filename, num_strands, z_step_size, z_step_num):
	curOffset = int(num_strands)
	z_offset = 0.5*z_step_num*z_step_size
	z_total = z_step_size*z_step_num

	verts = []

	while curOffset > 0: 
		with open(filename, 'r') as f:
			newStrand = ''
			curOffset -= 1

			for line in f:
				splitLine = line.split()
				if len(splitLine) != 3:
					# we have reached the end of a fiber, append an empty line to seperate fiber
					verts.append([line])
				else:
					# adjust points to be in the range [0, z] where z is the desired length of the tiled yarn
					newVert = splitLine
					newVert[0] = float(newVert[0])
					newVert[1] = float(newVert[1])
					newVert[2] = float(newVert[2]) + z_offset + curOffset*z_total - z_step_size*curOffset 
					verts.append(np.array(newVert))
	return verts


'''
	Syntax: python periodic_disjoint.py <yarn_file> <num_strands> <z_step_size> <z_step_num> <outfile>
'''
if __name__ == '__main__':
	from sys import argv
	print 'duplicating ' + argv[1] + ' to have ' + argv[2] + ' strands'
	print 'z_step_size: ' + argv[3]
	print 'z_step_num: ' + argv[4]
	print 'starting duplication'
	verts = tileYarn(argv[1], int(argv[2]), float(argv[3]), float(argv[4]))
	print 'finish duplication, saving to ' + argv[5]
	aggregate = ''
	for i in range(len(verts)):
		if len(verts[i]) < 3:
			aggregate += verts[i][0]
		else:
			newVert = [str(verts[i][0]), str(verts[i][1]), str(verts[i][2])]
			aggregate += str.join(' ', newVert) + '\n'
	with open(argv[5], 'w') as g:
		g.write(aggregate)