 # Imports

import pygame
import random
import json
from pygame import *
import socket
from _thread import *
import _pickle as pickle
from copy import copy
from pprint import pprint
from tkinter import *

import struct
import sys
from _thread import *
from tkinter import *

# Screen Dimensions

WIN_WIDTH = 800
WIN_HEIGHT = 500
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

# Screen Defaults

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

# Init, Create Screen

pygame.init()
screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)

##############Drawing Code##############

# sprites of gunner

spritesheet = pygame.image.load('Media/Graphics/white.png')

character = pygame.image.load('Media/Graphics/white.png')
character = pygame.transform.scale(character, (78,91))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
standright = stage

character = pygame.image.load('Media/Graphics/white.png')
character = pygame.transform.scale(character, (78,91))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
blinkright = stage

standloopright2 = [standright, blinkright]
standloopleft2 = [pygame.transform.flip(standright, True, False),
				  pygame.transform.flip(blinkright, True, False)]

character = pygame.image.load('Media/Graphics/wr1.png')
character = pygame.transform.scale(character, (75,103))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
stepright = stage

character = pygame.image.load('Media/Graphics/wr2.png')
character = pygame.transform.scale(character, (74,103))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
runright1 = stage

character = pygame.image.load('Media/Graphics/wr3.png')
character = pygame.transform.scale(character, (76,104))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
runright2 = stage

character = pygame.image.load('Media/Graphics/wr4.png')
character = pygame.transform.scale(character, (73,103))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
runright3 = stage

character = pygame.image.load('Media/Graphics/wr5.png')
character = pygame.transform.scale(character, (73,105))
stage = Surface((300, 150), pygame.SRCALPHA)
stage.blit(character, (130, 0))
runright4 = stage


walkloopright2 = [
	stepright,
	runright1,
	runright2,
	runright3,
	runright4
	]

walkloopleft2 = [
	pygame.transform.flip(walkloopright2[0], True, False),
	pygame.transform.flip(walkloopright2[1], True, False),
	pygame.transform.flip(walkloopright2[2], True, False),
	pygame.transform.flip(walkloopright2[3], True, False),
	pygame.transform.flip(walkloopright2[4], True, False)
	]

# global variables

musicplaying = ''
invincible = False
maincounter = 0
wave = 1
abilityShield = False
abilityShoot = False
shows = False
showa = False
enemyid = 1
renemyid = 0


# Main Function

