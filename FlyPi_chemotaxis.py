import Tkinter as tk
import time
import os
from gpiozero import LED
import io

serialAvail = False
class flypiApp:
    #filepath for output:
    basePath = '/home/pi/Desktop/flypi_output/'

####### use these flags to make whole pieces of the GUI disappear ######
    cameraFlag = 1
    ringFlag = 0
    led1Flag = 1
    led2Flag = 1
    matrixFlag = 0
    peltierFlag= 0
    protocolFlag = 0
    quitFlag = 1

###### Address for all arduino components #########
    ##LED1##
    led1OnAdd="31"
    led1OffAdd="32"
    led1ZapDurAdd="34000"

    ##LED2##
    led2OnAdd="35"
    led2OffAdd="36"
    led2ZapDurAdd="38000"

    ##MATRIX##
    matOnAdd="39"
    matOffAdd="40"
    matPat1Add="41"
    matPat2Add="42"
    matBrightAdd="43000"


    ##RING##
    ringOnAdd="44"
    ringOffAdd="45"
    ringZapAdd="52000"
    ringRedAdd="49000"
    ringGreenAdd="50000"
    ringBlueAdd="46000"
    ringAllAdd="51000"
    ringRotAdd="47500"

    ##PELTIER##
    peltOnAdd="53"
    peltOffAdd="54"
    peltTempAdd="55000"

    ##PELTIER##
    peltOnAdd="53"
    peltOffAdd="54"
    peltTempAdd="55000"
    showCaptureBackground=1

    def __init__(self,master,ser=""):
        ###create the mainframe####
        #self.frame = tk.Frame()
        #self.frame.grid(row=0,column=0,rowspan=1,columnspan=1)

        #create base path for storing files, temperature curves, etc:
        if not os.path.exists(self.basePath):
            #os.chdir('/home/pi/Desktop/')
            os.mkdir(self.basePath)
            os.chown(self.basePath,1000,1000)

        ##create the mainframe
        frame = tk.Frame()
        frame.grid(row=0,column=0,rowspan=1,columnspan=1)
        row4Frame = tk.Frame(master=frame,bd=2,relief="ridge")
        row1Frame = tk.Frame(master=frame,bd=2,relief="ridge")
        row2Frame = tk.Frame(master=frame,bd=2,relief="ridge")
        row3Frame = tk.Frame(master=frame,bd=2,relief="ridge")

        #self.var=0
        if serialAvail==True:
            #self.ser = serial.Serial('/dev/ttyACM0', 115200) # for Arduino Uno from RPi
            self.ser = serial.Serial('/dev/ttyUSB0', 115200) # for Arduino Nano from RPi

        ##### show the pieces of the GUI depending on which flags are on (see above) #####
        if self.protocolFlag==1:
            self.frameProt = tk.Frame(master=row4Frame,bd=3,relief="ridge")
            self.frameProt.pack(side="top")
            self.protocol=Protocol(parent=self.frameProt,ser=self.ser)
            #protLabel=tk.Label(master=self.frameProt,text="PROTOCOL: ")
            #protLabel.grid(row=0,column=0,columnspan=2,sticky="NW")

        else:
            self.frameProt=""

        ### Camera ###
        if self.cameraFlag==1:
            self.frameCam = tk.Frame(master=row2Frame,bd=3)
            self.frameCam.pack(side="top")#.grid(row=2,column=0,columnspan=5,rowspan=1,sticky="NW")
            self.Camera=Camera(parent=self.frameCam,label="CAMERA")

        if self.led1Flag==1:
            self.frameLed1 = tk.Frame(row1Frame,bd=3)
            self.frameLed1.grid(row=0,column=0,sticky="NW")
            self.LED1=LED_CONTROL(parent=self.frameLed1, label="Stim Light", gpio_pin=18)

        if self.led2Flag==1:
            self.frameLed2 = tk.Frame(row1Frame,bd=3)
            self.frameLed2.grid(row=0,column=2,sticky="NW")
            self.LED2=LED_CONTROL(parent=self.frameLed2, label="Back Light", gpio_pin=17)            
