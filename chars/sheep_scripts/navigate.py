import GameLogic

# Hit a Kill Object? How much and reset the time.

from Mathutils import CrossVecs, Vector, Matrix, RotationMatrix, AngleBetweenVecs, Rand, DotVecs

'''
import GameLogic as g
def setpos(pos):
	try:
		ob_debug = g.DEBUG_OB
	except:
		s = g.getCurrentScene()
		for ob in s.getObjectList():
			if ob.name =='OBdebug':
				ob_debug = ob
				break
	
	ob.setPosition(pos)
	return
'''

DIRECTION = [-1] # 0 nothing, 1 left, 2 right

def SIDE_OF_LINE(pa,pb,pp):
	s = ((pa[0]-pp[0])*(pb[1]-pp[1]))-((pb[0]-pp[0])*(pa[1]-pp[1]))
	return s

def sideOfGameObject(own, own_pos, pt):
	pos_y = own.getAxisVect([0,1,0])
	pos_y[0] += own_pos[0]
	pos_y[1] += own_pos[1]
	
	return SIDE_OF_LINE(own_pos, pos_y, pt)


def reset_target(own, cont, own_pos, predator_ob):
	# print 'RESET TARGET...'
	TARGET_DIST_MIN = 2.0
	TARGET_DIST_MAX = 8.0
	
	own.target_time = 0.0
	
	L = TARGET_DIST_MIN + (Rand() * (TARGET_DIST_MAX-TARGET_DIST_MIN))

	own_front= own.getAxisVect([0,L,0])
	
	# Should we run toward or away?

	# we need a random angle between 90 and 270
	
	if predator_ob:
		if own.revive_time < 4.0:
			# print "recover, escape!"
			ATTACK = False
		elif own.type == 'ram':
			ATTACK = True
		
		elif own.type == 'shp':
			ATTACK = False
		elif own.type == 'rat':
			# attack only when frankie is facing away - Sneaky!
			pred_front = Vector(predator_ob.getAxisVect([0,1,0]))
			pred_front.z = 0.0
			
			pos = Vector(predator_ob.getPosition())
			new_dir = own_pos - pos
			
			if DotVecs(new_dir, pred_front) > 0.0:
				ATTACK = False
			else:
				ATTACK = True
			
		# print 'ATTACK', ATTACK
		# Attack done
		
		
		#if predator_ob and Rand() > 0.33:
		pos = Vector(predator_ob.getPosition())
		new_dir = own_pos - pos
		
		if ATTACK:
			# ATTACK!
			### print 'ATTACK'
			#own.target_x = pos[0]
			#own.target_y = pos[1]
			new_dir.z = 0
			new_dir.length = 3 # set target to be 5 past the character.
			
			own.target_x = pos[0] - new_dir.x
			own.target_y = pos[1] - new_dir.y
		else:
			### print 'FLEE'
			new_dir.z = 0.0
			new_dir.length = L
			
			# new_dir = Vector(own_front) * RotationMatrix(ang, 3, 'z')
			ang = (Rand()*45) - (45/2.0)
			new_dir = new_dir * RotationMatrix(ang, 3, 'z')
			
			own.target_x = new_dir.x + own_pos[0]
			own.target_y = new_dir.y + own_pos[1]
		
	else:
		### print 'RANDOM'
		# Random target
		ang = 90 + (Rand()*180)
		new_dir = Vector(own_front) * RotationMatrix(ang, 3, 'z')
			
		own.target_x = new_dir.x + own_pos[0]
		own.target_y = new_dir.y + own_pos[1]
		
	# setpos([own.target_x, own.target_y, 0.0])

def target_direction(own, cont, own_pos):
	return Vector(own.target_x-own_pos[0], own.target_y-own_pos[1], 0.0)

def angle_target(own, cont, own_pos):
	# Head towards our target 
	direction = target_direction(own, cont, own_pos)
	
	# own_mat = Matrix(*own.getOrientation()).transpose()
	own_y = Vector(own.getAxisVect([0,1,0]))
	own_y.z = 0.0
	ang = AngleBetweenVecs(own_y, direction)
	if CrossVecs(direction, own_y).z < 0.0:
		ang = -ang
	return ang


