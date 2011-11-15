#!/usr/bin/env python

import sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
import scipy
import EMAN

def main():
	(options, maps, rotspin) = parse_command_line()

	pid = EMAN.LOGbegin(sys.argv)
	EMAN.LOGInfile(pid, maps[0])
	EMAN.LOGInfile(pid, maps[1])
	EMAN.LOGOutfile(pid, maps[2])
	
	target=EMAN.EMData()
	target.readImage(maps[0], -1)
	
	probe=EMAN.EMData()
	probe.readImage(maps[1], -1)

	if options.prealign: 
		x0 = ellipsoid_fitting_align(target, probe)
	else: 
		x0 = initial_transform(pretrans = options.pretrans, rotspin=rotspin, posttrans=options.posttrans)
	
	if options.maxscale>options.minscale: x0 += [(options.maxscale+options.minscale)/2.]
	print "Initial transform:", x0
	
	ref=target.copy(0,0)
	
	threshold_target = options.targetthresh
	threshold_probe  = options.targetthresh
	scorefunc = options.score

	extra_args = (target, probe, threshold_target, threshold_probe, scorefunc, options.verbose)
	
	if options.optimizer == "simplex":	# good
		xopt = scipy.optimize.fmin(score, x0, args=extra_args, xtol=1e-3, ftol=1e-4, maxiter=None, maxfun=None,full_output=0, disp=1, retall=0)
	elif options.optimizer == "powell":		# can not stop
		xopt = scipy.optimize.fmin_powell(score, x0, args=extra_args, xtol=1e-3, ftol=1e-4, maxiter=None, maxfun=None,full_output=0, disp=1, retall=0)
	elif options.optimizer == "cg":		# can not stop
		xopt = scipy.optimize.fmin_cg(score, x0, fprime=None, args=extra_args, gtol=1e-4, norm=scipy.inf, epsilon=1e-3, maxiter=None, full_output=0, disp=1, retall=0)
	elif options.optimizer == "bfgs":	# can not stop
		xopt = scipy.optimize.fmin_bfgs(score, x0, fprime=None, args=extra_args, gtol=1e-4, norm=-scipy.inf, epsilon=1e-3, maxiter=None, full_output=0, disp=1, retall=0)
	elif options.optimizer in ["lbfgs","tnc"]:	# not too bad
		if options.maxtrans:
			bounds = [	(-180,180),(-180,180),(-180,180), 
						(x0[3] - options.maxtrans[0], x0[3] + options.maxtrans[0]), 
						(x0[4] - options.maxtrans[1], x0[4] + options.maxtrans[1]), 
						(x0[5] - options.maxtrans[2], x0[5] + options.maxtrans[2]) 
					 ]
		else:
			dmax = target.xSize()
			bounds=((-180,180),(-180,180),(-180,180),(-dmax,dmax),(-dmax,dmax),(-dmax,dmax))
		if len(x0)==7: bounds += [ (options.minscale, options.maxscle) ]
		
		if options.optimizer == "lbfgs":
			xopt, f, d = scipy.optimize.fmin_l_bfgs_b(score, x0, fprime=None, args=extra_args, approx_grad=True, bounds=bounds, m=10, factr=10000000.0, \
										pgtol=1e-05, epsilon=1e-03, iprint=-1, maxfun=15000)	
		elif options.optimizer == "tnc":	# slow
			rc, nfeval, xopt = scipy.optimize.fmin_tnc(score, x0, fprime=None, args=extra_args, approx_grad=True, bounds=bounds, epsilon=1e-03, \
								scale=None, messages=15, maxCGit=-1, maxfun=None, eta=-1, stepmx=0, accuracy=0, fmin=0, ftol=0, rescale=-1)	
	elif options.optimizer == "cobyla":		# good
		if options.maxtrans:
			trans_bounds = [(x0[3] - options.maxtrans[0], x0[3] + options.maxtrans[0]), 
							(x0[4] - options.maxtrans[1], x0[4] + options.maxtrans[1]), 
							(x0[5] - options.maxtrans[2], x0[5] + options.maxtrans[2]) ]
		else:
			trans_bounds = None
		if options.maxrot>0:
			maxrot = options.maxrot*scipy.pi/180.
			rotinit = EMAN.Quaternion()
			ang = scipy.sqrt(x0[0]*x0[0] + x0[1]*x0[1] + x0[2]*x0[2])
			if ang: rotinit.setQuaternionAngleAxis(ang*scipy.pi/180., x0[0]/ang, x0[1]/ang, x0[2]/ang)
			else: rotinit.setQuaternionAngleAxis(0, 0, 0, 1)
		else:
			maxrot = None

		def cons(*args): 
			if trans_bounds:
				dx = args[3], dy = args[4], dz = args[5]
				trans_ok = trans_bounds[0][0] < dx < trans_bounds[0][1] and trans_bounds[1][0] < dy < trans_bounds[1][1] and \
						   trans_bounds[2][0] < dz < trans_bounds[2][1]
				if trans_ok == 0: trans_ok = -1
			else:
				trans_ok = 1
			if maxrot:
				rotcur = EMAN.Quaternion()
				ang = scipy.sqrt(args[0]*args[0] + args[1]*args[1] + args[2]*args[2])
				if ang: rotcur.setQuaternionAngleAxis(ang*scipy.pi/180., args[0]/ang, args[1]/ang, args[2]/ang)
				else: rotcur.setQuaternionAngleAxis(0, 0, 0, 1)
				
				rot_con = maxrot - rotinit.getAngle(rotcur)
			else:
				rot_con = 1
			if len(x0)==7: 
				scale = args[6]
				scale_ok = scale >= options.minscale and scale <= options.maxscale
				if scale_ok==0: scale_ok = -1
			else:
				scale_ok = 1
			return rot_con * trans_ok*scale_ok
				
		xopt = scipy.optimize.fmin_cobyla(score, x0, cons=[cons], args=extra_args, consargs=None, rhobeg=1e-1, rhoend=1e-3, iprint=1, maxfun=1000)	
	elif options.optimizer == "anneal":
		up=max(target.xSize(), 180)
		low = - up
		xopt, d = scipy.optimize.anneal(score, x0, args=extra_args, schedule='fast', full_output=0, T0=None, Tf=9.9999999999999998e-13, maxeval=None, \
					  maxaccept=None, maxiter=400, boltzmann=1.0, learn_rate=0.5, feps=1e-4, quench=1.0, m=1.0, \
					  n=1.0, lower=low, upper=up, dwell=50)

	ang = scipy.sqrt(xopt[0]*xopt[0] + xopt[1]*xopt[1] + xopt[2]*xopt[2])
	if ang!=0: spinaxis = (xopt[0]/ang, xopt[1]/ang, xopt[2]/ang, ang*scipy.pi/180.)
	else: spinaxis = (0, 0, 1, 0)
	e = EMAN.Euler(spinaxis[0],spinaxis[1],spinaxis[2],spinaxis[3],EMAN.Euler.SPIN)
	print "Final transform:  rot=%g,%g,%g trans=%g,%g,%g" % (e.alt()*180./scipy.pi,e.az()*180./scipy.pi,e.phi()*180./scipy.pi,xopt[3],xopt[4],xopt[5])
	print "\tie. rotation axis = %g %g %g\tangle = %g" % (spinaxis[0],spinaxis[1],spinaxis[2],spinaxis[3])
	print "\tinverse transform: --posttrans %g %g %g --rotspin %g %g %g %g" % (-xopt[3],-xopt[4],-xopt[5], spinaxis[0],spinaxis[1],spinaxis[2],-spinaxis[3])
	if len(x0)==7:
		scale = xopt[6]
		print "\tscale = %g" % ( scale)
	else:
		scale = 1.0
	
	# apply the final transform to probe
	probe2=probe.copy(0,0)
	probe2.setRAlign(e)
	probe2.setTAlign(xopt[3], xopt[4], xopt[5])
	probe2.rotateAndTranslate(scale)
	probe2.setPixel(target.Pixel())
	probe2.setXYZOrigin(target.getXorigin(),target.getYorigin(),target.getZorigin())          
	probe2.writeImage(maps[2])

	EMAN.LOGend()

