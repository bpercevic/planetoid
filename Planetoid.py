"""
TITLE:	untitled
GENRE:	space-shooter

BY:		dan, bojan
"""

import math, os, pygame, random, time, sys
from pygame.locals import *

# SCREENRECT = Rect(0,0,800,600)
SCREENRECT = Rect(0,0,1280,800)


#CONSTANT AND NONCONSTANT VARIABLES
global lives, astros, level, shots, score, astros_killed, plusminus, gainedlost, status
global firerate, bg_music_volume, shot_vol, game_images, screensize, shot_sound
global pause_music, game_images2, game_song, game_title, get_astronaut, get_collect
global explode_clip, astro_die_clip, bam, asteroid_count, game_intro, num_asteroids_killed, shipspeed, go_clip, intro_song, hud_pic
global intro_song_vol, intro_speak, low_health_beep, collide_clip
lives = 100
astros = 0
level = 1
ammo_amt = 1500
score = 0
astros_killed = 0
plusminus = ""
gainedlost = ""
status = ""
firerate = "/"
hud_pic = "hud3.bmp"
game_images = "glass.bmp"
game_images2 = "explosion.bmp"
game_intro = "intro.bmp"
screensize = 800,600
game_song = "fire.mp3"
game_title = "PLANETOID"
bg_music_volume = 0.9
get_astronaut = "get.wav"
# get_collect = "shipintegrity.wav"
get_ammo_clip = "get.wav"
get_heart_clip = "get.wav"
explode_clip = "kill_naut.wav"
astro_die_clip = ["kill_naut.wav"]
shot_sound = "shot3.wav"
shot_vol = 0.75
pause_music = "elevator.wav"
go_clip = "gameover.wav"
bam = ""
asteroid_count = 0
num_asteroids_killed = 0
shipspeed = 150
intro_song = "introsong.wav"
intro_song_vol = .15
intro_speak = "welcomeback.wav"
low_health_beep = "lowhealth.wav"
collide_clip = "explode.wav"

def set_firerate(what):
	global firerate
	if what == "|":
		firerate = "/"
	elif what == "||":
		firerate = "//"
	elif what == "|||":
		firerate = "///"
	elif what == "||||":
		firerate = "////"			

def set_status(what):
	global status
	if what == "ship-aster":
		status = "ship integrity -5%"
	elif what == "ship-astro":
		status = "savior"
	elif what == "ship-heart":
		global lives
		if lives == 100:
			status = "ship integrity max"
		else:
			status = "ship integrity +5%"
	elif what == "ship-ammo":
		status = "ammunition +10"
	elif what == "shot-aster":
		status = "planetoid funk-a-dunk!"
	elif what == "shot-astro":
		status = "butcher"
	elif what == "shot-heart":
		status = "resource waster"
	elif what == "shot-ammo":
		status = "resource waster"
	elif what == "obliterate":
		if asteroid_count == 1:
			status = str(asteroid_count)+" planetoid crushed"
		else:
			status = str(asteroid_count)+" planetoids crushed"
	elif what == "gameover":
		status = "ship integrity compromised"
	elif what == "shot-big-aster":
		status = "mega planetoid"
	elif what == "ship-big-aster":
		status = "get out of the way"
	elif what == "ship-m_ship":
		status = "get out of the way"
	elif what == "shot-m_ship":
		status = "mega ship"		

"""
Spritesheets can hold multiple sprites for different objects
This makes it easier to load slices of the sheet and assign the
slice to an object in the game
"""		
class Spritesheet:
	def __init__(self, filename):
		self.sheet = pygame.image.load(os.path.join('data', filename)).convert()
	def imgat(self, rect, colorkey = None):
		rect = Rect(rect)
		image = pygame.Surface(rect.size).convert()
		image.blit(self.sheet, (0,0), rect)
		if colorkey is not None:							#colorkey is the color that will be filtered
			if colorkey is -1:								#from a sprite and made transparent
				colorkey = image.get_at((0,0))				#this assigns colorkey to the top-left pixel
			image.set_colorkey(colorkey, RLEACCEL)			#which is usually part of the background
		return image
	def imgsat(self, rects, colorkey = None):
		imgs = []
		for rect in rects:
			imgs.append(self.imgat(rect, colorkey))
		return imgs
		