##
##            self.LED1=LED(parent = self.frameLed1,label="LED 1",
##                          onAdd=self.led1OnAdd,offAdd=self.led1OffAdd,
##                          zapDurAdd=self.led1ZapDurAdd,ser = self.ser)
##            self.ser.write(self.led1OffAdd.encode('utf-8'))

        if self.ringFlag==1:
            self.frameRing = tk.Frame(row1Frame,bd=3)
            self.frameRing.grid(row=1,column=0,sticky="NW",columnspan=3,rowspan=1)
            self.Ring = Ring(self.frameRing,label="RING",protFrame=self.frameProt,
                             ringOnAdd=self.ringOnAdd,ringOffAdd=self.ringOffAdd,
                             ringZapAdd=self.ringZapAdd,redAdd=self.ringRedAdd,
                             greenAdd=self.ringGreenAdd,blueAdd=self.ringBlueAdd,
                             allAdd=self.ringAllAdd,rotAdd=self.ringRotAdd,ser=self.ser)
            self.ser.write(self.ringOffAdd.encode('utf-8'))
            
        if self.quitFlag ==1:
            self.frameQuit = tk.Frame(master=frame)
            self.frameQuit.grid(row=5,column=2,sticky="NW")
            self.quitAPP(parent=self.frameQuit)

        #draw all frames on screen
        row4Frame.grid(row=5,column=0,sticky="NWE",columnspan=1)#pack(side="top",fill="x")
        row1Frame.grid(row=1,column=0,sticky="NWE",columnspan=1)#pack(side="top",fill="x")
        row3Frame.grid(row=0,column=2,sticky="NWE")#pack(after=row1Frame,side="right",fill="x")
        row2Frame.grid(row=0,column=0,sticky="NWE",columnspan=1)#pack(fill="x")
        #send starting code to arduino
        #startCode="99*"
        #self.ser.write(startCode.encode("utf-8"))

############### QUIT #########################
    def quitAPP(self,parent="none"):
        ##callback to close the program and close serial port
        def quitNcloseSerial():
            if serialAvail==True:
                self.ser.flush()
                self.ser.close()
            self.quit.quit()

        #self.rowCount=self.rowCount+1
        self.quit = tk.Button(parent,text="QUIT", fg="red", command=quitNcloseSerial)
        self.quit.pack(fill="x")#(row=self.rowCount,column=self.columnCount)