def main():
	i = 0
	global wave, maincounter
	# Create clock, set caption

	timer = pygame.time.Clock()
	pygame.display.set_caption('Among Us Clone')

	# Create Game

	game = Game()

	# Create Player

	player = Gunner(game)

	# create player 2 for multiplayer

	player2 = copy(player)
	player3 = copy(player)

	# Create Display

	display = Display('')

	# Create level

	room = Rooms(game, player)

	# Main Loop

	while 1:
		timer.tick(7)
		
		#multiplayer mode options for chosing to be host or client
		if game.screenfocus == 'Multiplayer':

			for e in game.titlegroup:
				#to draw the among us clone image on the title screen
				screen.blit(e.image, (0, 0))
			
			game.title.update2()

			game.buttongroup['host'].draw(screen)
			game.buttongroup['connect'].draw(screen)

		#characters select screen for multiplayer
		
		#connecting from host
		if game.screenfocus == 'host':
			server = ''
			port = 6767

			hsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			try:
				hsocket.bind((server, port))
			except socket.error as e:
				str(e)

			print('Waiting for a connection, Server Started.')
			showtxt('Host ip is :'
					+ socket.gethostbyname(socket.gethostname()))
			
			
			while True:
				 #getting other player's character type
				(data, addr) = hsocket.recvfrom(1024)
				data = data.decode('utf-8')
				if data == 'gunner':
					player2 = Gunner(game)
					game.playerentity.remove(player2)
				hsocket.sendto(player.type.encode('utf-8'), addr)
				

				game.screenfocus = 'Server'
				wave = 1
				
				break
		#running game from host end
		if game.screenfocus == 'Server':
			


			game.camera.update(game.camerafocus)
			player.update()

			
			for e in game.entities:
				#backgroud for the host
				screen.blit(e.image, game.camera.apply(e))

			#sending and reciving data to/from client
			try:
				#sending host side player info to client
				player_host = player.__dict__.copy()
				player_host.pop('image')
				player_host.pop('bg')
				player_host.pop('detectable')
				player_host.pop('game')
				player_host.pop('projectile')
				player_host.pop('_Sprite__g')
				player_host['rect'] = tuple(player_host['rect'])

				enemy_host = []  
				projectile_host = []
				
				#sending projectiles info towards client end
				for q in game.projectilegroup:
					temp = q.__dict__.copy()
					temp.pop('image')
					temp.pop('game')
					temp.pop('pxl')
					temp.pop('detectable')
					temp.pop('_Sprite__g')
					temp['rect'] = tuple(temp['rect'])
					projectile_host.append(temp)
				#object to store all info to be sent
				saveobj = (player_host, enemy_host, projectile_host, wave,player.isKilling)
			   
				hsocket.sendto(json.dumps(saveobj).encode('utf-8'),
							   addr)
			   
		
				(recv_client, addr) = hsocket.recvfrom(1024 * 8)
				recv_client = json.loads(recv_client.decode('utf-8'))
			   

				#variable to check if client's character killed which id mobs
				renemyid = recv_client[1]
				
				#client end player info is updated here
				player2.__dict__.update(recv_client[0])

				if player.isKilling == True:
					player2.isDead = True

				if player2.isKilling == True:
					player.isDead = True
					
				player2.animate()
				player2.rect = Rect(player2.rect)
				player2.detectable = pygame.sprite.Group()
				player2.detectable.rect = Rect(player2.rect)
				#projectiles info from client end is updated here
				for e in recv_client[2]:
					pro = copy(Projectile(player2, game, e['type']))
					pro.detectable.rect = Rect(e['rect'])
					pro.rect = Rect(e['rect'])

					#it keeps the client player moving
				  
					screen.blit(pro.image, game.camera.apply(pro))
				if not player2.destroyed == True:
					#draws player 2 in player 1 window
					screen.blit(player2.image,game.camera.apply(player2))

			except Exception as e:
				print(e)
			
			for e in game.playerentity:
				#draws player 1 on player 1 window
				screen.blit(e.image, game.camera.apply(e))

			keysss = pygame.key.get_pressed()
			if player.isDead == False:
				if ((player.rect.x) - (player2.rect.x)) < abs(40) and ((player.rect.y) - (player2.rect.y)) < abs(40) and keysss[pygame.K_SPACE]:
					player.isKilling = True

			
		#connecting from client
		if game.screenfocus == 'Connect':
			#ip = inputtxt('Please enter ip')
			#ip = ip + ''
			ip = '127.0.0.1'
			cl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			addr = (ip, 6767)
			print('connected')
			cl.sendto(player.type.encode('utf-8'), addr)
			(data, addr) = cl.recvfrom(1024)
			data = data.decode('utf-8')
			#getting character type info of host end
			if data == 'gunner':
				player2 = Gunner(game)
				game.playerentity.remove(player2)
			if player.name == '':
				player.name = inputtxt('enter name')
			game.screenfocus = 'Client'


		   #running game from client end

		if game.screenfocus == 'Client':
			
			game.camera.update(game.camerafocus)
			if player.destroyed == True:
				player.invincible = True
				player.icounter = 0
			player.update()
			
			for e in game.entities:
				#draws the background for player 2 window
				screen.blit(e.image, game.camera.apply(e))
			
			#sending and reciving data from/to client
			try:
				#sending client's end player info to host
				player_client = player.__dict__.copy()
				player_client.pop('image')
				player_client.pop('bg')
				player_client.pop('detectable')
				player_client.pop('game')
				player_client.pop('projectile')
				player_client.pop('_Sprite__g')
				player_client['rect'] = tuple(player_client['rect'])

				projectile_client = []
				#sending projectiles from client end info to server
				for q in copy(game.projectilegroup):
					temp = q.__dict__.copy()
					temp.pop('image')
					temp.pop('game')
					temp.pop('pxl')
					temp.pop('detectable')
					temp.pop('_Sprite__g')
					temp['rect'] = tuple(temp['rect'])
					projectile_client.append(temp)

				#object to store all info to be sent
				saveobj = (player_client, enemyid, projectile_client)
		
				(recv_host, addr) = cl.recvfrom(1024 * 20)
				recv_host = json.loads(recv_host.decode('utf-8'))
			   
			   
				cl.sendto(json.dumps(saveobj).encode('utf-8'), addr)
			   
				i = 0
				wave = recv_host[3]
				#host end character data ins updated here
				player2.__dict__.update(recv_host[0])
				if player2.isKilling == True:
					player.isDead = True

				if player.isKilling == True:
					player2.isDead = True

				player2.animate()
				player2.rect = Rect(player2.rect)
				player2.detectable = pygame.sprite.Group()
				player2.detectable.rect = Rect(player2.rect)

				#end game if host character dies
				if player2.destroyed == True:
					game.screenfocus = 'Multiplayer Game Over'
					cl.close()
				game.projectilegroupc.empty()

				#projectiles from host end are updated and shown here
				for e in recv_host[2]:
					pro = copy(Projectile(player2, game, e['type']))
					pro.detectable.rect = Rect(e['rect'])
					pro.rect = Rect(e['rect'])
					game.projectilegroupc.add(pro)

					#no idea why it is used does'nt changes anything
					screen.blit(pro.image, game.camera.apply(pro))

				#draws player 1 img in player 2 win
				screen.blit(player2.image, game.camera.apply(player2))

				
			except Exception as e:
				print(str(e))
			if not player.destroyed == True:
				for e in game.playerentity:
					#draws player 2 in player 2 window
					screen.blit(e.image, game.camera.apply(e))
			for e in game.projectilegroup:
				e.update(game.platforms)
				#makes the player 1 move condinuoulsy even after dead
				screen.blit(e.image, game.camera.apply(e))


			keysss = pygame.key.get_pressed()
			if player.isDead == False:
				if (player.rect.x-player2.rect.x)<abs(40) and (player.rect.y-player2.rect.y)<abs(40) and keysss[pygame.K_SPACE]:
					player.isKilling = True

			
		
		pygame.display.update()


