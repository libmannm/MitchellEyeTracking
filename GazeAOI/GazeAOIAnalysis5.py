import pandas as pd
import numpy as np
import json

class GazeAOI():
    def __init__(self, filePath,outPath):
        xL = pd.ExcelFile(filePath)
        self.outDict = {}
        global data
        data = []
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
            self.outDict[self.sheet]["LastValid"] = {}
            self.outDict[self.sheet]["Markov"] = {}
            
            self.realNums()
            self.strs()
            
            global outDict
            global gazeLoc
            outDict = self.outDict
            gazeLoc = self.gazeLoc
  
            data.append(self.df)
            #print(self.df.head())
            
        with open(outPath, "w") as outfile:
            json.dump(self.outDict, outfile, indent = 4)
            
            
    def realNums(self):
        for i,j in enumerate(self.trialIndex):
            numName = str(int(self.data[j,1]))+ "-" + str(int(self.data[j,2]))
            self.outDict[self.sheet]["Ratios"][numName] = {}
            self.outDict[self.sheet]["Markov"][numName] = {"Left":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                           "Right":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                           "NaN":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                           "Neither":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]}}
            
            timeNaN, timeNeither, timeL, timeR = 0,0,0,0

            start = int(j)
            if i < len(self.trialIndex)-1:
                end = int(self.trialIndex[i+1])
            else:
                end = len(self.gazeLoc)

            for k in range(start, end):
                if k < len(self.timeStamp)-1:
                    time = self.timeStamp[k+1] - self.timeStamp[k]
                else:
                    time = 5
                if k < len(self.gazeLoc)-1:
                    self.outDict[self.sheet]["Markov"][numName][self.NumtoStr(self.gazeLoc[k])][self.NumtoStr(self.gazeLoc[k+1])][1]+=1
                
                if self.gazeLoc[k] == -1:
                    timeNaN += time
                elif self.gazeLoc[k] == 1:
                    timeL += time
                elif self.gazeLoc[k] == 2:
                    timeR += time
                else:
                    timeNeither +=time
            for a in ["Left","Right","Neither","NaN"]:
                for b in ["Left","Right","Neither","NaN"]:
                    self.outDict[self.sheet]["Markov"][numName][a][b][0] = self.outDict[self.sheet]["Markov"][numName][a][b][1]/np.nansum(a = [self.outDict[self.sheet]["Markov"][numName][a]["Left"][1],
                                                                                                                                          self.outDict[self.sheet]["Markov"][numName][a]["Right"][1],
                                                                                                                                          self.outDict[self.sheet]["Markov"][numName][a]["NaN"][1],
                                                                                                                                          self.outDict[self.sheet]["Markov"][numName][a]["Neither"][1]])

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
            
            fullStr = []
            
            #lastLoc = self.gazeLoc[j]
            lastLoc = 5
            begTime = self.timeStamp[j]
            
            if i <len(self.trialIndex)-1:
                end = int(self.trialIndex[i+1])
            else:
                end = len(self.gazeLoc)
            
            for k in range(int(j), end):
                if self.gazeLoc[k] != lastLoc:
                    if self.skip(k) == False:
                        #print(self.skip(k))
                        time = self.timeStamp[k] - begTime
                        begTime = self.timeStamp[k]
                        valType = self.NumtoStr(self.gazeLoc[k])
                        #print(f"{valType} - {self.gazeLoc[k]}")
                        pTime = round(float(time),4)
                            
                        outStr = f"{valType}: {pTime}ms"
                        fullStr.append(outStr)
            
            outStr = []
            inc = 0
            for k,item in enumerate(fullStr):
                try:
                    if item[:2] == fullStr[k+1][:2]:
                        inc += float(item.split(": ")[1][:-2])
                    else:
                        inc += float(item.split(": ")[1][:-2])
                        ref = item.split(": ")[0]
                        outStr.append(f"{ref}: {inc}ms")
                        inc = 0
                except:
                    inc += float(item.split(": ")[1][:-2])
                    ref = item.split(": ")[0]
                    outStr.append(f"{ref}: {inc}ms")
                    inc = 0
                
            self.outDict[self.sheet]["Timeline"][numName] = outStr
            self.outDict[self.sheet]["LastLook"][numName] = outStr[-1]
            for k in range(-1,-1*len(outStr),-1):
                if "NaN" not in outStr[k] and "Neither" not in outStr[k]:
                    self.outDict[self.sheet]["LastValid"][numName] = outStr[k]
                    break
                    
            

fPath = "D:/Research/Kaiyo/PupilProcess2/GazeTrial.xlsx"
outPath = "D:/Research/Kaiyo/PupilProcess2/JsonTestMarkov2.json"
GazeAOI(fPath, outPath)