class Camera:
    def __init__(self,parent="none",label="CAMERA"):
        import Tkinter as tk
        try:
            import picamera # picamera module
            import picamera.array
            self.cam = picamera.PiCamera()
            self.stream = picamera.array.PiRGBArray(self.cam)
            self.cam.led = False
            self.cam.exposure_mode = "fixedfps"
            self.cam.exposure_compensation = 0
            self.cam.brightness = 50
            self.cam.awb_mode="auto"
        except ImportError:
            print ("picamera module not available!")

        self.camParent=parent
        self.autoExpVar = tk.IntVar()

        self.flipVar = tk.IntVar()
        self.flipVal = 0

        self.zoomVar = tk.DoubleVar(value=1.0)
        self.zoomVal = 1.0
        self.FPSVar = tk.IntVar()
        self.FPSVal = 15

        self.binVar = tk.IntVar()
        self.binVal = 0

        self.sizeVar = tk.IntVar()
        self.sizeVal = 180
        self.horVar = tk.DoubleVar()
        self.horVal = 1
        self.verVar = tk.DoubleVar()
        self.verVal = 1
        self.brightVar = tk.IntVar()
        self.brightVal = 50
        self.contVar = tk.IntVar()
        self.contVal = 50
        self.expVar = tk.IntVar()
        self.expVal = 0
        self.rotVar = tk.IntVar()
        self.rotVal = 0

        ### frames for all camera controls ###
        self.camFrame1=tk.Frame(master=self.camParent,bd=2)
        self.camFrame1.grid(row=0,column=0,columnspan=1,rowspan=2,sticky="N")

        frame2=tk.Frame(master=self.camParent,bd=2)
        frame2.grid(row=0,column=1,sticky="NW",columnspan=2)

        frame3=tk.Frame(master=frame2,bd=2,relief="ridge")
        frame3.grid(row=3,column=1,columnspan=2,rowspan=2,sticky="NW")

        #### variables for the dropdown menus ####
        self.camAWVar = tk.StringVar(master=self.camFrame1)
        self.camAWVal = "auto"
        self.camModVar = tk.StringVar(master=self.camFrame1)
        self.camColEffVar = tk.StringVar(master=self.camFrame1)
        self.camColEffVal = "NONE"
        self.resVar = tk.StringVar()
        self.resVal = "800x800"

        self.label=label
        #self.parent = parent

        self.camLabel = tk.Label(master=self.camFrame1,text = self.label)
        self.camLabel.pack()#grid(row = 0, column = 0,sticky="W")

        self.camOnButt=self.camButton(parent=self.camFrame1, rowIndx=1,colIndx=0,fill="x", buttText="ON",color="green",func=self.camOn)
        self.camOffButt=self.camButton(parent=self.camFrame1,rowIndx=1,colIndx=1,fill="x",buttText="OFF",color="red",func=self.camOff)

        self.camResLabel = tk.Label(master=self.camFrame1,text = " Resolution ")
        self.camResLabel.pack(fill="x")#grid(row=3, column=0,sticky="WE")
        self.camResMenu = tk.OptionMenu(self.camFrame1,self.resVar,'2592x1944','1920x1080','1296x972','1296x730','1280x1280','1000x1000','800x800','640x640','640x480')
        self.resVar.set("800x800")
        self.camResMenu.pack(fill="x")#grid(row=4,column=0,columnspan=2,sticky="WE")
        self.camResMenu.pack_propagate(flag=False)
        self.camAWLabel = tk.Label(master=self.camFrame1,text = " White balance ")
        self.camAWLabel.pack(fill="x")#grid(row=3, column=0,sticky="WE")
        self.camAWMenu = tk.OptionMenu(self.camFrame1,self.camAWVar,'off','auto','green','red','blue','sunlight','cloudy','shade','tungsten','fluorescent','incandescent','flash','horizon')
        self.camAWVar.set("auto")
        self.camAWval="auto"
        self.camAWMenu.pack(fill="x")#grid(row=4,column=0,columnspan=2,sticky="WE")
        self.camAWMenu.pack_propagate(flag=False)

        self.camModLabel = tk.Label(master=self.camFrame1,text = "Mode")
        self.camModLabel.pack(fill="x")#grid(row=5, column=0,sticky="W")
        self.camModes = tk.OptionMenu(self.camFrame1,
                                      self.camModVar,
                                      "none","negative","solarize","sketch",
                                      "denoise","emboss","oilpaint","hatch",
                                      "gpen","pastel","watercolor","film",
                                      "blur","saturation","colorswap","washedout",
                                      "posterise","colorpoint","colorbalance","cartoon",
                                      "deinterlace1","deinterlace2")

        #self.camModes.setvar("none")
        self.camModVar.set("none")
        #self.camModes.pack_propagate(flag=False)
        self.camModes.pack(fill="x")#grid(row=6,column=0,columnspan=2,sticky="WE")

        self.camColEffLabel = tk.Label(master=self.camFrame1,text = "color effect")
        self.camColEffLabel.pack(fill="x")#grid(row=3, column=2,sticky="W")
        self.camColEff = tk.OptionMenu(self.camFrame1,self.camColEffVar,"NONE","RED","GREEN","BLUE","BW")
        self.camColEff.pack(fill="x") #grid(row=4,column=2,columnspan=1,sticky="WE")
        self.camColEffVar.set("BW")
        self.camColEff.pack_propagate(flag=False)


        self.camFPS=self.camSlider(parent=frame2,  label_="FPS",
                                   var=self.FPSVar,len=90,
                                   rowIndx=1,colIndx=2,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=15,to__=90,res=5,set_=15)

        self.camBin=self.camSlider(parent=frame2,  label_="Binning",
                                   var=self.binVar,len=90,
                                   rowIndx=0,colIndx=2,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=0,to__=4,res=2,set_=0)

        self.camSize=self.camSlider(parent=frame2,  label_="Window size",
                                   var=self.sizeVar,
                                   rowIndx=0,colIndx=0,sticky="",
                                   orient_="horizontal",len=90,
                                   colSpan=1,from__=180,to__=800,res=10,set_=500)

        self.camZoon=self.camSlider(parent=frame2,  label_="Digi Zoom",
                                   var=self.zoomVar,len=90,
                                   rowIndx=0,colIndx=1,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=1,to__=10,res=1,set_=1.0)


        self.camHor=self.camSlider(parent=frame2,  label_="Horiz. Offset",
                                   var=self.horVar,len=90,
                                   rowIndx=1,colIndx=0,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=1,to__=100,res=5,set_=1)


        self.camVer=self.camSlider(parent=frame2,  label_="Verti. Offset",
                                   var=self.verVar,len=90,
                                   rowIndx=1,colIndx=1,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=1,to__=100,res=5,set_=1)

        self.camBright=self.camSlider(parent=frame2,  label_="Brightness",
                                   var=self.brightVar,len=90,
                                   rowIndx=2,colIndx=0,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=0,to__=100,res=5,set_=50)


        self.camCont=self.camSlider(parent=frame2,  label_="Contrast",
                                   var=self.contVar,len=90,
                                   rowIndx=2,colIndx=1,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=0,to__=100,res=5,set_=50)

        self.camExp=self.camSlider(parent=frame2,  label_="Exposure",
                                   var=self.expVar,len=90,
                                   rowIndx=2,colIndx=2,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=-25,to__=25,res=5,set_=0)


        self.camRot=self.camSlider(parent=frame2,  label_="Rotation",
                                   var=self.rotVar,len=90,
                                   rowIndx=3,colIndx=0,sticky="",
                                   orient_="horizontal",
                                   colSpan=1,from__=0,to__=270,res=90,set_=0)


        self.autoExposure = tk.Checkbutton(master=frame2,
                                           text="auto expos.",
                                           variable = self.autoExpVar,
      	                                     onvalue=1,offvalue=0)#,
                                           #command=self.autoExpVar.get)
        self.autoExpVar.set(1)
        self.autoExposure.grid(row=4, column=0,sticky="N")


        self.flip = tk.Checkbutton(master=frame2,text="Flip image",variable = self.flipVar,onvalue=1,offvalue=0) #command=self.flipVar.get)
        self.flipVar.set(0)
        self.flip.grid(row=4, column=0,sticky="S")

        #########Time lapse/video/photo####################
        self.TLLabel=tk.Label(master=frame3,text="TIME LAPSE")
        self.TLLabel.grid(row=2,column=0,sticky="N")
        self.TLdur = tk.Entry(master=frame3,width=8)
        self.TLdur.grid(row=3,column=1,sticky="WN")
        self.TLdur.insert(0,0)

        self.TLdurLabel=tk.Label(master=frame3,text="Duration (sec)")
        self.TLdurLabel.grid(row=2,column=1,sticky="W")

        self.TLinter = tk.Entry(master=frame3,width=8)
        self.TLinter.insert(0,0)
        self.TLinter.grid(row=5,column=1,sticky="NW")

        self.TLinterLabel=tk.Label(master=frame3,text="fps (Hz)")
        self.TLinterLabel.grid(row=4,column=1,sticky="W")

        self.camRecButt=tk.Button(master=frame3,text="Video",fg="black",command=self.camRec)
        self.camRecButt.grid(row=3,column=0,sticky="WEN")

        self.camTLButt=tk.Button(master=frame3,text="Timelapse",fg="black",command=self.camTL)
        self.camTLButt.grid(row=4,column=0,sticky="WES")

        self.camSnapButt=tk.Button(master=frame3,text="Photo",fg="black",command=self.camSnap)
        self.camSnapButt.grid(row=5,column=0,sticky="WEN")

