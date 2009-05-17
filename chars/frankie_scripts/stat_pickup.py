# Detect collision with pickup and act on this

import GameLogic

def main(cont):
	
	own = cont.getOwner()

	# Cant pickup when hurt
	print own.hit, own.revive_time
	if own.hit or own.revive_time < 1.0 or own.carrying or own.carried:
		print "Cant collect items when hit, reviving, carrying or carried"
		return 
	
	sens_pickup = cont.getSensor('pickup_touch')
	
	pickup_objects = sens_pickup.getHitObjectList()
	
	if not pickup_objects or len(pickup_objects) == 0: 
		return
	
	DONE_PICKUP = False
	LIFE_PICKUP = False
	
	# Loop over all colliding pickup onjects
	for pickup in pickup_objects:
		# We can either pickup an item or get life!
		
		if hasattr(pickup, 'life'): # LIFE PICKUP
			# Play Flash Anim!
			life_max = own.life_max
			life = own.life + pickup.life
			if life < life_max:
				# Life, we have enough
				own.life = life
			else:
				own.life = own.life_max
				
			GameLogic.frankhealth = own.life	
			GameLogic.addActiveActuator( cont.getActuator('pickup_flash_life'), True )
			GameLogic.addActiveActuator( cont.getActuator("send_healthchange"), True )
			DONE_PICKUP = LIFE_PICKUP = True
			
			
		elif hasattr(pickup, 'boost'): # BOOST PICKUP
			# now youll run faster etc
			# The value for boost is ignored
			own.boosted = -10.0 # As long is its under 0, boost will apply
			DONE_PICKUP = True
			
		else: # ITEM PICKUP
			item_attr = pickup.pickup
			
			if not item_attr.startswith('item_'):
				print 'Incorrect name', own, item_attr
			else:
				if hasattr(own, item_attr):
					own_value = getattr( own, item_attr )
					setattr( own, item_attr, own_value + 1 )
				else:
					setattr( own, item_attr, 1 )
				
				# Should be smarter here, for now just set the thor item to this one.
				own.throw_item = item_attr
				DONE_PICKUP = True
				
				
		# May pickup multiple objects at once.
		pickup.endObject() # delayed removes this object from the scene

	# Play pickup animation only if walking and on the ground.
	if DONE_PICKUP:
		# WARNING - test with getState() assumes running 
		# is on state 3, Id prefer not to use these kinds of tests
		# since running could be moved from state 3 but for now its ok.
		if own.grounded != 0 and not (cont.getState() & (1<<2)):
			GameLogic.addActiveActuator( cont.getActuator('pickup_anim'), True )
		if LIFE_PICKUP:
			GameLogic.addActiveActuator( cont.getActuator('sfx_life_pickup'), True )			
			hud_dict = GameLogic.globalDict['HUD']
			if own.id == 0:	hud_dict['life_p1'] = own.life
			else:			hud_dict['life_p2'] = own.life
			GameLogic.addActiveActuator( cont.getActuator('send_healthchange'), True )
		else:
			GameLogic.addActiveActuator( cont.getActuator('sfx_item_pickup'), True )		
	