class Game(object):

	def __init__(self):

		# Create Sprite Groups

		self.buttongroup = {}
		self.entities = pygame.sprite.Group()
		self.bg = pygame.sprite.Group()
		self.playerentity = pygame.sprite.Group()
		self.projectilegroup = pygame.sprite.Group()
		self.projectilegroupc = pygame.sprite.Group()

		self.enemygroup = pygame.sprite.Group()
		self.menugroup = pygame.sprite.Group()
		self.titlegroup = pygame.sprite.Group()
		self.detectablegroup = pygame.sprite.Group()

		# Create Camera

		self.camera = ''
		self.camerafocus = ''

		# Create Platforms

		self.platforms = []

	   
 
	  
		# Create Screen Focus

		self.screenfocus = 'Multiplayer'

		# Create Title

		self.title = Title(self)

		# Create Gameover

		

	  
  


class Entity(pygame.sprite.Sprite):

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)


class Platform(Entity):

	def __init__(self,x,y,w,h,chatid=0,):
		Entity.__init__(self)
		self.rect = Rect(x * 3, y * 3, w * 3, h * 3)
		self.chatid = chatid

	def update(self):
		pass




class Gunner(Entity):

	def __init__(self, game, typee='gunner'):
		Entity.__init__(self)
		#player type
		self.type = typee
		self.destroyed = False

		# Add Player to Game

		self.icounter = 0  # invincible counter
		self.name = 'bhargab'
		self.isKilling = False
		self.game = game
		self.score = 0
		self.game.playerentity.add(self)

		# Set Player Velocities

		self.xvel = 0
		self.yvel = 0

		# Set Player Offsets

		self.xoffset = -128
		self.yoffset = 0

		

		# Counters

		self.walkcounter = 0
		self.standcounter = 0

		self.attackcounter = 0
		self.takedamagecounter = 0
		self.counter = 0

		# States
		# abilities

		self.shooting = False
		#background
		self.bg = \
			pygame.image.load('Media/Graphics/Backgrounds/cafe.png')
		

		self.projectile = None

		self.collideright = False
		self.faceright = True
		self.takingdamage = False
		self.attacking = False

		self.moving = False

		# Create Player Sprite

		self.image = Surface((19 * 2, 35 * 2), pygame.SRCALPHA)
		self.rect = Rect(0, 0, 19 * 2, 35 * 2)

		# Create Player Detectable Area

		self.detectable = pygame.sprite.Sprite()
		self.detectable.rect = Rect(0, 0, 19 * 2, 35 * 2)
		self.detectable.image = Surface((19 * 2, 35 * 2))
		self.detectable.image.fill(Color('#0033FF'))
		self.detectable.image.set_alpha(150)
		self.detectable.image.convert_alpha()
		game.detectablegroup.add(self.detectable)


		# Inputs

		self.up = False
		self.down = False
		self.right = False
		self.left = False
		self.isDead = False

		colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,100,0),(30,30,30),(0,255,255)]
		i = random.randint(0,len(colors)-1)
		
		self.color = colors[i]

	#stats before serilizing and sending/recving via socket

	def __getstate__(self):

		state = self.__dict__.copy()

		surface = state.pop('image')

	   
		surface = state.pop('bg')

		
		surface = state.pop('detectable')

		surface = state.pop('game')

		return state

	def __setstate__(self, state):

	   
		state['bg'] = \
			pygame.image.load('Media/Graphics/Backgrounds/cafe.png')

	   
		self.__dict__.update(state)

	def startingposition(self, x, y):
		self.rect = Rect(x, y, 19 * 2, 22 * 2)
		self.detectable.rect = Rect(x, y, 19 * 2, 22 * 2)

	def inputhandler(self):

		for e in pygame.event.get():

			if e.type == QUIT:
				raise SystemExit('QUIT')
			'''

			if e.type == KEYDOWN and e.key == K_SPACE:
				self.isDead = True'''
			
			if e.type == KEYDOWN and e.key == K_UP:
				self.up = True
			if e.type == KEYDOWN and e.key == K_DOWN:
				self.down = True
			if e.type == KEYDOWN and e.key == K_LEFT:
				self.left = True
			if e.type == KEYDOWN and e.key == K_RIGHT:
				self.right = True
			

			
			if e.type == KEYUP and e.key == K_UP:
				self.up = False

			if e.type == KEYUP and e.key == K_a:
				self.canlaser = False
			if e.type == KEYUP and e.key == K_s:
				self.cansniper = False

			if e.type == KEYUP and e.key == K_DOWN:
				self.down = False
				self.dancecounter = 0
			if e.type == KEYUP and e.key == K_RIGHT:
				self.right = False
				self.counter = 0
			if e.type == KEYUP and e.key == K_LEFT:
				self.left = False
				self.counter = 0

			pos = pygame.mouse.get_pos()

			

	def update(self):

		

		global shows, showa
		iscolor = False

		

		self.inputhandler()

		
		# Apply Inputs
		# Move if not taking damage
		if self.isDead == False:
			if self.up:
				self.yvel = -20
				self.moving = True

				
			# Move if not taking damage
			if self.down:
				self.yvel = 20
				self.moving = True

			# Move if not taking damage
			if self.left:
				self.faceright = False
				self.xvel = -20
				self.moving = True

				

			if self.right:
				self.faceright = True
				self.xvel = 20
				self.moving = True

			
				
		
			#boundries for character
			
				# Apply States
			if not (self.left or self.right):
				self.xvel = 0
			if not (self.up or self.down):
				self.yvel = 0
			# Stop player if not taking damage
			if not (self.up or self.down or self.right or self.left):
				self.moving = False
		else:
			# Offsets

			self.rect.x = self.detectable.rect.x - 15
			self.rect.y = self.detectable.rect.y + self.yoffset
			self.animate()
			return

			
		

			
		

		# Collisions

		self.detectable.rect.left += self.xvel
		self.collide(self.xvel, 0)
		self.detectable.rect.top += self.yvel
		self.onGround = False
		self.collide(0, self.yvel)

		# Offsets

		self.rect.x = self.detectable.rect.x + self.xoffset
		self.rect.y = self.detectable.rect.y + self.yoffset

		# Animate

		self.animate()
		


	def collide(self, xvel, yvel):
		global invincible

		if invincible:
			self.icounter += 1
		if self.icounter >= 100:

			self.icounter = 0
			invincible = False

	def animate(self):

		state = []
		state.append(False)
		state.append(self.moving)
		state.append(self.faceright)

		if self.isDead == True:

			bone1 = pygame.image.load('Media/Graphics/bone1.png').convert_alpha()
			bone1 = pygame.transform.scale(bone1,(73,85))

			bone = pygame.image.load('Media/Graphics/bone.png').convert_alpha()
			bone = pygame.transform.scale(bone,(73,85))
			
			self.image =self.changColor(bone,bone1,self.color)

			return

		

		# Moving

		if state[1]:
			if state[0]:
				pass
			else:
				if state[2]:
					self.walkloop(walkloopright2)
				else:
					self.walkloop(walkloopleft2)
		else:
			if state[0]:
				pass
			else:

				if state[2]:
					self.standloop(standloopright2)
				else:
					self.standloop(standloopleft2)

		# Attacking

		

	# Standing Animation Loop

	def standloop(self, loop):
		if self.standcounter == 0 or self.standcounter == 1:
			self.walkcounter = 0
			self.updatecharacter(loop[0])
		elif self.standcounter == 200:
			self.updatecharacter(loop[1])
		elif self.standcounter == 210:
			self.updatecharacter(loop[0])
			self.standcounter = 0
		self.standcounter = self.standcounter + 1

	# Walking Animation Loop

	
	def walkloop(self, loop):
		if self.walkcounter == 0 or self.walkcounter == 1:
			self.standcounter = 0
			self.updatecharacter(loop[0])
		elif self.walkcounter == 5:
			self.updatecharacter(loop[1])
		elif self.walkcounter == 10:
			self.updatecharacter(loop[2])
		elif self.walkcounter == 15:
			self.updatecharacter(loop[3])
		elif self.walkcounter == 20:
			self.updatecharacter(loop[4])
		elif self.walkcounter == 25:
			self.updatecharacter(loop[0])
			self.walkcounter = 0
		

		self.walkcounter = self.walkcounter + 5

	# Update Current Frame

	def updatecharacter(self, ansurf):
		if self.isDead == False:
			self.image = ansurf
			self.image =self.changColor(self.image,self.image,self.color)
		
			


	def changColor(self,image, maskImage, newColor):
		colouredImage = pygame.Surface(image.get_size())
		colouredImage.fill(newColor)
		masked = maskImage.copy()
		masked.set_colorkey((0, 0, 0))
		masked.blit(colouredImage, (0, 0), None, pygame.BLEND_RGBA_MULT)
		finalImage = image.copy()
		finalImage.blit(masked, (0, 0), None)
		return finalImage