##        self.camGetBG=tk.Button(master=frame3,text="Capture Background",fg="black",command=self.captureBackground)
##        self.camGetBG.grid(row=5,column=0,sticky="WEN")
        
        ####callback for menus
        self.camGetMenus()

    ########callback for menus
    def camGetMenus(self):
        #this is a recursive function that will call itself
        #with a minimum interval of 700ms.
        #upon calling it will get the value of three variables
        #white balance, mode and color effect
        self.camFrame1.after(700, self.camGetMenus)

        if self.cam.awb_mode != self.camAWVar.get():
           self.camAWVal = self.camAWVar.get()
           if self.camAWVal != "":
               if self.camAWVal == "green":
                   self.cam.awb_mode = "off"
                   self.cam.awb_gains = (1,1)
               elif self.camAWVal == "red":
                   self.cam.awb_mode = "off"
                   self.cam.awb_gains = (8.0,0.9)
               elif self.camAWVal == "blue":
                   self.cam.awb_mode = "off"
                   self.cam.awb_gains = (0.9,8.0)
               elif self.camAWVal == "off":
                   self.cam.awb_mode = "off"

               else:
                   self.cam.awb_mode = self.camAWVal

        if self.cam.image_effect != self.camModVar.get():
          self.camModVal = self.camModVar.get()
          if self.camModVal != "":
              self.cam.image_effect = self.camModVal

        if self.camColEffVal != self.camColEffVar.get():
           self.camColEffVal = self.camColEffVar.get()
           if self.camColEffVal != "":
               if self.camColEffVal == "BW":
                   self.cam.color_effects = (128,128)
               elif self.camColEffVal == "RED":
                   self.cam.color_effects = (0,255)
               elif self.camColEffVal == "BLUE":
                   self.cam.color_effects = (255,0)
               elif self.camColEffVal == "GREEN":
                   self.cam.color_effects = (0,0)
               else:
                   self.cam.color_effects = None
        #ce = self.camColEffVar.get()

        autoExp= self.autoExpVar.get()
        if autoExp==0:
            self.cam.exposure_mode="off"
        else:
            self.cam.exposure_mode="auto"

        #flip= self.flipVar.get()
        #print(type(flip1))
        if self.flipVal != self.flipVar.get():
            self.flipVal=self.flipVar.get()
            if self.flipVal==1:
                self.cam.hflip=True
            else:
                self.cam.hflip=False

        #if self.binVal!=self.binVar.get():
        #    self.binVal=self.binVar.get()
        #    if self.binVal==0:
        #
        #    self.cam.binning=(self.binVal)

        if self.FPSVal!=self.FPSVar.get():
            self.FPSVal=self.FPSVar.get()
            self.cam.framerate=(self.FPSVal)

        if self.brightVal!=self.brightVar.get():
            self.brightVal=self.brightVar.get()
            self.cam.brightness=(self.brightVal)

        if self.contVal!=self.contVar.get():
            self.contVal=self.contVar.get()
            self.cam.contrast=(self.contVal)

        if self.expVal!=self.expVar.get():
            self.expVal=self.expVar.get()
            self.cam.exposure_compensation=(self.expVal)

        if self.sizeVal!=self.sizeVar.get():
            self.sizeVal=self.sizeVar.get()
            self.cam.preview_window = (0,0,self.sizeVal,self.sizeVal)

        if self.rotVal!=self.rotVar.get():
            self.rotVal=self.rotVar.get()
            self.cam.rotation = self.rotVal

        if self.resVal!=self.resVar.get():
            self.resVal=self.resVar.get()
            if self.resVal == "2592x1944":
                self.cam.resolution=(2592,1944)
                self.cam.framerate=(15)
                self.FPSVar.set(15)
                self.binVar.set(0)
            if self.resVal == "1920x1080":
                self.cam.resolution=(1920,1080)
                self.cam.framerate=(30)
                self.FPSVar.set(30)
                self.binVar.set(0)
                self.zoomVar.set(3)
            if self.resVal == "1296x972":
                self.cam.resolution=(1296,972)
                self.cam.framerate=(42)
                self.FPSVar.set(42)
                self.binVar.set(2)
            if self.resVal == "1296x730":
                self.cam.resolution=(1296,730)
                self.cam.framerate=(49)
                self.FPSVar.set(49)
                self.binVar.set(2)
            if self.resVal == "1280x1280":
                self.cam.resolution=(1280,1280)
                self.cam.framerate=(30)
                self.FPSVar.set(30)
                self.binVar.set(2)
            if self.resVal == "1000x1000":
                self.cam.resolution=(1000,1000)
                self.cam.framerate=(30)
                self.FPSVar.set(30)
                self.binVar.set(2)
            if self.resVal == "800x800":
                self.cam.resolution=(800,800)
                self.cam.framerate=(30)
                self.FPSVar.set(30)
                self.binVar.set(2)    
            if self.resVal == "640x640":
                self.cam.resolution=(640,640)
                self.cam.framerate=(75)
                self.FPSVar.set(75)
                self.binVar.set(4)                
            if self.resVal == "640x480":
                self.cam.resolution=(640,480)
                self.cam.framerate=(90)
                self.FPSVar.set(90)
                self.binVar.set(4)

        if self.zoomVal!=self.zoomVar.get() or self.horVal!=self.horVar.get() or self.verVal!=self.verVar.get():
            self.zoomVal=self.zoomVar.get()
            self.horVal=self.horVar.get()
            self.verVal=self.verVar.get()
            if self.zoomVal==1:
                self.cam.zoom=(0,0,1,1)
                self.horVar.set(0)
                self.verVar.set(0)
            else:
                zoomSide=1/self.zoomVal
                edge=1-zoomSide
                self.cam.zoom=((self.horVal/100.0)*edge,
                               (self.verVal/100.0)*edge,
                               1/self.zoomVal,
                               1/self.zoomVal)

        #print ("white bal: "+ aw)
        #print("color effect: " +ce)
        #print("cam mode: " +cm)
        #print("auto Exp: "+str(autoExp))
        #print("flip: "+str(flip1))

    #general function to create buttons
    def camButton(self,parent="none",fill="",side="top",rowIndx=1,colIndx=0,sticky="",buttText="button",color="black",func="none"):
        button = tk.Button(master=parent,text = buttText, fg = color, command = func)
        button.pack(fill=fill,side=side)
        #grid(row=rowIndx,column=colIndx,sticky=sticky)


    #general function for slider
    def camSlider(self,parent="none",  label_="empty",len=90,var="",rowIndx=1,colIndx=0,sticky="",orient_="vertical",colSpan=1,from__=100,to__=0,res=1,set_=0):
        Slider = tk.Scale(master=parent,from_=from__,to=to__,resolution=res,label=label_,length=90,variable=var,orient=orient_)
        Slider.set(set_)
        Slider.grid(row=rowIndx,column=colIndx,columnspan=colSpan)

    ###########callbacks for buttons#######
    def camOn(self):
        print ("cam on")
        res=self.resVar.get()
        size=self.sizeVar.get()
        self.cam.resolution=(800,800)
        self.cam.preview_window = (200,200,size,size)
        self.zoomVar.set(1)
        self.horVar.set(0)
        self.verVar.set(0)
        self.cam.zoom=(self.horVar.get(),self.verVar.get(),self.zoomVar.get(),self.zoomVar.get())
        self.cam.start_preview()
        self.cam.preview.fullscreen = False

    def camOff(self):
        print ("cam Off")
        self.cam.stop_preview()

    def camRec(self):
        dur=self.TLdur.get()
        videoPath=flypiApp.basePath+'/videos/'
        if not os.path.exists(videoPath):
            #if not, create it:
            os.makedirs(videoPath)
            os.chown(videoPath,1000,1000)

        #print ("recording for: " +dur+ " secs" )
        
        self.cam.start_recording(videoPath+'video_'+time.strftime('%Y-%m-%d-%H-%M-%S')+'.h264')
        self.cam.wait_recording(int(dur))
        self.cam.stop_recording()

    def filenames(self, shots, tlPath, tlFold):
        frameIndex = 0
        while frameIndex < shots:
            yield tlPath+tlFold+'/TL_image_%04d.jpg' % frameIndex
            frameIndex += 1

    def camTL(self):
        dur=self.TLdur.get()
        interval = self.TLinter.get()
        tlPath=flypiApp.basePath+'/time_lapse/'

        #check to see if the time lapse output folder is present:
        if not os.path.exists(tlPath):
            #if not, create it:
            os.makedirs(tlPath)
            os.chown(tlPath,1000,1000)

        #get the present time, down to seconds
        tlFold=time.strftime("%Y-%m-%d-%H-%M-%S")

        #make a new folder to store all time lapse photos
        os.makedirs(tlPath+tlFold)
        os.chown(tlPath+tlFold,1000,1000)
        #os.chdir(tlPath+tlFold)

