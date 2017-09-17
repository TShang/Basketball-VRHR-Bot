import gtk.gdk
import cv2
import numpy as np
from pymouse import PyMouse
import time
from PIL import Image

m = PyMouse()

def getPos(im1, im2):
		obj = cv2.imread(im1)
		screenshot = cv2.imread(im2)
		result = cv2.matchTemplate(obj,screenshot,cv2.TM_CCOEFF_NORMED)
		y,x = np.unravel_index(result.argmax(), result.shape)
		width, height,ch = obj.shape
		return x+width/2,y+height/2

def notMoving (x1 ,x2):
	return (abs(x1-x2) < 3)

def capture ():
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	pb.save("screenshot.png","png")
	#crop image for just game to reduce image matching processing time
	img = Image.open("screenshot.png")
	img2 = img.crop((722,146,1187,971))#values for where game located on screen
	img2.save("crop.png")

#converting x,y values to the proper 1080p values
def convert (x , y):
	return x + 722 , y + 146

move = 0;
count = 0;
f = open('final_data.txt','a') #file for data useful for debugging/testing
time.sleep(2)
while True:
	#m.press(951,900)
	#m.release(951,900)
	mousex,mousey = m.position()
	capture()
	ballx,bally = getPos("basketball_ball.png", "crop.png")
	t1 = time.time();
	x,y = getPos("basketball_hoop.png", "crop.png")
	
	capture()
	t2 = time.time();
	x1,y1 = getPos("basketball_hoop.png", "crop.png")
	
	x,y = convert (x,y)
	x1,y1 = convert (x1,y1)
	ballx, bally = convert(ballx,bally)


	#executes seperate shot commands for static shots and moving shots
	if (move != 1 and notMoving(x,x1)):
		offset = abs(ballx - x)
		if ballx > x:
			x += offset / 3
		else:
			x -= offset / 3
		print("Fixed hoop position: "+str((x,y)))
		#press at ball position, move gradually towards target release coord then release
		m.press(ballx,bally)
		m.move(x - ballx / 3, y - bally / 3)
		m.move(x - ballx / 2, y - bally / 2)
		m.release(x,y)
		time.sleep(3)
		
		
	else:
		move = 1
		offset = abs(ballx - x)
		if ballx > x:
			x += offset / 2
		else:
			x -= offset / 2
		offset = abs(ballx - x1)
		if ballx > x1:
			x1 += offset / 2
		else:
			x1 -= offset / 2

		dx = x1 - x
		dt = t2 - t1
		velocity = (dx)/(dt)
		print x1
		print velocity
		#tested values for a 1080p display; different conditions for either direction
		if (x1 < 1050 and x1 > 965 and velocity < 0):
			x1 -= 65
			
			m.press(ballx,bally)
			m.move(x1 - ballx / 3, y1 - bally / 3)
			m.move(x1 - ballx / 2, y1 - bally / 2)
			m.release(x1, y1)
	
			print ("Hoop shot position:" + str((x1,y1)))
			
			#f.write("\n" + "Velocity:" + str(velocity))
			f.write("\n" + "Pred Shot Position:" + str((x1,y1)))
			count += 1
			time.sleep(3)

		elif (x1 < 939 and x1 > 859 and velocity > 0):
			x1 += 65
			
			m.press(ballx,bally)
			m.move(x1 - ballx / 3, y1 - bally / 3)
			m.move(x1 - ballx / 2, y1 - bally / 2)
			m.release(x1, y1)
	
			print ("Hoop shot position:" + str((x1,y1)))
			
			#f.write("\n" + "Velocity:" + str(velocity))
			f.write("\n" + "Pred Shot Position:" + str((x1,y1)))
			count += 1
			time.sleep(2)

	
		

	
	
f.close ()