def go_target(own, cont, own_pos, predator_ob, TARGET_TIME_LIMIT):
	# AURIENT_LAG = 0.02
	
	# Head towards our target 
	target_x = own.target_x
	target_y = own.target_y
	
	if (target_x==-1.0 and target_y==-1.0):
		reset_target(own, cont, own_pos, None)
		target_x = own.target_x
		target_y = own.target_y
	
	direction = target_direction(own, cont, own_pos)
	
	if	(direction.length < 1.2) or \
		(own.target_time > TARGET_TIME_LIMIT) or \
		(predator_ob and own.type in ('ram', 'rat') and own.target_time > 0.15):
		
		# print "Over time limit", (direction.length < 1.2), (own.target_time > TARGET_TIME_LIMIT), (predator_ob and own.type=='ram' and own.target_time > 0.15)
		reset_target(own, cont, own_pos, predator_ob)
	
	'''
	side = sideOfGameObject(own, own_pos, [target_x, target_y])
	if side > 0:
		DIRECTION[0] = 2
		#print "LEFT"
	else:
		DIRECTION[0] = 1
		#print "RIGHT"
	'''
	
	# Angle test means we can check for a low angle
	angle = angle_target(own, cont, own_pos)
	if abs(angle) < 10:
		DIRECTION[0] = 0
	elif angle < 0:
		DIRECTION[0] = 2
		#print "LEFT"
	else:
		DIRECTION[0] = 1
		#print "RIGHT"

