from fltk import *
from PIL import Image
import random, io, time

class game(Fl_Double_Window):
	def __init__(self,w,h,label = "Minesweeper"):
		super().__init__(w,h,label)
		self.rows = 20
		self.cols = 20
		self.tsizex = w//self.rows
		self.tsizey = h//self.cols
		self.marker = 0 #start time marker

		self.buts(w,h)
		while self.mines > 0 :#makes sure all mines are placed
			self.buts(w,h)

		self.images = {	#covers 90% of tile to show lines
			"click":self.img_resize('click.png',(self.tsizex//10)*9),
			"mine": self.img_resize('mine.png',(self.tsizex//10)*9),
			"flag": self.img_resize('flag.png',(self.tsizex//10)*9),
			"wrong": self.img_resize('wrong.png',(self.tsizex//10)*9),
			"numbers": [None],
			"wnumbers":[None],
			'red': self.img_resize('red.png',(self.tsizex//10)*9),
        }
		for i in range(1, 9):
			self.images["numbers"].append(self.img_resize(str(i)+'.png',(self.tsizex//10)*9))
			self.images["wnumbers"].append(self.img_resize('w'+str(i)+'.png',(self.tsizex//10)*9))

		self.resizable(self)
		self.size_range(w,h)

	#creates grid
	def buts(self,w,h):
		p=Fl_Group(0,0,w,h)
		p.begin()
		self.tiles = {}
		self.mines = 40
		self.mcount = self.mines #constant value of # of mines in game
		for x in range(0,w,self.tsizex):
			for y in range(0,h,self.tsizey):
				dx = round(x/self.tsizex)
				dy = round(y/self.tsizey)
				if y == 0:
					self.tiles[dx] = {}

				but = Fl_Button(x,y,self.tsizex,self.tsizex)
				but.color(FL_DARK2)
				isMine = False

				#random place mine/ act like percentage
				if random.uniform(0.0, 1.0) < 0.05 :
					if self.mines > 0:
						isMine = True
						self.mines -= 1
				
				id = str(dx) + "_" + str(dy)
				tile = {
					"id": id,
					"isMine": isMine,
					"clicked": False,
					"flag":False,
					"coords": {"x": x,"y": y},
					"but": but,
					"mines":0
					}

				self.tiles[dx][dy] = tile
		
		#counts the number of mine surrounding each tile
		for i in range (self.rows):
			for j in range (self.cols):
				num = self.getBombs(i,j)
				self.tiles[i][j].update({'mines':num})

		p.end()
		p.type(FL_NO_BOX)
		p.resizable(None)

	def handle(self,event):
		#mark start time
		while self.marker == 0:
			self.start = time.time()
			self.marker += 1
		
		r = super().handle(event)
		try:
			dx = Fl.event_x()//self.tsizex
			dy = Fl.event_y()//self.tsizey
			clk = self.tiles[dx][dy]
			self.surround(dx,dy)

		except:
			return r

		#flag
		if event == FL_PUSH and Fl.event_button() == FL_RIGHT_MOUSE:

			if clk['but'].image() == None:
				clk['but'].image(self.images['flag'])
				clk['flag'] = True

			elif clk['flag'] == True:
				clk['but'].image(None)
				clk['flag'] = False
			
			return 1

		elif event == FL_PUSH and Fl.event_button() == FL_LEFT_MOUSE:
			
			if clk['but'].image() == None:
				clk['clicked'] = True
				if clk['isMine'] == True:
					clk['but'].image(self.images['mine'])
					self.lost()
					fl_message("You lost!")
					self.hide()

				elif clk['mines'] > 0 and clk['isMine'] == False:
					clk['but'].image(self.images['numbers'][clk['mines']])
			
				elif clk['mines'] == 0:
					clk['but'].image(self.images['click'])
					self.csurrond(dx,dy)
				self.win()
				return 1
			
			else:
				pass
		return r

	#check if won
	def win(self):
		for x in range(self.rows):
			for y in range(self.cols):
				var = self.tiles[x][y]
				if var['clicked'] == False and var['isMine'] == False:
					return

		self.end = time.time()
		sec = round(self.end - self.start,2)
		
		with open('highscore.txt', 'r') as f: 
			text = f.read()
		f.close()
		with open('highscore.txt', 'w') as f:

			if text == '':
				name = fl_input(f'Congrats!! New high score of {sec} seconds!!\nEnter name:')
				f.write(f'{name} - {sec}s')
			elif sec < float(text[-5:-1]):
				name = fl_input(f'Congrats!! New high score of {sec} seconds!!\nEnter name:')
				f.write(f'{name} - {sec}s')
			else:
				fl_message(f'You won in {sec} seconds!\nRecord: {text}')
			f.close()	
		self.hide()

	#when loses
	def lost(self):
		for x in range(self.rows):
			for y in range(self.cols):

				var = self.tiles[x][y]	

				#ways of losing
				if var['mines'] == 0 and var['clicked'] == False:
					var['but'].image(self.images['red'])
					var['but'].redraw()

				elif var['flag'] == True and var['isMine'] == True:
					pass

				elif var['isMine'] == False and var['flag'] == True:
					var['but'].image(self.images['wrong'])
					var['but'].redraw()

				elif var['isMine'] == False and var['clicked'] == False:
					var['but'].image(self.images['wnumbers'][var['mines']])
					var['but'].redraw()

				elif var['isMine'] == True:
					var['but'].image(self.images['mine'])
					var['but'].redraw()

				else:
					pass
	
	#get coordinates for surronding tiles
	def surround(self,dx,dy):
		coords = [
				{"x": dx-1,  "y": dy-1},  #top right
				{"x": dx-1,  "y": dy},    #top middle
				{"x": dx-1,  "y": dy+1},  #top left
				{"x": dx,    "y": dy-1},  #left
				{"x": dx,    "y": dy+1},  #right
				{"x": dx+1,  "y": dy-1},  #bottom right
				{"x": dx+1,  "y": dy},    #bottom middle
				{"x": dx+1,  "y": dy+1},  #bottom left
			]
		return coords

	#changes surrouding tiles
	def csurrond(self,dx,dy):
		for b in self.surround(dx,dy):	
			try:	
				x = b['x'] 
				y = b['y']
				
				num = self.tiles[x][y]['mines']

				if self.tiles[x][y]['but'].image() == None:
					if num == 0:
						self.tiles[x][y]['but'].image(self.images['click'])
						self.tiles[x][y]['but'].redraw()						
						self.csurrond(x,y)

					elif num > 0:
						self.tiles[x][y]['but'].image(self.images['numbers'][num])
						self.tiles[x][y]['but'].redraw()

					self.tiles[x][y]['clicked'] = True

				else:
					pass				
			except:
				pass

	#get surronding tiles number of bombs
	def getBombs(self,dx,dy):
		if self.tiles[dx][dy]['isMine'] == False:
			coords = self.surround(dx,dy)

			for b in coords:
				try:
					if self.tiles[b["x"]][b["y"]]['isMine'] == True:
						self.tiles[dx][dy]['mines'] += 1
					else:
						pass

				except:
					pass

			return self.tiles[dx][dy]['mines']

	def img_resize(self,fname,width):
		img = Image.open(fname)
		w,h = img.size
		height = int(width*h/w)
		img = img.resize((width, height), Image.BICUBIC)
		mem = io.BytesIO()  
		img.save(mem, format="PNG")
		siz = mem.tell()
		return Fl_PNG_Image(None, mem.getbuffer(), siz)

app = game(250,250)
app.show()
Fl.run()