class Rooms(object):

	def __init__(self, game, player):
		self.width = 0
		self.height = 0
		self.game = game
		self.player = player

		self.createroom1('a')

	def dumpsprites(self):

		self.game.enemygroup.empty()
		self.game.entities.empty()

		self.game.platforms = []

	def resetcamera(self):
		total_level_width = self.width * 3
		total_level_height = self.height * 3
		self.game.camera = Camera(complex_camera, total_level_width,
								  total_level_height)
		self.game.camerafocus = self.player.detectable

	def setbackground(self, backgroundpath):
		self.dumpsprites()
		bg = Entity()

		bg.image = pygame.image.load(backgroundpath)
		self.width = bg.image.get_width()
		self.height = bg.image.get_height()

		bg.rect = Rect(0, 0, self.width * 3, self.height * 3)
		bg.image = pygame.transform.scale(bg.image,(2748,1425))

	   
		self.game.entities.add(bg)

		self.resetcamera()

	def createroom1(self, entrance):
		# creating buttons

		self.game.buttongroup['back'] = button(
			(0, 255, 0),
			400,
			500,
			180,
			50,
			'back',
			)

		self.game.buttongroup['host'] = button(
			(0, 255, 0),
			300,
			300,
			200,
			50,
			'host',
			)
		self.game.buttongroup['connect'] = button(
			(255, 0, 0),
			300,
			400,
			200,
			50,
			'connect',
			)

		
		#setting background
		self.setbackground('Media/Graphics/Backgrounds/cafe.png')

	

		bg = pygame.image.load('Media/Graphics/Backgrounds/cafe.png')

		# Set Up Player

		if entrance == 'a':
			self.player.startingposition(520 * 3, 258 * 3)

		# Set Up Enemies

		# Set Up Platforms

		self.game.platforms.append(Platform(506, 24, 158, 39))
		self.game.platforms.append(Platform(506, 577, 158, 39))
		self.game.platforms.append(Platform(1000, 255, 30, 67))
		self.game.platforms.append(Platform(118, 274, 33, 61))