#Arena is a rectangle in the game window that will display all our game objects 
class Arena:
    #lower probability number increases the amount of objects
    m_ships_probability = 2000
    big_asteroid_L_probability = 500
    big_asteroid_R_probability = 500
    asteroid_L_probability = 12
    asteroid_R_probability = 12
    asteroid_T_probability = 12
    astronaut_L_probability = 500
    astronaut_R_probability = 500
    ammo_probability = 900
    hearts_probability = 900
    speed = 10		#controls the speed of the scrolling of the background
    def __init__(self, asteroids, num_astros, shots, ammo, hearts, big_asteroids, m_ships):
        w = SCREENRECT.width
        h = SCREENRECT.height
        self.tileside = self.tile.get_height()	#tileside is the length of one side of the tile
        self.counter = 0
        self.floor = pygame.Surface((w, h + self.tileside)).convert()
        for x in range(w/self.tileside):											#tiles left-to-right
            for y in range(h/self.tileside + 1):									#tiles top-to-bottom
                self.floor.blit(self.tile, (x*self.tileside, y*self.tileside))		#draw the tiles
        self.asteroids = asteroids
        self.num_astros = num_astros
        self.shots = shots
        self.ammo = ammo
        self.hearts = hearts
        self.big_asteroids = big_asteroids
        self.m_ships = m_ships
        self.boom = 0
        self.number_of_shots = 0
    def offset(self):													#this is what controls the animated scrolling 
        self.counter = (self.counter - self.speed) % self.tileside		#of the background, counter is a changing variable
        return (0, self.counter, SCREENRECT.width, SCREENRECT.height)	#which in turn changes the position of the background
    def update(self):													#which creates the illusion of a moving background
    	#maintain the probability of objects being created on the screen
        if not random.randrange(self.astronaut_L_probability):
        	Astronaut()
        if not random.randrange(self.astronaut_R_probability):	
        	Astronaut2()
        if not random.randrange(self.asteroid_T_probability):
            AsteroidT()
        if not random.randrange(self.asteroid_L_probability):    
            AsteroidL()
        if not random.randrange(self.asteroid_R_probability):
        	AsteroidR()    
        if not random.randrange(self.ammo_probability):
        	Ammunition()
        if not random.randrange(self.hearts_probability):
        	Heart()	
        if not random.randrange(self.big_asteroid_L_probability):
        	BigAsteroidL()		
        if not random.randrange(self.big_asteroid_R_probability):
        	BigAsteroidR()
        if not random.randrange(self.m_ships_probability):
        	Motherships()		
        #collisions and point system	
        for asteroid in pygame.sprite.groupcollide(self.shots, self.asteroids, 1, 1):
        	global score, plusminus, gainedlost, status, num_asteroids_killed
        	set_status("shot-aster")
        	score += 1000
        	plusminus = "+"
        	gainedlost = 1000
        	num_asteroids_killed += 1
        	explode()
        	Explosion(asteroid)
        for astronauts in pygame.sprite.groupcollide(self.shots, self.num_astros, 1, 1):
        	global score, astros_killed, plusminus, gainedlost, status
        	set_status("shot-astro")
        	score -= 3000
        	plusminus = "-"
        	astros_killed += 1
        	gainedlost = 3000
        	astroDie()
        	Explosion(astronauts)
        for ammunitions in pygame.sprite.groupcollide(self.shots, self.ammo, 1, 1):
        	global plusminus, score, gainedlost, status
        	set_status("shot-ammo")
        	plusminus = "-"
        	score -= 50
        	gainedlost = 50
        	explode()
        	Explosion(ammunitions)
        for hearts in pygame.sprite.groupcollide(self.shots, self.hearts, 1, 1):
        	global plusminus, score, gainedlost, status
        	set_status("shot-heart")
        	plusminus = "-"
        	score -= 50
        	gainedlost = 50
        	explode()
        	Explosion(hearts)
# 		global does_it_explode, number_of_shots
		self.boom = 0	
# 		self.number_of_shots = 0
        for big_asteroid in pygame.sprite.groupcollide(self.big_asteroids, self.shots, 0, 1):
        	global score, plusminus, gainedlost, status
        	set_status("shot-big-aster")
        	score += 10000
        	plusminus = "+"
        	gainedlost = 10000
        	big_asteroid.life -= 1
 #        	if big_asteroid.life < 1:
#         		self.boom = 1
#         	if big_asteroid.life == 0:
#         		big_asteroid.life = 5
#         	self.number_of_shots += 1
#         	if self.number_of_shots == 4:
#         		pygame.sprite.spritecollide(self.shots, self.big_asteroids, 1)
#     			self.boom = 1
#     			explode()
#     			self.boom = 0
#     			self.number_of_shots = 0
# #         		
# 			if self.number_of_shots == 4:
#         		self.boom = 1
# 				self.number_of_shots = 0
# 				self.boom = 0
# 				explode()
# 				Explosion(big_asteroid)
# 				for big_asteroid in pygame.sprite.groupcollide(self.shots, self.big_asteroids, 1, 1)
# 					pass
# 				big_asteroid.kill()
        for m_ship in pygame.sprite.groupcollide(self.shots, self.m_ships, 1, 0):
        	global score, plusminus, gainedlost, status
        	set_status("shot-m_ship")
        	score += 100000
        	plusminus = "+"
        	gainedlost = 100000
        for m_ship in pygame.sprite.groupcollide(self.m_ships, self.m_ships, 0, 0)  :
        	pass	

#the sound an exploding asteroid makes
def explode():
	expsound = pygame.mixer.Sound(os.path.join('data', explode_clip))
	expsound.set_volume(1)
	expsound.play(0)
	
def collide():
	expsound = pygame.mixer.Sound(os.path.join('data', collide_clip))
	expsound.set_volume(1)
	expsound.play(0)	
	
#the sound an astronaut makes when you shoot him	
def astroDie():
	die = pygame.mixer.Sound(os.path.join('data', random.choice(astro_die_clip)))
	die.play(0)
			
			
class Ship(pygame.sprite.Sprite):
	guns = [(23,1)]		#the location of the gun on the ship
	def __init__(self, arena, asteroids, ships, num_astros, ammo, hearts, big_asteroids, m_ships):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect()				#self.image will be given a value later in the main()
		self.arena = arena
		self.asteroids = asteroids
		self.ship = ships
		self.num_astros = num_astros
		self.ammo = ammo
		self.hearts = hearts
		self.big_asteroids = big_asteroids
		self.m_ships = m_ships
		self.rect.centerx = SCREENRECT.centerx
		self.rect.bottom = SCREENRECT.bottom+15
		self.vx = 0										#velocity on x	
		self.vy = 0										#velocity on y
	def update(self):
		self.rect.clamp_ip(SCREENRECT)					#lock the object to the Arena
		self.rect.move_ip((self.vx, self.vy))			#move_ip is a function that moves the object around the screen		
		self.arena.update()								#this update needs to be there so that pygame will draw the other objects on the screen
		#reverse velocities if the ship hits the sides of the arena
		if self.rect.top == SCREENRECT.top:
			self.vy = 1
# 			self.arena.speed += 10
		if self.rect.bottom == SCREENRECT.bottom:
			self.vy = -1