####        shots=int(int(dur)/int(interval))
        shots=int(float(dur)*float(interval))

        try:
            self.cam.framerate = float(interval)+shots*0.000
            # Give the camera some warm-up time
            time.sleep(2)
            start = time.time()
            self.cam.capture_sequence(self.filenames(shots,tlPath, tlFold), use_video_port=True)
            finish = time.time()
            print('Total Elapsed Time %.2f' % (finish - start))
            print('Captured %d frames at %.2f fps' % (shots, shots / (finish - start)))

##                print('time lapse:')
##                print('number of shots: '+ str(shots))
##                self.cam.framerate = int(interval)+2
##                # Wait for the automatic gain control to settle
##                # Now fix the values
##                self.cam.shutter_speed = self.cam.exposure_speed
##                print("Exposure Speed", self.cam.exposure_speed)
##                start = time.time()
##                self.cam.capture_sequence([tlPath+tlFold+'/TL_image_%02d.jpg' % i for i in range(shots)], use_video_port=True)
##                finish = time.time()
##                
##                # How fast were we?
##                print('Captured %d images at %.2f fps' % (i+1, (i+1) / (finish - start))) 
            print("done.")
        except KeyboardInterrupt:
            print("Recording is interupted.")

                

        #print("timeLapse:")
        #print("duration " + dur)
        #print("interval "+interval)

    def camSnap(self):
        photoPath=flypiApp.basePath+'/snaps/'
        #check to see if the snap output folder is present:
        if not os.path.exists(photoPath):
            #if not, create it:
            os.makedirs(photoPath)
            os.chown(photoPath,1000,1000)

        #get the present time, down to seconds
        #print (time.strftime("%Y-%m-%d-%H-%M-%S"))
        # Camera warm-up time
        time.sleep(2)
        self.cam.capture(photoPath+'snap_'+time.strftime("%Y-%m-%d-%H-%M-%S")+'.jpg')

