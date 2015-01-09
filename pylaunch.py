import sys
from Tkinter import * 
from subprocess import Popen
from os import listdir
import os
from PIL import ImageTk, Image
import cairo
import rsvg
from io import BytesIO

rn=6
execs = []
icons = []
iconpaths = []
names = []
px = []
py = []

def calcpos(w):
    isize=128
    marginy = 20
    marginx = 20
    rn = w//isize
    n=0
    global px
    px = []
    global py
    py = []
    print 'recalc '+str(rn)+' columns'
    for icon in icons:
        py.append(marginy+(n//rn)*isize)
        px.append(marginx+(n%rn)*isize)
        #print 'recalc '+icon+' n'+str(n)+' px='+str(px[-1])+' py='+str(py[-1])
        n = n+1
    global rows
    rows = n//rn
    
def genlist():
    print "gen list"
    appsdir = '/usr/share/applications/'
    apps = listdir(appsdir)

    #print 'w='+str(w)+' | rn='+str(rn) 
    for app in apps:
        iconpos = -1
        execpos = -1
        openfile = open(appsdir+app, 'r')
        contents = openfile.read()
        execpos = contents.find('Exec=')
        iconpos = contents.find('Icon=')
        namepos = contents.find('Name=')
        if execpos > 0:
            execs.append(contents[execpos+5:contents.find('\n',execpos)])
            #print 'exec='+execs[n]
            if iconpos > 0:
                icons.append(contents[iconpos+5:contents.find('\n',iconpos)])
                #print 'icon='+icons[n]
            else:
                icons.append('noicon')
                #print 'noicon'
            if namepos > 0:
                names.append(contents[namepos+5:contents.find('\n',namepos)])
                #print 'icon='+icons[n]
            else:
                name.append('noname')
                #print 'noicon'
            
        openfile = ''
        contents = ''
    print 'end genlist'
    print 'finding icons'
    iconsdirs = ['/home/gma/.icons/Numix/','/usr/share/icons/hicolor/','/usr/share/pixmaps/']
    allicons = []
    for root,dirs,files in os.walk(iconsdirs[2],topdown=True):
        for name in files:
            allicons.append(os.path.join(root, name))
    for root,dirs,files in os.walk(iconsdirs[1],topdown=True):
        for name in files:
            allicons.append(os.path.join(root, name))
    for root,dirs,files in os.walk(iconsdirs[0],topdown=True):
        for name in files:
            allicons.append(os.path.join(root, name))
            #print 'available icon '+allicons[-1]
    print 'looked up all dirs'
    for icon in icons:
        #print 'searching icon for '+icon
        iconpaths.append('x.png')
        if icon.find('/') == 0:
            iconpaths[-1] = icon
            #print 'fullpath '+iconpaths[-1]
            continue
        matches = ['x.png']
        for path in allicons:
            #print 'comparing with '+path
            #if fnmatch.filter(path, '*'+icon+'.*'):
            if path.find(icon+'.') > 0:
                #matches.append(path)
                iconpaths[-1] = path
                if path.find('16x16') < 0 and path.find('22x22') < 0 and \
                path.find('24x24') < 0 and path.find('32x32') < 0 and path.find('36x36') < 0 \
                and path.find('44x44') < 0 and path.find('48x48') < 0:
                    break
                #print icon+' matches '+matches[-1]
                #j=j+1
                
def launch(x,y):
    print str(x)+" "+str(y)
    i=0
    for app in execs:
        if x > px[i] and x < px[i]+100 and y > py[i] and y < py[i]+100 :
            print "clicou "+names[i]
            print "executar "+app
            try:
                if app.find(' ') > 0:
                    cmd = app[:app.find(' ')]
                else:
                    cmd = app
                Popen([cmd])
            except:
                print 'cannot start '+cmd
        i=i+1

def drawicons(frame):
            frame.canvas.delete(ALL)
	    print 'draw icons'
            frame.image = []
            frame.img = []
            i=0
            for icon in icons:
                if iconpaths[i][-3:] == 'svg':
                    handler= rsvg.Handle(iconpaths[i])
                    imgsvg =  cairo.ImageSurface(cairo.FORMAT_ARGB32, handler.props.width,handler.props.height)
                    ctx = cairo.Context(imgsvg)
                    #ctx.scale(64,64)
                    handler.render_cairo(ctx)
                    im = Image.frombuffer('RGBA',(handler.props.width,handler.props.height),imgsvg.get_data(),'raw','BGRA',0,1)
                else:
                    try:
                        im = Image.open(iconpaths[i])
                    except:
                        print 'cannot open '+iconpaths[i]
                try:
                    imr = im.resize((64,64),Image.BICUBIC)
                    temp = ImageTk.PhotoImage(imr)
                except:
                    temp = ImageTk.PhotoImage(Image.open('openbox.png'))
                frame.image.append(temp)
                #print 'drawing '+icon+' n'+str(i)
                frame.img.append(frame.canvas.create_image(px[i], py[i], anchor='nw', image=frame.image[i]))
                frame.canvas.create_text(px[i],py[i]+80,text=names[i], anchor='nw', fill='white', width='128')
                i=i+1

print "init"
genlist()

class Launcher(Frame):
    def __init__(self, parent=None, color='black'):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)                  
        canv = Canvas(self, bg=color, relief=SUNKEN,width=300, height=200)
        canv.config(scrollregion=(0,0,300, 1000))         
        canv.config(highlightthickness=0)                 
	
	sbar = Scrollbar(self)
        sbar.config(command=canv.yview)                   
        canv.config(yscrollcommand=sbar.set)              
        sbar.pack(side=RIGHT, fill=Y)                     

	canv.pack(side=LEFT, expand=YES, fill=BOTH)
        canv.bind("<Button-4>", self.onwheelup)
        canv.bind("<Button-5>", self.onwheeldown)
        canv.bind('<Button-1>', self.onClick)       # set event handler
        self.bind("<Configure>", self.onresize)
        self.canvas = canv

        #genlist()
	#drawicons()

    def onresize(self, event):
        width = event.width
        print 'resized to '+str(width)
        calcpos(width)
        self.canvas.config(scrollregion=(0,0,300, (rows+1)*128))
        drawicons(self)
        
    def onwheelup(self, event):
        self.canvas.yview_scroll(-1, "units")

    def onwheeldown(self, event):
        self.canvas.yview_scroll(1, "units")
        
    def onClick(self, event):                  
        launch(event.x,self.canvas.canvasy(event.y))
        quit()
	
    def quit():
        global root
        root.destroy()


if __name__ == '__main__': Launcher().mainloop()