# 			self.arena.speed += 10
		if self.rect.left == SCREENRECT.left:
			self.vx = 1
		if self.rect.right == SCREENRECT.right:
			self.vx = -1
		#check for collisions with other objects and act accordingly
		if pygame.sprite.spritecollide(self, self.big_asteroids, 0):
			if level != "go":
				global lives, score, plusminus, gainedlost, status
				set_status("ship-big-aster")
				score -= 100
				plusminus = "-"
				rating = "attention"
				gainedlost = 100
				lives -= 1
			else:
				pass
		if pygame.sprite.spritecollide(self, self.asteroids, 1):
			#level "go" stands for gameover
			if level != "go":
				global lives, score, plusminus, gainedlost, status, num_asteroids_killed
				set_status("ship-aster")
				lives -= 5
				score -= 500
				plusminus = "-"
				gainedlost = 500
				num_asteroids_killed += 1
				collide()
			else:
				pass	
		if pygame.sprite.spritecollide(self, self.num_astros, 1):
			if level != "go":
				global astros, score, plusminus, gainedlost, status
				set_status("ship-astro")
				astros += 1
				score += 3000
				plusminus = "+"
				gainedlost = 3000
				getAstro()
			else:
				pass
		if pygame.sprite.spritecollide(self, self.ammo, 1):
			if level != "go":
				global ammo_amt, score, plusminus, gainedlost, status
				set_status("ship-ammo")
				ammo_amt += 10
				score += 500
				plusminus = "+"
				gainedlost = 500
				getAmmo()
			else:
				pass
		if pygame.sprite.spritecollide(self, self.hearts, 1):
			if level != "go":
				global lives, score, plusminus, gainedlost, status
				set_status("ship-heart")
				lives += 10
				score += 500
				plusminus = "+"
				gainedlost = 500
				getHeart()
			else:
				pass
		if pygame.sprite.spritecollide(self, self.m_ships, 0):
			if level != "go":
				global lives, score, plusminus, gainedlost, status
				set_status("ship-m_ship")
				score -= 100
				plusminus = "-"
				rating = "attention"
				gainedlost = 100
				lives -= 1
			else:
				pass					

#the sound made from collecting an astronaut
def getAstro():
	get_astro = pygame.mixer.Sound(os.path.join('data', get_astronaut))
 	get_astro.set_volume(.75)
	get_astro.play(0)
	
#the sound made from collecting a heart
def getHeart():
	get_heart = pygame.mixer.Sound(os.path.join('data', get_heart_clip))
 	get_heart.set_volume(.75)
	get_heart.play(0)	
	
#the sound made from collecting ammunition	
def getAmmo():
	get_ammo = pygame.mixer.Sound(os.path.join('data', get_ammo_clip))
	get_ammo.set_volume(.75)
	get_ammo.play(0)
	
def play_game_over():
	go_sound = pygame.mixer.Sound(os.path.join('data', go_clip))
	go_sound.set_volume(1)
	go_sound.play(0)		
	

class Shot(pygame.sprite.Sprite):
    speed = 9
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        self.rect.move_ip(0, -self.speed)
        if self.rect.top < 0:
            self.kill()

class Motherships(pygame.sprite.Sprite):
    animcycle = 4
    speed = 1
    life = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.imagesets)
        self.image = random.choice(self.images)
        self.counter = 0
#         self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)		#this creates a random starting location on the screen
        self.rect.bottom = SCREENRECT.top
    def update(self):
        self.rect.move_ip(0, self.speed)
#         self.counter = (self.counter + 1) % self.maxcount
        if self.rect.top > SCREENRECT.bottom:
        	self.kill()

class BigAsteroidL(pygame.sprite.Sprite):
    animcycle = 4
    speeds = [1,2,3,4,5,6,7,8,9,10]
    speed = random.choice(speeds)
    life = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.imagesets)
        self.image = random.choice(self.images)
        self.counter = 0
        self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)		#this creates a random starting location on the screen
        self.rect.bottom = SCREENRECT.top
        self.life = 5
    def update(self):
        self.rect.move_ip(0, self.speed)
        self.counter = (self.counter + 1) % self.maxcount
        if self.rect.top > SCREENRECT.bottom:
        	self.kill()
        	
class BigAsteroidR(pygame.sprite.Sprite):
    animcycle = 4
    speeds = [1,2,3,4,5,6,7,8,9,10]
    speed = random.choice(speeds)
    life = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.imagesets)
        self.image = random.choice(self.images)
        self.counter = 0
        self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)		#this creates a random starting location on the screen
        self.rect.bottom = SCREENRECT.top
        self.life = 5
    def update(self):
        self.rect.move_ip(0, self.speed)
        self.counter = (self.counter + 1) % self.maxcount
        if self.rect.top > SCREENRECT.bottom:
        	self.kill()        	

#the asteroids coming from the top of the screen
class AsteroidT(pygame.sprite.Sprite):
    animcycle = 4
    speed = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.imagesets)
        self.image = random.choice(self.images)
        self.counter = 0
        self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)		#this creates a random starting location on the screen
        self.rect.bottom = SCREENRECT.top
    def update(self):
        self.rect.move_ip(-1, self.speed)
        self.counter = (self.counter + 1) % self.maxcount
        if self.rect.top > SCREENRECT.bottom:
        	self.kill()
#         self.image = self.images[self.counter/self.animcycle]		#this can create an animation in the asteroids

#the asteroids coming from the left of the screen
class AsteroidL(pygame.sprite.Sprite):
    animcycle = 4
    speed = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.imagesets)
        self.image = random.choice(self.images)
        self.counter = 0
        self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)
        self.rect.bottom = SCREENRECT.top
    def update(self):
        self.rect.move_ip(1, self.speed)
        self.counter = (self.counter + 1) % self.maxcount
        if self.rect.top > SCREENRECT.bottom:
        	self.kill()
