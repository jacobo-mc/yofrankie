'''
This script triggers one off actions, kicking, throwing etc.


It is executed when an action key is pressed and no other actons have been set
or when the "action_name" property is set.

Each action has a TRIGGER_FRAME, which is the frame the function is run to perform the action.
for instance - when throwing, you dont want the object to be thrown right away.

Once the action is done the "action_name" property is cleared so other actions can be done.
'''
import GameLogic
from Mathutils import Vector, AngleBetweenVecs, CrossVecs


def side_of_other(own, other):
	'''
	What side of the sheep are we standing on? (2D function)
	'''
	relative_vec = Vector(own.getPosition())-Vector(other.getPosition())
	other_y_vec = Vector(other.getAxisVect( (0,1,0) ))
	relative_vec.z = other_y_vec.z = 0.0
	
	if CrossVecs(other_y_vec, relative_vec).z > 0:
		return True
	else:
		return False


def do_throw(cont, own):
	'''
	Throw objects in your inventory, object names are madeup from the property
	so you must make sure there is an object in a hidden layer that exists with this name.
	'''
	# Ok We can throw now,
	throw_item= own.throw_item
	if not throw_item:
		return # nothing to throw
	
	if not throw_item.startswith( 'item_' ):
		print '\twarning: throw item inavlid, must "item_" prefix -',throw_item
		own.throw_item = ''
		return
	
	throw_actu = cont.getActuator('throw_create')	
	
	try:
		throw_actu.setObject(throw_item)
	except:
		print '\twarning: could not find object to throw'
		print '\tmissing from scene. Add it to a background layer:', throw_item
		return
	
	
	# just aim ahead
	# we tried auto aim but it ended up not working well for moving objects
	own_y_throw = own.getAxisVect([0,8,0])
	own_y_throw[2] += 2.0
	
	throw_actu.instantAddObject()
	ob_throw = throw_actu.getLastCreatedObject()
	
	# Position the object since its at friankies middle
	# you can place the 3D cursor to double check these values
	ob_throw.setPosition( Vector(own.getPosition()) + Vector(own.getAxisVect([0.2, 0.422, 0.455])) )
	
	if hasattr(ob_throw, 'projectile_id'):
		ob_throw.projectile_id = own.id # so we dont let it his us.
	ob_throw.setLinearVelocity(own_y_throw)	
	

	# Decrement the number of items we have
	item_count = getattr(own, throw_item) - 1
	
	if item_count <= 0: # No Items? - Set to zero
		# own.throw_item = ''
		# Next available item
		propVal = 0
		for propName in own.getPropertyNames():
			if propName != throw_item and propName.startswith('item_'):
				propVal = getattr(own, propName)
				if propVal:
					own.throw_item = propName
					break
		
		# No Items Left
		if not propVal:
			own.throw_item = ''
		
		setattr(own, throw_item, 0)
	else: # Decrement
		setattr(own, throw_item, item_count)


def do_throw_carry(cont, own):
	'''
	Throw items your carrying ontop of your head
	'''
	
	ob_parent = cont.getSensor('carry_pos_linkonly').getOwner()
	
	try:
		own_carry = ob_parent.getChildren()[0]
	except:
		print 'frankie.carrying was set to 1 but was carry nothing. should never happen'
		print 'this is a bug'
		own.carrying = 0
		return
	
	own_carry.removeParent()
	own_carry.carried = 0
	own.carrying = 0
	
	
	# Tell the object we threw it. so we cant hurt ourselves.
	# Only add the property if this object has it to start with,
	# otherwise you could add when throwing a character which messes up
	# respawning properties works.
	if hasattr(own_carry, 'projectile_id'):
		own_carry.projectile_id = own.id
	
	own_y = own.getAxisVect([0,4,0])
	own_y[2] = 0.0
	own_carry.setLinearVelocity([own_y[0],own_y[1], 3], 0) # We are carrying sideways
	
	# Rotate forward, looks more natural
	if side_of_other(own, own_carry):	ang =  8
	else:								ang = -8
		
	own_carry.setAngularVelocity([0, ang, 0], 1) # We are carrying sideways
	
	# Notes 
	# * set upright while in the falling with interpolation or landing.
	# * dont need to turn the carry animation off, its done via a property check.
	

def kick_raytest(cont, own):
	'''
	p = own.getPosition()
	y = own.getAxisVect([0,1,0])	
	
	# just return the object
	return own.rayCastTo([p[0]+y[0],  p[1]+y[1],  p[2]+y[2]], 1.2, 'kickable')
	'''
	hit_ob = cont.getSensor('kick_radar').getHitObject()
	
	# Cant kick a dead enimy
	if hit_ob == None or (hasattr(hit_ob, 'life') and hit_ob.life <= 0):
		return None
	
	if hit_ob and own.getDistanceTo(hit_ob) > 0.7:
		return
	
	# Pitty but radar is buggy- test angle here
	ang = AngleBetweenVecs( \
		( Vector(own.getAxisVect([0,1,0])) ), \
		( Vector(hit_ob.getPosition()) - Vector(own.getPosition()) ) \
	)
	
	if ang > 33.0:	
		return None
	
	return hit_ob
	
	