def main(cont):
	
	WALL_LIMIT = 0.1
	TURN_TIME = 0.5
	# we are touching somthing and will always turn the same way out.
	# If ray sensors measure this close
	TOO_CLOSE = 0.55
	DIRECTION[0] = 0 # just incase, multiple animals will use this module so must initialize
	
	own = cont.getOwner()
	# print own.type
	actu_motion = cont.getActuator('motion_py')
	
	# print own.target_time
	
	### setpos([own.target_x, own.target_y, 0.0])
	
	cont_name = cont.getName()
	
	#print cont_name, 'cont_name'
	if cont_name.startswith('walk_normal'):
		ROTATE_SPEED = 0.02
		RUN_SPEED = 0.02
		TIME_LIMIT = 6.0
		ESCAPE = False
		predator_ob = None
	else:
		ROTATE_SPEED = 0.1
		if own.type == 'rat':
			RUN_SPEED = 0.05
		else:
			RUN_SPEED = 0.03
		
		TIME_LIMIT = 4.0
		ESCAPE = True
		predator_ob = [ob for ob in cont.getSensor('predator_sensor').getHitObjectList() if (hasattr(ob, 'life')==False or ob.life != 0)]
		if predator_ob:
			predator_ob = predator_ob[0]
		else:
			# EXIT ESCAPE STATE
			predator_ob = None
			
			GameLogic.addActiveActuator(cont.getActuator('walk_state'), 1)
	
	own_pos = Vector(own.getPosition())
	
	'''
	sens_l= cont.getSensor('RayLeft')
	sens_r = cont.getSensor('RayRight')
	sens_l_hitob = sens_l.getHitObject()
	sens_r_hitob = sens_r.getHitObject()	 
	'''
	
	# use python to get rays instead
	# ray should be 
	ray_pos = own_pos.copy()
	ray_pos[2] += 0.18 # cast the ray from slightly above, be sure they dont hit objects children
	
	
	# see objects "reference_only", these are the raydirections we are casting in python
	right_ray = Vector(own.getAxisVect([  0.41, 0.74, -0.53 ]))
	left_ray =  Vector(own.getAxisVect([ -0.41, 0.74, -0.53 ]))
	
	sens_l_hitob, lpos, lnor = own.rayCast(ray_pos + left_ray, ray_pos, 1.8)
	sens_r_hitob, rpos, rnor = own.rayCast(ray_pos + right_ray,  ray_pos, 1.8)
	
	# ob_ledge, hit_down, nor_down
	
	
	
	
	
	
	# If it has a barrier, respect it
	
	if sens_l_hitob and hasattr(sens_l_hitob, 'barrier') or hasattr(sens_l_hitob, 'water') or hasattr(sens_l_hitob, 'lava'):
		sens_l_hitob = None
		
	if sens_r_hitob and hasattr(sens_r_hitob, 'barrier') or hasattr(sens_r_hitob, 'water') or hasattr(sens_r_hitob, 'lava'):
		sens_r_hitob = None
		
	
	
	
	#if sens_l_hitob:
	#	print str(sens_l_hitob.name), 'hitob'
	
	
	
	# print 'TETS', type(sens_l_hitob), type(sens_r_hitob)
	
	
	# Check if we are running into frankie while he is reviving, if so turn away.
	# Do this because otherwise we keep running into frankie after hitting him.
	for ob in (sens_l_hitob, sens_r_hitob):
		if ob and hasattr(ob, 'predator') and hasattr(ob, 'revive_time') and ob.revive_time < 1.0:
			# would be nice to alternate but no big deal
			DIRECTION[0] = 1
			RUN_SPEED = 0.0
			
			# sets a too close value that is checked above
			# this means the sheep will turn for a while so it will never jitter
			own.target_time = -TURN_TIME
			break
	
	
	
	if own.target_time < 0.0:
		# Should this be a state rather then abusing a timer?
		# This is a bit of a hack. oh well :/
		# print 'ROTATING!', own.target_time
		DIRECTION[0] = 1
		RUN_SPEED = 0.0
	elif sens_l_hitob and sens_r_hitob:
		# print "BOTH OK"
		# Both collide, so do somtething
		####lpos =  sens_l.getHitPosition()
		ldist = own.getDistanceTo(lpos)
		####lnor = sens_l.getHitNormal()
		
		####rpos =  sens_r.getHitPosition()
		rdist = own.getDistanceTo(rpos)
		####rnor = sens_r.getHitNormal()
		
		# print ldist, rdist, 'DIST'
		
		# Not really an angle, but we can treat it a bit like one
		ang = ldist-rdist
		
		# Cheap trick, so flat surfaces give low angles
		# Maybe we should deal with flat surfaces differently
		# but we are really looking for walls, so flat'ish ground can be ignored.
		# 
		# zl and zr both have a range of -1.0 to 1.0, so if teh surface is totally flat,
		# the 'ang' will be unchanged
		# '''
		zl = lnor[2]
		zr = rnor[2]
		if zl < 0.0: lz = 0.0 
		if zr < 0.0: rz = 0.0 
		
		ang = ang * (2.0-(zl+zr))
		# '''
		# Done with cheap trick, remove if it causes problems
		
		
		
		# Do we need to agoid a wall?
		# IF we are really close to a corner we can get stuck and jitter
		# in this case just turn 1 way
		
		if ldist<TOO_CLOSE and rdist<TOO_CLOSE:
			# print "\tchar navigation: ray casts both too close", ldist, rdist
			# would be nice to alternate but no big deal
			DIRECTION[0] = 1
			RUN_SPEED = 0.0
			
			# sets a too close value that is checked above
			# this means the sheep will turn for a while so it will never jitter
			own.target_time = -TURN_TIME
			
		elif abs(ang) > WALL_LIMIT:
			#print "GO WALL"
			if ang < 0 or (ldist<TOO_CLOSE and rdist<TOO_CLOSE):
				DIRECTION[0] = 1
			else:
				DIRECTION[0] = 2
		else:
			# print "GO TARGET"
			go_target(own, cont, own_pos, predator_ob, TIME_LIMIT)
		
		if not (sens_l_hitob and sens_r_hitob):
			RUN_SPEED = 0.0

	elif (not sens_l_hitob) and (not sens_r_hitob):
		# We are on a ledge
		# print "EMPTY CLOSE" #, ldist, rdist
		# would be nice to alternate but no big deal
		DIRECTION[0] = 1
		RUN_SPEED = 0.0
		
		# sets a too close value that is checked above
		# this means the sheep will turn for a while so it will never jitter
		own.target_time = -TURN_TIME
		
	elif not sens_l_hitob or not sens_r_hitob:
		
		if abs(angle_target(own, cont, own_pos)) < 90 and own.target_time > TIME_LIMIT:
			reset_target(own, cont, own_pos, predator_ob)
		go_target(own, cont, own_pos, predator_ob, TIME_LIMIT)
		
		# Dont do anything
		RUN_SPEED = 0.0
	
	
	# Apply direction
	# print 'DIRECTION', DIRECTION, ldist, rdist
	if DIRECTION[0] == 0:
		# print 'NotTurning'
		actu_motion.setDRot(0,0,0,True)
		# GameLogic.addActiveActuator(actu_turn, 0)
	else:
		if DIRECTION[0] == 1:
			# print 'Turning Left'
			rot = -ROTATE_SPEED
		elif DIRECTION[0] == 2:
			# print 'Turning Right'
			rot = ROTATE_SPEED	
		actu_motion.setDRot(0,0,rot,True)
	
	# This is a bit weired, use negative z dloc to stick him to the ground.
	actu_motion.setDLoc(0,RUN_SPEED,-0.01,True)
	
	GameLogic.addActiveActuator(actu_motion, 1)