def score( x, ref, probe, threshold_target, threshold_probe, scorefunc, verbose ):
	
	ang = scipy.sqrt(x[0]*x[0] + x[1]*x[1] + x[2]*x[2])
	if ang!=0: 
		e = EMAN.Euler(x[0]/ang, x[1]/ang, x[2]/ang, ang*scipy.pi/180., EMAN.Euler.SPIN)
	else:
		e = EMAN.Euler(0, 0, 1, 0., EMAN.Euler.SPIN)
	alt = e.alt()
	az  = e.az()
	phi = e.phi()
	
	dx = x[3]
	dy = x[4]
	dz = x[5]
	
	if len(x)==7: scale = x[6]
	else: scale = 1.0
	
	probe2=probe.copy(0,0)
	probe2.setRAlign(alt,az,phi)
	probe2.setTAlign(dx,dy,dz)
	probe2.rotateAndTranslate(scale)
	
	probe2thresh = probe2.copy()
	probe2thresh.realFilter(0,threshold_probe)
	
	probe2bin = probe2.copy()
	probe2bin.realFilter(2,threshold_probe)
	refmasked = ref.copy()
	refmasked.mult(probe2bin)
	
	if scorefunc == "ncc":
		tempscore= 1 - probe2thresh.ncccmp(refmasked)
	elif scorefunc == "dot":
		norm = ref.xSize()*ref.ySize()*ref.zSize()
		tempscore= - probe2thresh.dot(refmasked)/norm
	if verbose: print "compute score:", x, "->", tempscore
	return tempscore