#         self.image = self.images[self.counter/self.animcycle]		#this can create an animation in the asteroids
        	
#the asteroids coming from the right of the screen
class AsteroidR(pygame.sprite.Sprite):
    animcycle = 4
    speed = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.imagesets)
        self.image = random.choice(self.images)
        self.counter = 0
        self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)
        self.rect.bottom = SCREENRECT.top
    def update(self):
        self.rect.move_ip(0, self.speed)
        self.counter = (self.counter + 1) % self.maxcount
        if self.rect.top > SCREENRECT.bottom:
        	self.kill()
#         self.image = self.images[self.counter/self.animcycle]		#this can create an animation in the asteroids
            
#the astronauts floating in from the left            
class Astronaut(pygame.sprite.Sprite):
	animcycle = 6
	speed = 3
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.images = random.choice(self.imagesets)
		self.image = random.choice(self.images)
		self.counter = 0
		self.maxcount = len(self.images)*self.animcycle
		self.rect = self.image.get_rect()
		self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)
		self.rect.top = SCREENRECT.top
	def update(self):
		self.rect.move_ip(1, self.speed)
		self.counter = (self.counter + 1) % self.maxcount
		
#the astronauts floating in from the right		
class Astronaut2(pygame.sprite.Sprite):
	animcycle = 6
	speed = 3
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.images = random.choice(self.imagesets)
		self.image = random.choice(self.images)
		self.counter = 0
		self.maxcount = len(self.images)*self.animcycle
		self.rect = self.image.get_rect()
		self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)
		self.rect.top = SCREENRECT.top
	def update(self):
		self.rect.move_ip(-1, self.speed)
		self.counter = (self.counter + 1) % self.maxcount		
					
class Ammunition(pygame.sprite.Sprite):
	animcycle = 6
	speed = 2
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.counter = 0
		self.maxcount = 10*self.animcycle
		self.rect = self.image.get_rect()
		self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)
		self.rect.top = SCREENRECT.top
	def update(self):
		self.rect.move_ip(-1, self.speed)
		self.counter = (self.counter + 1) % self.maxcount
		
class Heart(pygame.sprite.Sprite):
	animcycle = 6
	speed = 2
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.counter = 0
		self.maxcount = 10*self.animcycle
		self.rect = self.image.get_rect()
		self.rect.left = random.randrange(SCREENRECT.width - self.rect.width)
		self.rect.top = SCREENRECT.top
	def update(self):
		self.rect.move_ip(-1, self.speed)
		self.counter = (self.counter + 1) % self.maxcount 
		
