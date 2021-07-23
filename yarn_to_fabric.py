import numpy as np
import math
import periodic_disjoint as periodic #change this line to change tiling method
'''
	Class representing a reference frame along a polyline. 
	
	t: normalized tangent vector
	n: normalized normal vector
	b: normalized binormal vector
	point: the point that generated this reference frame 
	parametric: the parametric value for this point along the polyline 
'''
class RefFrame:
	def __init__(self, _t, _n, _b, _p, _z):
		self.t = _t
		self.n = _n
		self.b = _b
		self.point = _p
		self.parametric = _z

def normalize(v):
    norm = np.linalg.norm(v)
    if norm < 0.001: 
       return v
    return v / norm

'''
	Process a single fiber strand by transforming it from yarn space to fabric space. 

	We do this by following the mapping process described in "Fiber-Level On-the-Fly Procedural Textiles"

	Reference frame calculation follows "Calculation of Reference Frames along a Space Curve" (Jules Bloomenthal)
'''
def processFiber(outfileobj, refFrames, yarn_to_fabric, fiberFile, num_strands, z_step_size, z_step_num):
	verts = periodic.tileYarn(fiberFile, num_strands, z_step_size, z_step_num)
	
	for vert in verts:
		if len(vert) < 3:
			outfileobj.write(vert[0])
		else:
			newPoint = np.array([0.,0.,0.])
			yarnParam = vert[2] * yarn_to_fabric

			for i in range(len(refFrames) - 1):
				if refFrames[i].parametric <= yarnParam and refFrames[i+1].parametric > yarnParam:
					alpha = refFrames[i].point + refFrames[i].t*(yarnParam - refFrames[i].parametric)
					newPoint = (vert[0]*yarn_to_fabric)*refFrames[i].n + (vert[1]*yarn_to_fabric)*refFrames[i].b + alpha

			if not (newPoint[0] == 0 and newPoint[1] == 0 and newPoint[2] == 0):
				outfileobj.write(str(newPoint[0]) + ' ' + str(newPoint[1]) + ' ' + str(newPoint[2]) + '\n')


def main(polyFile, fiberFile, configFile, poly_radius, outfile):
	# read in procedural parameters from yarn config file
	with open(configFile, 'r') as c:
		for line in c:
			splitline = line.split()
			if len(splitline) != 0:
				if splitline[0] == 'yarn_radius:':
					yarn_radius = float(splitline[1])
				elif splitline[0] == 'z_step_size:':
					z_step_size = float(splitline[1])
				elif splitline[0] == 'z_step_num:':
					z_step_num = float(splitline[1])

	yarn_to_fabric = poly_radius/yarn_radius
	fabric_to_yarn = yarn_radius/poly_radius

	with open(outfile, 'w') as h:
		with open(polyFile, 'r') as g:
			prevPt = None
			curPt = None
			polylineLen = 0.
			runTotalLen = 0.
			refFrames = []
			count = 0

			line = g.readline()

			while True:
				splitline = line.split()
				if len(splitline) != 3 or line == '': # end of current fiber, process then move to next
					polylineLen = runTotalLen
					if polylineLen > 0:
						processFiber(h, refFrames, yarn_to_fabric, fiberFile, math.ceil(polylineLen*fabric_to_yarn), z_step_size, z_step_num)
						count += 1
						print 'num polylines processed: ' + str(count) # useful to check progress
					prevPt = None
					curPt = None
					polylineLen = 0.
					runTotalLen = 0.
					refFrames = []
					h.write(line)
				else:
					curPt = np.array([float(splitline[0]), float(splitline[1]), float(splitline[2])])
					
					# create the reference frame with 'prevPt' as its origin
					if prevPt is not None:
						# we create reference frames for each new line segment by rotating the previous one
						# a reference frame is an orthonormal basis, thus we need 3 mutually normal vectors
						# we use t (the tangent), n (an arbitrary normal), and b (a binormal)
						
						# t is the tangent vector, which is just the normalized direction from the 
						# prevPt to the curPt (the next point along the polyline)
						t = normalize(curPt - prevPt)
						if len(refFrames) == 0:
							# if we are creating the first reference frame, we create an arbitrary
							# normal n which is orthogonal to t. Let n = <1, 1, k> and t = <t1, t2, t3>.
							# Then, t1 + t2 + t3*k = 0 and k = -(t1 + t2)/t3
							#<k = (-1 * (prevPt[0] + prevPt[1])) / prevPt[2]> old, erroneous normal calculation
							k = (-1 * (t[0] + t[1])) / t[2]
							n = normalize(np.array([1,1,k]))
							
							# b is an an arbitrary binormal, a vector that is orthogonal to both t and n
							# since b can be any such vector, we use the cross product of t and n
							b = normalize(np.cross(t, n))
						else:
							# calculations for sequential reference frames taken from 
							# http://webhome.cs.uvic.ca/~blob/courses/305/notes/pdf/ref-frames.pdf
							n = normalize(np.cross(refFrames[-1].b, t)) 
							b = normalize(np.cross(t, n))

						refFrames.append(RefFrame(t, n, b, prevPt, runTotalLen))
						runTotalLen += np.linalg.norm(curPt - prevPt)

					prevPt = curPt
				if line == '':
					break
				else:
					line = g.readline()


'''
	Syntax: python yarn_to_fabric.py <polyline_file> <yarn_file> <yarn_config_file> <polyline_radius> <output_file>
'''
if __name__ == '__main__':
	from sys import argv
	print 'Attaching fiber model ' + argv[2] + ' to polyline ' + argv[1] + '.\nUsing config file ' + argv[3] + ' with polyline radius ' + argv[4] +'\nSaving result in ' + argv[5]
	main(argv[1], argv[2], argv[3], float(argv[4]), argv[5])