def ellipsoid_fitting_align(ref, probe):
	objref = EMAN.ObjectStat()
	objprobe = EMAN.ObjectStat()
	objref.SetObject(ref)
	objprobe.SetObject(probe)
	eref = objref.rotationFromOrigin()
	eref = EMAN.Euler(eref.alt(), eref.az(), eref.phi())
	eprobe = objprobe.rotationFromOrigin()
	eprobe_inv = eprobe.inverse()
	eprobe_inv = EMAN.Euler(eprobe_inv.alt(), eprobe_inv.az(), eprobe_inv.phi())
	ediff = eref * eprobe_inv	# rotate probe to ref
	print "ref   center: %g %g %g" % (objref.xc, objref.yc, objref.zc)
	print "probe center: %g %g %g" % (objprobe.xc, objprobe.yc, objprobe.zc)
	print "orientation diff: %g %g %g" % (ediff.alt()*180./scipy.pi, ediff.az()*180./scipy.pi, ediff.phi()*180./scipy.pi) 
	return initial_transform(	pretrans = (-objprobe.xc, -objprobe.yc, -objprobe.zc), \
							 	rotspin  = (ediff.n1(), ediff.n2(), ediff.n3(), ediff.Q() * 180./scipy.pi), \
								posttrans= (objref.xc, objref.yc, objref.zc) )

def initial_transform(pretrans = None, rotspin=None, posttrans=None):
	total_pretrans = scipy.zeros((3,),typecode='f')
	if pretrans: total_pretrans += scipy.array(pretrans,typecode='f')
	if rotspin:
		n1 = rotspin[0]; n2 = rotspin[1]; n3 = rotspin[2]; Q = rotspin[3]
	else:
		n1 = 0; n2 = 0; n3 = 1; Q = 0
	if posttrans:
		posttrans_Vect = EMAN.Vect(posttrans[0], posttrans[1], posttrans[2])
		e = EMAN.Euler(n1, n2, n3, Q*scipy.pi/180., EMAN.Euler.SPIN)
		tmp_trans = posttrans_Vect.rotate(e.inverse())
		print "total_pretrans", total_pretrans
		print "rot", rotspin
		print "rot2", e.alt()*180./scipy.pi, e.az()*180./scipy.pi, e.phi()*180./scipy.pi
		print "post", posttrans
		print "tmp_trans", [tmp_trans.X(), tmp_trans.Y(), tmp_trans.Z()]
		total_pretrans += scipy.array([tmp_trans.X(), tmp_trans.Y(), tmp_trans.Z()],typecode='f')
		print "final pretrans", total_pretrans
	
	x0 = [ n1*Q, n2*Q, n3*Q, total_pretrans[0], total_pretrans[1], total_pretrans[2] ]
	return x0
	