class Camera(object):

	def __init__(
		self,
		camera_func,
		width,
		height,
		):
		self.camera_func = camera_func
		self.state = Rect(0, 0, width, height)

	def apply(self, target):
		return target.rect.move(self.state.topleft)

	def update(self, target):
		self.state = self.camera_func(self.state, target.rect)


def simple_camera(camera, target_rect):
	(l, t, _, _) = target_rect
	(_, _, w, h) = camera
	return Rect(-l + HALF_WIDTH, -t + HALF_HEIGHT, w, h)


def complex_camera(camera, target_rect):
	(l, t, _, _) = target_rect
	(_, _, w, h) = camera
	(l, t, _, _) = (-l + HALF_WIDTH, -t + HALF_HEIGHT, w, h)

	l = min(0, l)  # stop scrolling at the left edge
	l = max(-(camera.width - WIN_WIDTH), l)  # stop scrolling at the right edge
	t = max(-(camera.height - WIN_HEIGHT), t)  # stop scrolling at the bottom
	t = min(0, t)  # stop scrolling at the top
	return Rect(l, t, w, h)







class Title(object):

	def __init__(self, game, player=None):
		self.game = game
		self.counter = 0
		self.createtitle()
		self.player = player

	def createtitle(self):

		# Empty Sprite Groups

		self.game.titlegroup.empty()
		self.game.menugroup.empty()

		# Create Background Sprite

		bg = Entity()
		bg.image = \
			pygame.image.load('Media/Graphics/Backgrounds/title.png')
		self.game.titlegroup.add(bg)

	def inputhandler(self):
		for e in pygame.event.get():
			if e.type == QUIT:
				raise SystemExit('QUIT')

			pos = pygame.mouse.get_pos()

			if e.type == pygame.MOUSEBUTTONDOWN:
				
				if self.game.buttongroup['host'].isOver(pos):
					self.game.screenfocus = 'host'
				elif self.game.buttongroup['connect'].isOver(pos):
					self.game.screenfocus = 'Connect'
			

	def update(self):
		self.inputhandler()

		# Animate Title Screen

		self.counter = self.counter + 1

	def update2(self):
		for e in pygame.event.get():
			if e.type == QUIT:
				raise SystemExit('QUIT')
			
			pos = pygame.mouse.get_pos()

			if e.type == pygame.MOUSEBUTTONDOWN:
				if self.game.buttongroup['host'].isOver(pos):
					self.game.screenfocus = 'host'
				elif self.game.buttongroup['connect'].isOver(pos):
					self.game.screenfocus = 'Connect'