# #this is the explosion animation that is created in place of the destroyed asteroid		
class Explosion(pygame.sprite.Sprite):
    animcycle = 4
    def __init__(self, asteroid):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.counter = 0
        self.maxcount = len(self.images)*self.animcycle
        self.rect = self.image.get_rect()
        self.rect.center = asteroid.rect.center
        self.asteroid = asteroid
    def update(self):
    	self.rect.move_ip((0, -self.asteroid.speed/2))
        self.image = self.images[self.counter/self.animcycle]
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()	

	
def pause():
	loop = 1
	pygame.mixer.music.pause()
	elemusic = pygame.mixer.Sound(os.path.join('data', pause_music))
	elemusic.set_volume(.25)
	elemusic.play(-1)
	while loop:
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_p:
					pygame.mixer.music.unpause()
					loop = 0
				elif event.type == QUIT or (event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
	pygame.mixer.stop()					
				
def start_game():
	loop = 1
	while loop:
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_RETURN:
					loop = 0
				elif event.type == QUIT or (event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()				

def game_wait():
	loop = 1
	while loop:
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key:
					loop = 0
	
				
def game_quit():
	loop = 1
	while loop:
		time.sleep(.15)
		pygame.quit()
		sys.exit()
		
def play_introsong(playit):
	intro_sound = pygame.mixer.Sound(os.path.join('data', intro_song))
	if playit == "play":
		intro_sound.play(-1)
	elif playit == "stop":
		intro_sound.stop()
					

# #HANDLE INPUT
# def handle_input():
# 	for event in pygame.event.get():
# 		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
# 			pygame.quit()
# 			sys.exit()
# 			
# 			#HOW GAMEOVER WORKS WITH CONTROLS:
# 			#	if level != "go" aka GAMEOVER:
# 			#		then allow for things to happen
# 			#	else if level == "go":
# 			#		dont allow any control of ship and other stuf
# 			
# 		#WHAT HAPPENS WHEN YOU PRESS CERTAIN KEYS	
# 		if event.type == KEYDOWN:
# 		
# 			#SPACE SHIP MOVEMENT	
# 			if event.key == K_UP:
# 				if level != "go":
# 					arena.speed += 5
# 					BigAsteroidL.speed += 3
# 					BigAsteroidR.speed += 3
# 					AsteroidT.speed += 3
# 					AsteroidL.speed += 3
# 					AsteroidR.speed += 3
# 					Astronaut.speed += 3
# 					Astronaut2.speed += 3
# 					Heart.speed += 3
# 					Ammunition.speed += 3					
# 					Ship.image = spritesheet.imgat((167, 193, 47, 50), -1)
# 					ship.vy = -4
# 					shipspeed = 250
# 				elif level == "go":
# 					pass
# 			elif event.key == K_DOWN:
# 				if level != "go":
# 					arena.speed -= 2
# # 						arena.speed = -arena.speed
# 					BigAsteroidL.speed -= 1
# 					BigAsteroidR.speed -= 1					
# 					AsteroidT.speed -= 1
# 					AsteroidL.speed -= 1
# 					AsteroidR.speed -= 1
# 					Astronaut.speed -= 1
# 					Astronaut2.speed -= 1
# 					Heart.speed -= 1
# 					Ammunition.speed -= 1															
# 					Ship.image = spritesheet.imgat((167, 246, 47, 50), -1)
# 					ship.vy = +4
# 					shipspeed = 50
# 				elif level == "go":
# 					pass							
# 			elif event.key == K_LEFT:
# 				if level != "go":
# 					Ship.image = spritesheet.imgat((220, 246, 32, 50), -1)
# 					ship.vx = -4
# 				elif level == "go":
# 					pass							
# 			elif event.key == K_RIGHT:
# 				if level != "go":
# 					Ship.image = spritesheet.imgat((220, 193, 32, 50), -1)
# 					ship.vx = +4
# 				elif level == "go":
# 					pass
# 					
# 			#SHOOT								
# 			elif event.key == K_SPACE:
# 				if level != "go":
# 					if ammo_amt > 0:
# 						shotsound = pygame.mixer.Sound(os.path.join('data', shot_sound))
# 						shotsound.set_volume(shot_vol)
# 						shotsound.play(0)
# 						for gun in ship.guns:
# 							Shot((ship.rect.left+gun[0], ship.rect.top+gun[1]))
# 							ammo_amt -= 1
# 				elif level == "go":
# 					pass
# 			
# 			#PAUSE GAME
# 			elif event.key == K_p:
# 				if level != "go":
# 					screen.blit(game_pause, (200, SCREENRECT.centery-150))
# 					screen.blit(game_pause_caption, (SCREENRECT.centerx-455, SCREENRECT.centery+45))
# 					pygame.display.update()
# 					pause()
# 				elif level == "go":
# 					pass
# 					
# 			#FIRING RATE 1-4		
# 			elif event.key == K_1:
# 				if level != "go":
# 					ship.guns = [(23,1)]
# 					set_firerate("|")
# 				elif level == "go":
# 					pass	
# 			elif event.key == K_2:
# 				if level != "go":
# 					ship.guns = [(15,1), (31,1)]
# 					set_firerate("||")
# 				elif level == "go":
# 					pass	
# 			elif event.key == K_3:
# 				if level != "go":
# 					ship.guns = [(0,1), (23,1), (46,1)]
# 					set_firerate("|||")
# 				elif level == "go":
# 					pass	
# 			elif event.key == K_4:
# 				if level != "go":
# 					ship.guns = [(-15,1), (10,1), (33,1), (56,1)]
# 					set_firerate("||||")
# 				elif level == "go":
# 					pass	
# 					
# 			#KILL-ALL BUTTON		
# 			elif event.key == K_RSHIFT or event.key == K_LSHIFT:
# 				if level != "go":
# 					global asteroid_count
# 					if ammo_amt > 1:
# 						for asteroid in asteroids:
# 							asteroid_count += 1
# 							Explosion(asteroid)	
# 							asteroid.kill()	
# 							global score, plusminus, gainedlost, num_asteroids_killed
# 							score += 10000
# 							plusminus = "+"
# 							gainedlost = 10000	
# 							num_asteroids_killed += 1							
# 						explode()
# 						ammo_amt -= asteroid_count
# 						set_status("obliterate")
# 						asteroid_count = 0
# 				elif level == "go":
# 					pass											
# 					
# 		#WHAT HAPPENS WHEN YOU RELEASE CERTAIN KEYS			
# 		elif event.type == KEYUP:	
# 			if event.key == K_UP:
# 				if level != "go":
# 					arena.speed -= 5
# 					BigAsteroidL.speed -= 3
# 					BigAsteroidR.speed -= 3					
# 					AsteroidT.speed -= 3
# 					AsteroidL.speed -= 3
# 					AsteroidR.speed -= 3
# 					Astronaut.speed -= 3
# 					Astronaut2.speed -= 3
# 					Heart.speed -= 3
# 					Ammunition.speed -= 3					
# 					Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
# 					ship.vy = -1
# 					shipspeed = 150
# 				elif level == "go":
# 					pass
# 			elif event.key == K_DOWN:
# 				if level != "go":
# 					arena.speed += 2
# # 						arena.speed = -arena.speed
# 					BigAsteroidL.speed += 1
# 					BigAsteroidR.speed += 1					
# 					AsteroidT.speed += 1
# 					AsteroidL.speed += 1
# 					AsteroidR.speed += 1
# 					Astronaut.speed += 1
# 					Astronaut2.speed += 1
# 					Heart.speed += 1
# 					Ammunition.speed += 1					
# 					Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
# 					ship.vy = 1
# 					shipspeed = 150
# 				elif level == "go":
# 					pass
# 			elif event.key == K_LEFT:
# 				if level != "go":
# 					Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
# 					ship.vx = -1
# 				elif level == "go":
# 					pass
# 			elif event.key == K_RIGHT:
# 				if level != "go":
# 					Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
# 					ship.vx = 1
# 				elif level == "go":
# 					pass
# 			elif event.key == K_RSHIFT or event.key == K_LSHIFT:
# 				pass











		
		
def main():
	#INITIALIZE
	pygame.init()
	screen = pygame.display.set_mode(SCREENRECT.size)#, FULLSCREEN | DOUBLEBUF)
# 	screen = pygame.display.set_mode(SCREENRECT.size, HWSURFACE | DOUBLEBUF | FULLSCREEN)

	pygame.display.set_caption(game_title)
	clock = pygame.time.Clock()
	clock2 = pygame.time.Clock()
	pygame.mixer.music.load(os.path.join('data', game_song))
	pygame.mixer.music.set_volume(bg_music_volume)
	
	#FONT SETUP	
	stats = pygame.font.Font(None, 18)
	biggest = pygame.font.Font(None, 300)
	bigger = pygame.font.Font(None, 200)
	big = pygame.font.Font(None, 160)
	small = pygame.font.Font(None, 50)
	smaller = pygame.font.Font(None, 35)
	smallest = pygame.font.Font(None, 20)				
	scorefont = pygame.font.Font(None, 50)
	statusfont = pygame.font.Font(None, 20)
	gainlostfont = pygame.font.Font(None, 50)
	hundred = pygame.font.Font(None, 50)
	fatalerror = pygame.font.Font(None, 240)
	integrity = pygame.font.Font(None, 40)
	
	#SPRITES SETUP
	spritesheet = Spritesheet(game_images)
	explodeimgs = Spritesheet(game_images2)
	introsheet = Spritesheet(game_intro)
	mothersprite = Spritesheet('motherships.bmp')
	errorsheet = Spritesheet('error.bmp')
	game_hud = Spritesheet(hud_pic)
	arenatile = Spritesheet('arena.bmp')
	Arena.tile = arenatile.imgat((0,0,256,256))	
	Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
	Shot.image = spritesheet.imgat((193, 81, 15, 15), -1)	
	Ammunition.image = spritesheet.imgat((97, 161, 22,13), -1)
	Heart.image = spritesheet.imgat((129, 129, 17, 17), -1)
# 	Motherships.image = mothersprite.imgat((0,0,240,900), -1)
	Motherships.imagesets = [
		mothersprite.imgsat([(0,0,240,900), (250,0,241,1150), (0,0,240,900), (250,0,241,1150),], -1),
		mothersprite.imgsat([(0,0,240,900), (250,0,241,1150), (0,0,240,900), (250,0,241,1150),], -1),
		mothersprite.imgsat([(0,0,240,900), (250,0,241,1150), (0,0,240,900), (250,0,241,1150),], -1)
		]
	BigAsteroidL.imagesets = [
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200)], -1),
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200)], -1),
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200)], -1),
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200), (321,81,200,200)], -1)
		]
	BigAsteroidR.imagesets = [
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200)], -1),
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200)], -1),
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200)], -1),
		spritesheet.imgsat([(321,81,200,200), (321,81,200,200), (321,81,200,200), (321,81,200,200)], -1)
		]				
	AsteroidT.imagesets = [
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1)
		]
	AsteroidL.imagesets = [
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1)
		]
	AsteroidR.imagesets = [
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(1,65,31,31), (33,65,31,31), (65,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(97,65,31,31), (129,65,31,31), (161,65,31,31)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1),
		spritesheet.imgsat([(193,65,15,15), (225,65,15,15), (257,65,15,15), (289,65,15,15)], -1)
		]				
	Astronaut.imagesets = [ #new 26x31
		spritesheet.imgsat([(1,129,25,31), (33,129,25,31), (65,129,31,25), (97,129,31,25)], -1),
		spritesheet.imgsat([(1,129,25,31), (97,129,31,25), (33,129,25,31), (65,129,31,25)], -1),
		spritesheet.imgsat([(1,129,25,31), (33,129,25,31), (65,129,31,25), (97,129,31,25)], -1)
		]
	Astronaut2.imagesets = [
		spritesheet.imgsat([(1,129,25,31), (33,129,25,31), (65,129,31,25), (97,129,31,25)], -1),
		spritesheet.imgsat([(1,129,25,31), (97,129,31,25), (33,129,25,31), (65,129,31,25)], -1),
		spritesheet.imgsat([(1,129,25,31), (33,129,25,31), (65,129,31,25), (97,129,31,25)], -1)
		]
	Explosion.images = explodeimgs.imgsat([(70, 169, 32, 32), (103, 169, 32, 32), (136, 169, 32, 32), (169, 169, 32, 32), (202, 169, 32, 32), (235, 169, 32, 32)], -1)	
	
		
	#GROUP OBJECTS	
	m_ships = pygame.sprite.Group()
	shots = pygame.sprite.Group()
	asteroids = pygame.sprite.Group()
	big_asteroids = pygame.sprite.Group()
	num_astros = pygame.sprite.Group()
	ships = pygame.sprite.Group()
	ammo = pygame.sprite.Group()
	hearts = pygame.sprite.Group()
	all = pygame.sprite.RenderPlain()
	
	#CREATE OBJECT CONTAINERS
	Motherships.containers = all, m_ships
	Ship.containers = all
	Shot.containers = all, shots
	BigAsteroidL.containers = all, big_asteroids
	BigAsteroidR.containers = all, big_asteroids
	AsteroidT.containers = all, asteroids
	AsteroidL.containers = all, asteroids
	AsteroidR.containers = all, asteroids
	Astronaut.containers = all, num_astros
	Astronaut2.containers = all, num_astros
	Ammunition.containers = all, ammo
	Heart.containers = all, hearts
	Explosion.containers = all
	
	#CREATE OBJECTS AND ASSOCIATE GROUPS OF OBJECTS WITH THE OBJECTS	
	arena = Arena(asteroids, num_astros, shots, ammo, hearts, big_asteroids, m_ships)
	ship = Ship(arena, asteroids, ships, num_astros, ammo, hearts, big_asteroids, m_ships)
	
	#INTRODUCTION TEXT	
	intropic = introsheet.imgat((0, 0, 1280, 800))
	screen.blit(intropic, (0, 0))
	intro_sound = pygame.mixer.Sound(os.path.join('data', intro_song))
	intro_speaking = pygame.mixer.Sound(os.path.join('data', intro_speak))

	#UPDATE DISPLAY AFTER BLITTING AND WAIT FOR AN INPUT TO BEGIN THE GAME, THEN START THE BG MUSIC
	pygame.display.update()
	intro_sound.set_volume(intro_song_vol)
	intro_sound.play(-1)
	intro_speaking.play(0)
	start_game()
	intro_sound.stop()
	intro_speaking.stop()
	pygame.mixer.music.play(-1)
			
	game = True		
	while game:
	
		global ammo_amt, shipspeed
		