def parse_command_line():
	usage = "Usage: %prog <target> <probe> <output fitted probe> [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("--roteuler",dest="roteuler",metavar="alt az phi",type="float",nargs=3, \
					  help="initial rotation in EMAN Euler notation (in degree)")
	parser.add_option("--rotspin",dest="rotspin",metavar="x y z ang",type="float",nargs=4, \
					  help="initial rotation in spin axis notation (in degree)")
	parser.add_option("--pretrans",dest="pretrans",metavar="dx dy dz",type="float",nargs=3, \
					  help="initial translation before the rotation (in pixel or Angstrom if apix is used)")
	parser.add_option("--posttrans",dest="posttrans",metavar="dx dy dz",type="float",nargs=3, \
					  help="initial translation after the rotation (in pixel)")
	parser.add_option("--maxrot",dest="maxrot",metavar="angle",type="float",nargs=1, \
					  help="maximal allowed rotation from starting values (in degree)")
	parser.add_option("--maxtrans",dest="maxtrans",metavar="dx dy dz",type="float",nargs=3, \
					  help="maximal allowed translation after the refinement (in pixel)")
	parser.add_option("--minscale",dest="minscale",metavar="scale",type="float",nargs=1, \
					  help="minimal allowed scale, default=1", default=1)
	parser.add_option("--maxscale",dest="maxscale",metavar="scale",type="float",nargs=1, \
					  help="maximal allowed scale, default=1", default=1)
	parser.add_option("--probethresh",dest="probethresh",type="float",help="threshold for the probe map. default to 0", default=0)
	parser.add_option("--targetthresh",dest="targetthresh",type="float",help="threshold for the target map. default to 0", default=0)
	parser.add_option("--apix",dest="apix",type="float",help="angstrom/pixel for the maps", default=0)
	parser.add_option("--prealign",dest="prealign",action="store_true",help="use ellipsoidal fitting to find the initial alignment, default to 0", default=0)
	parser.add_option("--optimizer",dest="optimizer",type="choice",choices=["simplex","powell","cg","bfgs","lbfgs","tnc","cobyla","anneal"], \
					  help="optimizer to use", default="simplex")
	parser.add_option("--score",dest="score",type="choice",choices=["ncc","dot"], \
					  help="scoring function to use", default="ncc")
	
	parser.add_option("--verbose",dest="verbose",action="store_true",help="default to 0", default=0)
	
	(options, maps)=parser.parse_args()

	if len(maps) !=3:
		parser.print_help()
		sys.exit(-1)
	
	if options.roteuler:
		e = EMAN.Euler(options.roteuler[0]*scipy.pi/180., options.roteuler[1]*scipy.pi/180., options.roteuler[2]*scipy.pi/180.)
		Q = e.Q()*180./scipy.pi
		n1= e.n1()
		n2= e.n2()
		n3= e.n3()
	elif options.rotspin:
		Q = options.rotspin[3]
		n1= options.rotspin[0]
		n2= options.rotspin[1]
		n3= options.rotspin[2]
	else:
		Q = 0
		n1 = 0
		n2 = 0
		n3 = 1
		
	if options.maxscale<options.minscale:
		raise ValueError(": maxscale=%g < minscale=%g" % (options.maxscale, options.minscale))
	elif options.maxscale <=0: 
		raise ValueError(": maxscale=%g <=0, it must be>0" % (options.maxscale))
	elif options.minscale <=0: 
		raise ValueError(": minscale=%g <=0, it must be>0" % (options.minscale))
	
	
	return (options, maps, (n1,n2,n3,Q) )

if __name__== "__main__":
	main()