def do_kick(cont, own):
	'''
	Kick anything infront of you
	'''
	
	ob_kick = kick_raytest(cont, own)
	
	if not ob_kick:
		return
	
	'''
	if hasattr(ob_kick, 'grounded') and not ob_kick.grounded:
		print 'cant kick airbourne objects'
		return
	'''
	
	if hasattr(ob_kick, 'carried') and ob_kick.carried:
		print '\tkick: cant kick object being carried'
		return
	
	
	kick_dir = Vector(ob_kick.getPosition()) - Vector(own.getPosition())
	
	
	# Tell the object we kicked it. so we cant hurt ourselves
	if hasattr(ob_kick, 'projectile_id'):
		ob_kick.projectile_id = own.id
	
	if hasattr(ob_kick, 'type'):
		ob_kick_type = ob_kick.type
	else:
		if hasattr(ob_kick, 'predator'):	
			ob_kick_type = 'frank'
		else:
			ob_kick_type = 'unknown'
	
	# print 'ObKick_Type', ob_kick_type
	
	if ob_kick_type == 'rat':
		# rats are like footballs
		'''
		kick_dir = own.getAxisVect([0,6,0])
		kick_dir[2] = 5
		ob_kick.setLinearVelocity(kick_dir, 0)
		'''
		# This is a bit nicer, use relative pos
		#  rather then franks direction above
		kick_dir.z = 0
		kick_dir.length = 3.0
		kick_dir.z = 4.0
		ob_kick.setLinearVelocity(kick_dir, 0)
		ob_kick.setAngularVelocity([0,-10, 0], 1) # We are carrying sideways
		
	elif ob_kick_type == 'shp':
		# We need to do some complicated crap to make sure they land on our head.
		kick_dir.z = 0
		kick_dir.negate()
		
		
		if own.carrying: # So we can kick a sheep into frankies arms
			kick_dir.length = 0.4
			kick_dir.z = 5.0 # we negate next line
		else:
			kick_dir.length = 0.8
			kick_dir.z = 4.0
			
		
		ob_kick.setLinearVelocity(kick_dir, 0)
		
		if side_of_other(own, ob_kick):	ang = -5
		else:							ang =  5
		ob_kick.setAngularVelocity([0, ang, 0], 1) # We are carrying sideways
	elif ob_kick_type == 'frank':
		# This is a bit nicer, use relative pos
		#  rather then franks direction above
		kick_dir.z = 0
		kick_dir.length = 2.0
		kick_dir.z = 6.0
		ob_kick.setLinearVelocity(kick_dir, 0)
		
		# dont really need this but nice not to always turn the same way
		if side_of_other(own, ob_kick):	ang_vel_z =  18
		else:							ang_vel_z = -18
		
		ob_kick.setAngularVelocity([0,0, 18], ang_vel_z) # We are carrying sideways
		ob_kick.hit = 1
		
	else:
		kick_dir.z = 0
		kick_dir.length = 0.5
		kick_dir.negate()
		kick_dir.z = 5.0
		ob_kick.setLinearVelocity(kick_dir, 0)
		
		# do nothing or rams? just play animations
		print 'unknown kick type...', ob_kick_type
		
		
	


def tailwhip_raytest(cont, own):
	'''
	p = own.getPosition()
	y = own.getAxisVect([0,1,0])	
	
	# just return the object, detect anything that can be hit.
	return own.rayCastTo([p[0]+y[0],  p[1]+y[1],  p[2]+y[2]], 2.0, 'hit')
	'''
	hit_ob = cont.getSensor('tailwhip_radar').getHitObject()
	
	if hit_ob and own.getDistanceTo(hit_ob) < 1.2:
		return hit_ob
	return None
	
def do_tailwhip(cont, own):
	'''
	Whip anything infront of you
	'''
	
	ob_whip = tailwhip_raytest(cont, own)
	
	if not ob_whip:
		return
	
	# Ok whip the other guy back
	whip_dir = own.getAxisVect([0,2.0, 0])
	whip_dir[2] = 1 # how high to whip
	ob_whip.setLinearVelocity(whip_dir, 0)
	
	
	# On second thaught. make landing hard the part that hurts.
	# Tell the object to be hit if it has a hit property
	if hasattr(ob_whip, 'hit'):
		ob_whip.hit = 1
		
		if hasattr(ob_whip, 'projectile_id'):
			ob_whip.projectile_id = own.id
		
		# Whip not used yet as an attack type ...
		'''
		if hasattr(ob_whip, 'attack_type'):
			ob_kick.attack_type = 'whip'
		else:
			print 'cant assign whip'
		'''
	else:
		print '\twarning: object cant be hurt when whipped:', ob_kick.name