# 		handle_input()
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
				
				#HOW GAMEOVER WORKS WITH CONTROLS:
				#	if level != "go" aka GAMEOVER:
				#		then allow for things to happen
				#	else if level == "go":
				#		dont allow any control of ship and other stuf
				
			#WHAT HAPPENS WHEN YOU PRESS CERTAIN KEYS	
			if event.type == KEYDOWN:
			
				#SPACE SHIP MOVEMENT	
				if event.key == K_UP:
					if level != "go":
						arena.speed += 5
						BigAsteroidL.speed += 3
						BigAsteroidR.speed += 3
						AsteroidT.speed += 3
						AsteroidL.speed += 3
						AsteroidR.speed += 3
						Astronaut.speed += 3
						Astronaut2.speed += 3
						Heart.speed += 3
						Ammunition.speed += 3					
						Ship.image = spritesheet.imgat((167, 193, 47, 50), -1)
						ship.vy = -4
						shipspeed = 250
					elif level == "go":
						pass
				elif event.key == K_DOWN:
					if level != "go":
						arena.speed -= 2
# 						arena.speed = -arena.speed
						BigAsteroidL.speed -= 1
						BigAsteroidR.speed -= 1					
						AsteroidT.speed -= 1
						AsteroidL.speed -= 1
						AsteroidR.speed -= 1
						Astronaut.speed -= 1
						Astronaut2.speed -= 1
						Heart.speed -= 1
						Ammunition.speed -= 1															
						Ship.image = spritesheet.imgat((167, 246, 47, 50), -1)
						ship.vy = +4
						shipspeed = 50
					elif level == "go":
						pass							
				elif event.key == K_LEFT:
					if level != "go":
						Ship.image = spritesheet.imgat((220, 246, 32, 50), -1)
						ship.vx = -4
					elif level == "go":
						pass							
				elif event.key == K_RIGHT:
					if level != "go":
						Ship.image = spritesheet.imgat((220, 193, 32, 50), -1)
						ship.vx = +4
					elif level == "go":
						pass
						
				#SHOOT								
				elif event.key == K_SPACE:
					if level != "go":
						if ammo_amt > 0:
							shotsound = pygame.mixer.Sound(os.path.join('data', shot_sound))
							shotsound.set_volume(shot_vol)
							shotsound.play(0)
							for gun in ship.guns:
								Shot((ship.rect.left+gun[0], ship.rect.top+gun[1]))
								ammo_amt -= 1
					elif level == "go":
						pass
				
				#PAUSE GAME
				elif event.key == K_p:
					if level != "go":
						screen.blit(game_pause, (200, SCREENRECT.centery-150))
						screen.blit(game_pause_caption, (SCREENRECT.centerx-455, SCREENRECT.centery+45))
						pygame.display.update()
						pause()
					elif level == "go":
						pass
						
				#FIRING RATE 1-4		
				elif event.key == K_1:
					if level != "go":
						ship.guns = [(23,1)]
						set_firerate("|")
					elif level == "go":
						pass	
				elif event.key == K_2:
					if level != "go":
						ship.guns = [(15,1), (31,1)]
						set_firerate("||")
					elif level == "go":
						pass	
				elif event.key == K_3:
					if level != "go":
						ship.guns = [(0,1), (23,1), (46,1)]
						set_firerate("|||")
					elif level == "go":
						pass	
				elif event.key == K_4:
					if level != "go":
						ship.guns = [(-15,1), (10,1), (33,1), (56,1)]
						set_firerate("||||")
					elif level == "go":
						pass	
						
				#KILL-ALL BUTTON		
				elif event.key == K_RSHIFT or event.key == K_LSHIFT:
					if level != "go":
						global asteroid_count
						if ammo_amt > 1:
							for asteroid in asteroids:
								asteroid_count += 1
								Explosion(asteroid)	
								asteroid.kill()	
								global score, plusminus, gainedlost, num_asteroids_killed
								score += 10000
								plusminus = "+"
								gainedlost = 10000	
								num_asteroids_killed += 1							
							explode()
							ammo_amt -= asteroid_count
							set_status("obliterate")
							asteroid_count = 0
					elif level == "go":
						pass											
						
			#WHAT HAPPENS WHEN YOU RELEASE CERTAIN KEYS			
			elif event.type == KEYUP:	
				if event.key == K_UP:
					if level != "go":
						arena.speed -= 5
						BigAsteroidL.speed -= 3
						BigAsteroidR.speed -= 3					
						AsteroidT.speed -= 3
						AsteroidL.speed -= 3
						AsteroidR.speed -= 3
						Astronaut.speed -= 3
						Astronaut2.speed -= 3
						Heart.speed -= 3
						Ammunition.speed -= 3					
						Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
						ship.vy = -1
						shipspeed = 150
					elif level == "go":
						pass
				elif event.key == K_DOWN:
					if level != "go":
						arena.speed += 2
