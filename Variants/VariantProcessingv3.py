import pandas as pd
import numpy as np
import os
import json

class VariantProcess():
    def __init__(self, dataPath, referencePath,output, seconds = 0):
        if "Letter" in referencePath:
            self.refdf = pd.read_csv(referencePath, usecols=["TrialISI","StimDur","letter_disp.started"])
        else:
            self.refdf = pd.read_csv(referencePath, usecols=["TrialISI","StimDur","arrow_disp.started"])
        self.refdf = self.refdf.to_numpy()
        self.data = pd.read_csv(dataPath, usecols = ["Timestamp","ET_PupilLeft","ET_PupilRight"]).to_numpy()
        fileID = dataPath.split("\\")[-1][4:7]
        if "Letter" in referencePath:
            fileID = fileID + "L"
        elif "Arrow" in referencePath:
            fileID = fileID + "A"
        else:
            print("ISSUE")
            exit()
        
        self.output = output
        self.output[fileID] = {"Dilated":{"750 - 800":[],"750 - 400":[],"750 - 200":[],"1000 - 800":[],"1000 - 400":[],"1000 - 200":[]},
                               "BaselineAve":{"750 - 800":[],"750 - 400":[],"750 - 200":[],"1000 - 800":[],"1000 - 400":[],"1000 - 200":[]},
                               "Total":{"750 - 800":[],"750 - 400":[],"750 - 200":[],"1000 - 800":[],"1000 - 400":[],"1000 - 200":[]},
                               "Truncated":{"750 - 800":[],"750 - 400":[],"750 - 200":[],"1000 - 800":[],"1000 - 400":[],"1000 - 200":[]}}   
        
        self.startTrial = [0]
        self.endTrial = []
        
        for i,row in enumerate(self.refdf):
            if row[0]*0 != 0 and self.refdf[i-1,2]*0 == 0:
                #print(self.refdf[i-1,2])
                self.startTrial.append(i+1)
                self.endTrial.append(i)
        
        self.newTrial = self.startTrial[:-1]
        
        print(f"AAA {self.newTrial}")
        
        self.baseline()
        
        self.numNames = []
        for i in self.newTrial:
            try:
                self.numName = str(int(self.refdf[i,0]))+" - " + str(int(self.refdf[i,1]))
            except:
                self.numName = str(int(self.refdf[i-5,0]))+" - " + str(int(self.refdf[i-5,1]))
            self.numNames.append(self.numName)
            
        self.startTimes = []
        self.endTimes = []
        self.fullTimes = []
        
        if seconds != 0:
            for k,endIndex in enumerate(self.endTrial):
                #print(endIndex)
                self.startTimes.append((self.refdf[endIndex-1,2]-seconds)*1000)
                self.endTimes.append((self.refdf[endIndex-1,2])*1000)
                self.fullTimes.append((self.refdf[self.newTrial[k],2])*1000)
        else:
            for k,endIndex in enumerate(self.endTrial):
                #print(endIndex)
                self.startTimes.append((self.refdf[self.newTrial[k],2])*1000)
                self.endTimes.append((self.refdf[endIndex-1,2])*1000)
        
        global starts
        global ends
        starts = self.startTimes
        ends = self.endTimes
        
        #print(self.startTimes)
        #print(self.endTimes)
        print(f"BBB {self.startTrial}")
        
        self.indeces = self.convertRef([self.startTimes,self.endTimes])
        print(self.indeces)
        for i,j in enumerate(self.indeces):
            subsect = self.data[int(j[0]):int(j[1]),1:2]
            #subsectFull = self.data[int()]
            self.output[fileID]["Dilated"][self.numNames[i]].append(np.nanmean(subsect)-self.baseline[i])
            self.output[fileID]["BaselineAve"][self.numNames[i]].append(self.baseline[i])
            self.output[fileID]["Truncated"][self.numNames[i]].append(np.nanmean(subsect))
        
        if seconds != 0:
            self.indecesFull = self.convertRef([self.fullTimes,self.endTimes])
            for i,j in enumerate(self.indecesFull):
                subsect = self.data[int(j[0]):int(j[1]),1:2]
                self.output[fileID]["Total"][self.numNames[i]].append(np.nanmean(subsect))    
                
    def baseline(self):
        self.baseline = []
        for i in self.newTrial:
            endTime = 1000*self.refdf[i,2]
            startTime = endTime - 5000
            #print(f"{startTime} - {endTime}")
            j = 0
            while self.data[j,0] < startTime:
                j+=1
            startIndex = j
            j = 0
            while self.data[j+1,0] < endTime:
                j+=1
            endIndex = j
            self.baseline.append(np.nanmean(self.data[startIndex:endIndex,1:3]))
        print(self.baseline)
        
    def convertRef(self, refIndeces):
        tempInd = np.zeros((len(refIndeces[0]),2))

        for i,array in enumerate(refIndeces):
            for k,index in enumerate(array):
                j = 0
                while self.data[j,0] < index:
                    j+=1
                under = j-1
                over = j
                if abs(self.data[under,0]-index) > abs(self.data[over,0]-index):
                    tempInd[k,i] = int(over)
                else:
                    tempInd[k,i] = int(under)
        return(tempInd)
    
    def returner(self):
        return(self.output)
        
    
        
dataPath = ["D:\\Research\\Kaiyo\\Variants\\Variant Raw Sensor Data\\001_109CE Letter 03-08-22 14h22mfiltered.csv",
            "D:\\Research/Kaiyo\\Variants\\Variant Raw Sensor Data\\002_109CE Arrow 03-08-22 13h41mfiltered.csv"]
referencePath = ["D:\\Research\\Kaiyo\\Variants\\Variant Raw Sensor Data\\Timestamps\\LetterTask_109CE_3_1_2022_Aug_03_1425.csv",
                 "D:\\Research\\Kaiyo\\Variants\\Variant Raw Sensor Data\\Timestamps\\Arrow_ArrowRV_109CE_4_1_2022_Aug_03_1345.csv"]
time = 25
#Use if new
#f = open("D:\\Research\\Kaiyo\\Variants\\25Seconds.json")
#dictionary = json.load(f)
#f.close()

#dictionary = {"Participant":[],"750 - 800":[],"750 - 400":[],"750 - 200":[],"1000 - 800":[],"1000 - 400":[],"1000 - 200":[]}

dictionary = {}


for i in range(len(dataPath)):
    A = VariantProcess(dataPath[i], referencePath[i], dictionary, seconds = 23)
    dictionary = A.returner()


with open("D:\\Research\\Kaiyo\\Variants\\Variant Raw Sensor Data\\23Seconds2.json", "w") as outfile:
    json.dump(dictionary, outfile, indent = 4)