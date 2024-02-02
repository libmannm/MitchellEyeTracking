import pandas as pd
import numpy as np
import json

class GazeAOI():
    def __init__(self, filePath,outPath):
        xL = pd.ExcelFile(filePath)
        self.outDict = {}
        for sheet in xL.sheet_names:
            self.sheet = sheet
            self.outDict[self.sheet] = {}
            cols = ["Timestamp", "row", "column","GazeLoc",'TrialIndex']
            self.df = pd.read_excel(filePath, usecols= cols, sheet_name = sheet)
            self.data = self.df[["Timestamp", "row", "column","GazeLoc"]].to_numpy()
            self.trialIndex = self.df[["TrialIndex"]].to_numpy()
            self.gazeLoc = self.df[["GazeLoc"]].to_numpy()
            self.timeStamp = self.df[["Timestamp"]].to_numpy()
            i = 3
            while(self.trialIndex[i] != 0):
                i+=1
            self.trialIndex = self.trialIndex[:i]
            
            self.outDict[self.sheet]["Timeline"] = {}
            self.outDict[self.sheet]["LastLook"] = {}
            self.outDict[self.sheet]["Ratios"] = {}
            
            
            self.realNums()
            self.strs()
            
            global outDict
            outDict = self.outDict
            
        with open(outPath, "w") as outfile:
            json.dump(self.outDict, outfile, indent = 4)
            
            
    def realNums(self):
        for i,j in enumerate(self.trialIndex):
            numName = str(int(self.data[j,1]))+ "-" + str(int(self.data[j,2]))
            self.outDict[self.sheet]["Ratios"][numName] = {}
            
            timeNaN, timeNeither, timeL, timeR = 0,0,0,0
            try:
                for k in range(int(j), int(self.trialIndex[i+1])):
                    time = self.timeStamp[k+1] - self.timeStamp[k]
                    if self.gazeLoc[k] == -1:
                        timeNaN += time
                    elif self.gazeLoc[k] == 1:
                        timeL += time
                    elif self.gazeLoc[k] == 2:
                        timeR += time
                    else:
                        timeNeither +=time
            except:
                for k in range(int(j), len(self.gazeLoc)):
                    try:
                        time = self.timeStamp[k+1] - self.timeStamp[k]
                    except:
                        time = 5
                    if self.gazeLoc[k] == -1:
                        timeNaN += time
                    elif self.gazeLoc[k] == 1:
                        timeL += time
                    elif self.gazeLoc[k] == 2:
                        timeR += time
                    else:
                        timeNeither +=time
            totalTime = timeNaN + timeL + timeR + timeNeither
            self.outDict[self.sheet]["Ratios"][numName]["NaN"] = [float(100*timeNaN/totalTime),float(timeNaN)]
            self.outDict[self.sheet]["Ratios"][numName]["L"] = [float(100*timeL/totalTime),float(timeL)]
            self.outDict[self.sheet]["Ratios"][numName]["R"] = [float(100*timeR/totalTime),float(timeR)]
            self.outDict[self.sheet]["Ratios"][numName]["Neither"] = [float(100*timeNeither/totalTime),float(timeNeither)]
    
    def skip(self,i):
        retVal = True
        try:
            if self.gazeLoc[i-1] != self.gazeLoc[i+1]:
                retVal = False
        except:
            retVal = True
        return(retVal)
    
    def NumtoStr(self, num):
        if num == -1:
            return("NaN")
        if num == 0:
            return("Neither")
        if num == 1:
            return("Left")
        if num == 2:
            return("Right")
    
    def strs(self):
        for i,j in enumerate(self.trialIndex):
            numName = str(int(self.data[j,1]))+ "-" + str(int(self.data[j,2]))
            #self.outDict[self.sheet]["Ratios"][numName] = {}
            
            fullStr, lastStr = "",""
            
            lastLoc = self.gazeLoc[j]
            begTime = self.timeStamp[j]
            try:
                for k in range(int(j), int(self.trialIndex[i+1])):
                    if self.gazeLoc[k] != lastLoc:
                        if self.skip(k) == False:
                            time = self.timeStamp[k] - begTime
                            begTime = self.timeStamp[k]
                            valType = self.NumtoStr(self.gazeLoc[k])
                            pTime = round(float(time),4)
                            
                            outStr = f"{valType}: {pTime}ms; "
                            fullStr = fullStr + outStr
            except:
                for k in range(int(j), len(self.gazeLoc)):
                    if self.gazeLoc[k] != lastLoc:
                        if self.skip(k) == False:
                            time = self.timeStamp[k] - begTime
                            begTime = self.timeStamp[k]
                            valType = self.NumtoStr(self.gazeLoc[k])
                            pTime = round(float(time),4)
                            
                            outStr = f"{valType}: {pTime}ms; "
                            fullStr = fullStr + outStr
                        
            for k in range(len(fullStr)-3,0,-1):
                if fullStr[k] == ";":
                    lastStr = fullStr[k:]
                    break
                        
            self.outDict[self.sheet]["Timeline"][numName] = fullStr
            self.outDict[self.sheet]["LastLook"][numName] = lastStr
                    
            

fPath = "D:/Research/Kaiyo/PupilProcess2/GazeTrial.xlsx"
outPath = "D:/Research/Kaiyo/PupilProcess2/JsonTest.json"
GazeAOI(fPath, outPath)