# 						arena.speed = -arena.speed
						BigAsteroidL.speed += 1
						BigAsteroidR.speed += 1					
						AsteroidT.speed += 1
						AsteroidL.speed += 1
						AsteroidR.speed += 1
						Astronaut.speed += 1
						Astronaut2.speed += 1
						Heart.speed += 1
						Ammunition.speed += 1					
						Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
						ship.vy = 1
						shipspeed = 150
					elif level == "go":
						pass
				elif event.key == K_LEFT:
					if level != "go":
						Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
						ship.vx = -1
					elif level == "go":
						pass
				elif event.key == K_RIGHT:
					if level != "go":
						Ship.image = spritesheet.imgat((61, 193, 47, 50), -1)
						ship.vx = 1
					elif level == "go":
						pass
				elif event.key == K_RSHIFT or event.key == K_LSHIFT:
					pass			
		
		#NEXT LEVEL STATE ----- *** IMPLEMENT LATER
# 		if astros > 1000:
# 			level = 2
# 			asteroid_L_probability = 30
# 			asteroid_R_probability = 30
# 			asteroid_T_probability = 30
# 			astronaut_L_probability = 300
# 			astronaut_R_probability = 300
# 			ammo_probability = 40
# 			hearts_probability = 400			
# 			Arena.speed = 2
# 			AsteroidT.speed = 5
# 			AsteroidL.speed = 5
# 			AsteroidR.speed = 5
# 			Astronaut.speed = 5
# 			Astronaut2.speed = 5
# 			Heart.speed = 4
# 			Ammunition.speed = 4
			
			
		game_over = fatalerror.render("FATAL ERROR", 1, (0,0,0), (255,242,0))
		game_over_caption = small.render("HULL BREACH", 1, (0,0,0), (255,242,0))
		errorpic = errorsheet.imgat((0, 0, 1280, 800))			
			
		#GAME OVER STATE SETUP
		global lives
		if lives < 1:
			pygame.mixer.music.stop()		
			global level
			level = "go"
			set_status("gameover")
			pygame.time.delay(750)
			play_game_over()
			endloop = True
			thex = 0
			they = 0
			keycount = 0
			print score
			#this loop creates the shaking image at the end, the blue screen of death
			while endloop:
				screen.blit(errorpic, (thex,they))
				if thex == 4:
					thex -= 3
				if they == 4:
					they -= 3
				thex += 1
				they += 1
				screen.blit(errorpic, (thex,they))
				pygame.display.update()	
				for event in pygame.event.get():
					if event.type == KEYDOWN:
						if event.key == K_RETURN:
							keycount += 1
				if keycount == 2:
					endloop = False
					pygame.quit()
					sys.exit()
					
		elif lives > 100:
			lives = 100						
			
		game_pause = biggest.render("PAUSED", 1, (0,0,0), (255, 242, 0))
		game_pause_caption = small.render("    CRUSH P TO CONTINUE;  ESC TO BE A QUITTER    ", 1, (0,0,0), (255,242,0))
		
		if ammo_amt < 0:
			ammo_amt = 0
		
		#labels for energy, astros, shots, etc...
		num_lives = stats.render((str(lives)), 1, (255,242,0))
		num_astros = stats.render((str(astros)), 1, (255,242,0))
		num_ammo = stats.render((str(ammo_amt)), 1, (255, 242, 0))
		num_astros_killed = stats.render ((str(astros_killed)), 1, (255,242,0))	
		num_ast_destroyed = stats.render(str(num_asteroids_killed), 1, (255,242,0))
		num_shipspeed = stats.render(str(shipspeed)+"K", 1, (255,242,0))
		num_fuel = stats.render("100", 1, (255,242,0))
		rate = smallest.render(str(firerate), 1, (255,242,0))
		
		
		#score label
		num_points = scorefont.render((str(score)), 1, (255, 242, 0))
		
		#this determines the color of the point tracker.  if you are losing health for example, the tracker is red		
		if plusminus == "-":	
			g_l_color = (255,0,0)
		elif plusminus == "+":
			g_l_color = (0,255,0)
		elif plusminus == "":
			g_l_color = (0,0,0)
		elif (plusminus == "-" and rating == "attention"):
			g_l_color = (255,255,0)
		
		global bg_music_volume
		beep = pygame.mixer.Sound(os.path.join('data', low_health_beep))
		beep.set_volume(.05)
		global lives
		if lives < 40:
