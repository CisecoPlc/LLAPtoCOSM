#!/usr/bin/env python

# LLAP to COSM
# dpslwk 20/03/13

import sys, time, Queue
import LLAPSerial
import eeml

class LLAPCOSM:
    def __init__(self):
        self._running = True
        self.devid = "PI"
        self.port = "/dev/ttyAMA0"
        
        #cosm details
        self.COSMMQTTServer = "api.cosm.com"
        self.COSMAPIKey ="YOUR API KEY HERE"    #<<<YOUR FEED API KEY HERE
        self.COSMFeed = 123456                  #<<<YOUR FEED NUMBER HERE
        
        self.COSMUrl = '/v2/feeds/{feednum}.xml' .format(feednum = self.COSMFeed)
        
        
        #setup serial bits
        self.queue = Queue.Queue()
        self.serial = LLAPSerial.LLAPSerial(self.queue)
    
    def __del__(self):
       pass
    
    def on_init(self):
    
        # connect serial on start
        self.serial.connect(self.port)
        print("Serial Connected")
        self._running = True
        print("Running")
    
    
    def main(self):
        if self.on_init() == False:
            self._running = False
        
        # loop
        while ( self._running ):
            try:
                self.on_loop()
            except KeyboardInterrupt:
                print("Keybord Quit")
                self._running = False
        self.disconnect_all()
            
    def disconnect_all(self):
        # disconnet serial
        self.serial.disconnect()
        
    
    def on_loop(self):
        if not self.queue.empty():
            llapMsg = self.queue.get()
            #print(llapMsg)
            devID = llapMsg[1:3]
            payload = llapMsg[3:]
            #main state machine to handle llapMsg's
            if payload.startswith('TMPA'):
                #got Temp from solar
                temp = payload[4:]
                cosm = eeml.Pachube(self.COSMUrl, self.COSMAPIKey)
                    
                #send celsius data
                cosm.update([eeml.Data(devID + "_Temperature", temp, unit=eeml.Celsius())])
                print("Cosm updated "+devID+"_Temperature with value: "+temp);
                # push data to cosm
                try:
                    cosm.put()
                except :
                    # that didnt work now what?
                    print("Failed to Send")
                
            elif payload.startswith('BATT'):
                # strip temp from llap
                voltage = payload[4:8]
                # open cosm feed
                cosm = eeml.Pachube(self.COSMUrl, self.COSMAPIKey)

                #send celsius data
                cosm.update([eeml.Data(devID + "_Voltage", voltage, unit=eeml.Unit('Volt', 'derivedSI', 'V'))])
                print("Cosm updated "+ devID +"_Voltage with value: "+voltage);
                # push data to cosm
                try:
                    cosm.put()
                except :
                    # that didnt work now what?
                    print("Failed to Send")

        
if __name__ == "__main__":
    application = LLAPCOSM()
    application.main()
