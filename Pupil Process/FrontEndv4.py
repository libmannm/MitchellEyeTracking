#Mitchell Lab, 2024
#Written by Max Libmann - libmannm@oregonstate.edu
#Coordinated by Kaiyo Shi - shik@ohsu.edu

import matplotlib.pyplot as plt
import sys
import pandas as pd
from tqdm import tqdm

def runProgram(folder_path, file_path, output_name = "", export_yn = False, sheet_num = -1):
    sys.path.append(folder_path)
    from BackEndv6 import PreProcess, Analysis, exporter
    plt.rcParams['figure.dpi']= 300
    
    cols = [0,1,2,7,8,20,21,15,18,19]
    
    if sheet_num != -1:
        #prechecks
        sheet_num = sheet_num-1
        xL = pd.ExcelFile(file_path)
        sheet_name = xL.sheet_names[sheet_num]
        try:
            #ITI_path = "D:\\Research\\Kaiyo\\PupilProcess\\" + str(sheet_name[:16]) + "BehavET_ITIDat.xlsx"
            ITI_path = folder_path + "ITI\\" + str(sheet_name[:16]) + "BehavET_ITIDat.xlsx"
            df = pd.read_excel(ITI_path, usecols= [57])
            if df["Trial"].max() != 144:
                print(f"\nThe ITI data for {sheet_name} does not contain data for 144 trials")
                return(0)
        except:
            print(f"\nNo ITI for {sheet_name}")
            return(0)
        print("prechecks done")
        sample = PreProcess(file_path, sheet_num, cols)
        output = sample.returner(0)
        sheetName = sample.sheetName()
        
        A = Analysis(ITI_path, data = output)
        analyzedData = A.retTable()
        blinkLocs = A.retInputs()
        trialIndex = A.retIndex()
        
        exp_string = folder_path + output_name
        
        finalOut = exporter(analyzedData, trialIndex, blinkLocs, exp_string, sheetName, export = True)
        
        print("Done!")
    
    else:
        #TESTS TO PREVENT ERRORS
        xL = pd.ExcelFile(file_path)
        #print(xL.sheet_names)
        for i in tqdm(xL.sheet_names[1:]):
            try:
                #ITI_path = "D:\\Research\\Kaiyo\\PupilProcess\\" + str(i[:16]) + "BehavET_ITIDat.xlsx"
                ITI_path = folder_path + "ITI\\" + str(i[:16]) + "BehavET_ITIDat.xlsx"
                df = pd.read_excel(ITI_path, usecols= [57])
                if df["Trial"].max() != 144:
                    print(f"\nThe ITI data for {i} does not contain data for 144 trials")
                    return(0)
            except:
                print(f"\nNo ITI for {i}")
                return(0)
        
        print("Prechecks Done")
        
        for sheet_name in tqdm(range(len(xL.sheet_names))):
            sample = PreProcess(file_path, sheet_name, cols)
            output = sample.returner(0)
            sheetName = sample.sheetName()
            
            A = Analysis(ITI_path, data = output)
            analyzedData = A.retTable()
            blinkLocs = A.retInputs()
            trialIndex = A.retIndex()
            
            exp_string = folder_path + output_name
            
            finalOut = exporter(analyzedData, trialIndex, blinkLocs, exp_string, sheetName, export = True)
        
        print("Done!")
    
    print("Done Again")
#IF YOU ARE DOING MULTIPLE AT ONCE, MAKE SURE THE ITI PATH LIST IS CORRECT OR THERE WILL BE AN ERROR

runProgram(folder_path= 'D:\\Research\\Kaiyo\\PupilProcess2\\', 
           file_path= "D:\\Research\Kaiyo\\PupilProcess2\\smallmerge.xlsx",
           output_name= "GazeTrial",
           export_yn= True)