def main(cont):
	own = cont.getOwner()
	
	# Keep this since debugging actions can get annoying, others may want to do it.
	DEBUG=False
	
	
	if DEBUG: print '###ATTEMPTING ACTION', own.carrying, own.action_name
	
	# Warning - This could be called by carry collider, special case- we need it to know what object were carrying
	# but dont want to do an action for every time it collides
	# Watch this case. should be ok for now.
	
	
	# Which keys are being pressed ? 
	# TRIGGER_FRAME - after this frame the function is called.
	action_name = own.action_name
	
	# Are we running an action? if not, check our keys
	action_init = 0
	do_action_function = None
	
	sens_throw = cont.getSensor('key_throw') 
	sens_kick = cont.getSensor('key_action')
	
	# Check triggered so holding the keys has no affect
	KEY_THROW = sens_throw.isPositive() and sens_throw.isTriggered()
	KEY_KICK = sens_kick.isPositive() and sens_kick.isTriggered()
	
	
	if KEY_THROW or KEY_KICK:
		# Dont do idle anims for a while
		GameLogic.addActiveActuator( cont.getActuator('idle_anim_disable'), True)
		
	
	if action_name == 'throw_carry' or (action_name=='' and KEY_THROW and own.carrying==1):
		do_action_function = do_throw_carry
		TRIGGER_FRAME = 14.0
		if action_name == '': # key triggered
			own.force_walk = -1.0
			own.action_name = action_name = 'throw_carry'
			action_init = 1
	elif action_name == 'throw' or (action_name=='' and KEY_THROW and own.carrying==0):
		do_action_function = do_throw
		TRIGGER_FRAME = 14.0
		if action_name == '': # key triggered
			# Can We Throw?
			if own.throw_item == '':
				if DEBUG: print '### NOTHING TO THROW, RET'
				return
			
			own.force_walk =  -1.0
			own.action_name = action_name = 'throw'
			action_init = 1
		
		# Tricky, be context sensative - if we cant kick anything. do tail whip!
	elif action_name == 'kick' or (action_name=='' and kick_raytest(cont, own) and KEY_KICK):
		
		if own.carried: # Cant carry and kick
			if DEBUG: print '### CANT CARRY and kick, RET'
			return
		
		# Ok, do kick
		do_action_function = do_kick
		TRIGGER_FRAME = 5.0
		if action_name == '': # key triggered
			own.force_walk =  -1.0
			own.action_name = action_name = 'kick'
			action_init = 1
		

	elif action_name == 'tailwhip' or (action_name=='' and KEY_KICK and own.carrying==0 and own.carried==0):
		
		# Ok, do tailwhip
		do_action_function = do_tailwhip
		TRIGGER_FRAME = 10.0
		if action_name == '': # key triggered
			own.force_walk =  -1.0
			own.action_name = action_name = 'tailwhip'
			action_init = 1
			
			# Special effect!
			if own.grounded:
				actu = cont.getActuator( 'add_fx_blast' )
				GameLogic.addActiveActuator( actu, True )
			
		
	# This shouldnt happen, but when it does there is nothing we can do.
	if action_name == '' or do_action_function == None:
		if DEBUG: print '###COULD NOT DO ACTION, RET'
		return
	
	# Are we initializeing? Dont do anything, we need the frame o be zero'd first
	
	if action_init == 1:
		own.action_done = 0
			
		for actu in cont.getActuators():
			try:
				actu.setFrame( actu.getStart() )
				GameLogic.addActiveActuator( actu, False )
			except:
				pass
		
		# Maybe there is a sound?
		try:
			actu = cont.getActuator( action_name + '_snd' )
			if DEBUG: print "ATTEMP TO PLAY SOUNT"
			GameLogic.addActiveActuator( actu, True )
			#GameLogic.addActiveActuator( actu, False)
		except:
			pass
		if DEBUG: print '###INIT ONLY, RET'
		return
	
	# print action_name
	actu_action = cont.getActuator(action_name) # action
		
	firstFrame = actu_action.getStart()
	lastFrame = actu_action.getEnd()
	curFrame = actu_action.getFrame()
	
	# We are at the start frame, play the animation!
	if firstFrame==curFrame:
		GameLogic.addActiveActuator( actu_action, True )
		return
	
	# Have we alredy thrown?, maybe we can exit this state
	if own.action_done == 1:
		if curFrame >= lastFrame-1: # EXIT THIS STATE		
			own.force_walk = 0.0 # disable
			own.action_done = 0
			own.action_name = ''
			GameLogic.addActiveActuator( actu_action, False )
			
			# Set the idle timer so we dont plane any idle animations for a while
			own.idle_anim_timer = -6.0
		

	
	elif curFrame > TRIGGER_FRAME:
		# Should we throw the object?
		do_action_function(cont, own)
		# Dont throw again
		own.action_done = 1