class Display(Entity):

	def __init__(self, string):
		Entity.__init__(self)
		self.font = pygame.font.Font(None, 80)
		self.image = self.font.render(string, 1, (255, 0, 0))

	def update(self, string):
		self.image = self.font.render(string, 1, (255, 0, 0))


class button:

	def __init__(
		self,
		color,
		x,
		y,
		width,
		height,
		text='',
		):
		self.color = color
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text

	def draw(self, win, outline=None):

		# Call this method to draw the button on the screen

		if outline:
			pygame.draw.rect(win, outline, (self.x - 2, self.y - 2,
							 self.width + 4, self.height + 4), 0)

		pygame.draw.rect(win, self.color, (self.x, self.y, self.width,
						 self.height), 0)

		if self.text != '':
			font = pygame.font.SysFont('comicsans', 60)
			text = font.render(self.text, 1, (0, 0, 0))
			win.blit(text, (self.x + self.width / 2 - text.get_width()
					 / 2, self.y + self.height / 2 - text.get_height()
					 / 2))

	def isOver(self, pos):

		# Pos is the mouse position or a tuple of (x,y) coordinates

		if pos[0] > self.x and pos[0] < self.x + self.width:
			if pos[1] > self.y and pos[1] < self.y + self.height:
				return True

		return False


def inputtxt(msg):
	window = Tk()
	window.title('window')
	window.geometry('500x500+300+100')
	txt = StringVar()

	def com():
		if txt.get() == '' or txt.get()[0] == ' ':
			pass
		else:
			window.destroy()

	labl2 = Label(text=msg, font=20).pack()
	button1 = Button(text='Enter', command=com).pack()
	text = Entry(textvariable=txt).pack()
	window.mainloop()
	while txt.get() == '' or txt.get()[0] == ' ':
		window.mainloop()

	return txt.get()


def showtxt(msg):
	window = Tk()
	window.title('window')
	window.geometry('500x500+300+100')
	txt = StringVar()

	def com():
		window.destroy()

	labl2 = Label(text=msg, font=20).pack()
	button1 = Button(text='OK', command=com).pack()
	window.mainloop()


if __name__ == '__main__':
	main()


			