# 			shipstatus = "INTEGRITY WARNING"
			shipstatus = "BEWARE LOW HEALTH"
			l_h_color = (182,177,0)		
		else:
			healthstatus = False
			l_h_color = (0,0,0)
			shipstatus = ""
			beep.stop()
			
			
			
								
		
		#point tracker: g_l is the actual points being tracked, event_status is just the information that you get, aka WHY youre losing pts		
		event_status = statusfont.render(str(status), 1, g_l_color)
		g_l = statusfont.render(str(plusminus)+str(gainedlost), 1, g_l_color)
		low_health = integrity.render(str(shipstatus), 1, l_h_color)				
				
		#GUI IMAGES		
		heart_icon = spritesheet.imgat((209,81,15,15))
		astronaut_icon = spritesheet.imgat((225,81,15,15))
		ammo_icon = spritesheet.imgat((193,81,15,15))
		dead_astro_icon = spritesheet.imgat((273,81,15,15))
		firerate_icon = spritesheet.imgat((289,81,15,15))
		hud = game_hud.imgat((0,0,1280,260), -1)	#the green hud display
		
		
		#DRAW THE GAME AND SPACE BG
		all.update()						#this updates the group containing all objects, allowing them to be redrawn to create animation
		screen.blit(arena.floor, (0,0), arena.offset())
	
		#DRAW HUD		
		screen.blit(hud, (0,0))
		screen.blit(rate, (1205,0))
		screen.blit(num_lives, (55,15))
		screen.blit(num_ammo, (1200,15))
		screen.blit(num_astros, (55,64))
		screen.blit(num_ast_destroyed, (55,114))
		screen.blit(num_shipspeed, (1193,62))
		screen.blit(num_fuel, (1200, 114))
		screen.blit(num_points, (655,30))
		screen.blit(g_l, (360,20))
		screen.blit(event_status, (360,40))
		screen.blit(low_health, (485, 85))
		
		#REFRESH SCREEN
		all.draw(screen)	#this command actually renders the objects on the screen		
		pygame.display.update()
			
		#SET REFRESH RATE
		clock.tick(60)
				
if __name__ == '__main__': main()		