##    def captureBackground(self):
##        self.cam.capture(self.stream, format='bgr')
##        im = self.stream.array
##        imgr = cv2.cvtColor(im, cv2.cv.CV_BGR2GRAY)
##        avg2 = np.float32(imgr)
##        for x in range(0,4):
##            im = self.stream.array
##            imgr = cv2.cvtColor(im, cv2.cv.CV_BGR2GRAY)
##            cv2.accumulateWeighted(imgr,avg2,0.01)
##            res2 = cv2.convertScaleAbs(avg2)
##        self.bk = res2

class LED_CONTROL:
    def __init__(self, parent="none", label="LED", gpio_pin = 23):
        self.led = LED(gpio_pin)
        self.label=label
        self.ledLabel = tk.Label(master=parent,text = self.label)
        self.ledLabel.pack()#grid(row = 0, column = 0)
##        self.ser=
                        
        self.ledOnButt = tk.Button(master=parent,text = "ON", fg = "green", command = self.ledOn)
        self.ledOnButt.pack(fill="x")
        
        self.ledOffButt = tk.Button(master=parent,text = "OFF", fg = "RED", command = self.ledOff)
        self.ledOffButt.pack(fill="x")        
##
##        self.ledZapTime = tk.Entry(master=parent,width=10)
##        self.ledZapTime.insert(0,"zap in ms")
##        self.ledZapTime.pack(fill="x")
##        
##        self.ledZapButt = tk.Button(master=parent,text = "ZAP!", command = self.ledZap)
##        self.ledZapButt.pack(fill="x")        
 
    #callbacks for LED
    def ledOn(self):
        self.led.on()
        
    def ledOff(self):
        self.led.off()
        
##    def ledZap(self):
##        time = self.ledZapTime.get()
##        if time=="zap in ms":
##            time=0
##            print ("you didn't set a value!")
##        time=int(time)
##        time = str(int(self.zapDurAddress)+time)
##        self.ser.write(time.encode("utf-8")+"*")
##        print(self.label+" ZAP for "+time[1:])


root = tk.Tk()
root.title("Fly Pi 0.99")

dummie = flypiApp(root)

#dummie.title("test")
root.resizable(width=False, height=False)
root.mainloop()

root.destroy()
