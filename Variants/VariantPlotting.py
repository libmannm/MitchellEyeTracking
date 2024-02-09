import json
import matplotlib.pyplot as plt

f = open("M:\\Research\\Kaiyo\\Variants\\Variant Raw Sensor Data\\2-8Update\\23SecondOutput.json")
data = json.load(f)

fig, ax = plt.subplots(2,3, figsize = (15,10))

x = [0,1,2,0,1]
y = [0,1,0,1,0]

keys = list(data.keys())

Akeys = []
Lkeys = []

for a in keys:
    if "A" in a:
        Akeys.append(a)
    if "L" in a:
        Lkeys.append(a)


print(Akeys)

for j, vals in enumerate(Akeys):
    #print(j)
    #print(vals)
    #print(j)
    dilated = []
    total = []
    baseline = []
    trunc = []
    axis = [0,1,2,3,4,5]
    
    for i in data[vals]["Order"]:
        #print(i)
        dilated.append(data[vals]["Dilated"][i][0])
        total.append(data[vals]["Total"][i][0])
        baseline.append(data[vals]["BaselineAve"][i][0])
        trunc.append(data[vals]["Truncated"][i][0])
        
    ax[y[j],x[j]].plot(axis,dilated, label = "Dilated")
    ax[y[j],x[j]].plot(axis,total, label = "Total")
    ax[y[j],x[j]].plot(axis,baseline, label = "Baseline")
    ax[y[j],x[j]].plot(axis,trunc, label = "Truncated")
    ax[y[j],x[j]].set_title(vals)
    #print(j)
ax[0,0].legend()
fig.tight_layout()

fig2, ax2 = plt.subplots(2,3, figsize = (15,10))

for j, vals in enumerate(Lkeys):
    #print(j)
    #print(vals)
    #print(j)
    dilated = []
    total = []
    baseline = []
    trunc = []
    axis = [0,1,2,3,4,5]
    
    for i in data[vals]["Order"]:
        #print(i)
        dilated.append(data[vals]["Dilated"][i][0])
        total.append(data[vals]["Total"][i][0])
        baseline.append(data[vals]["BaselineAve"][i][0])
        trunc.append(data[vals]["Truncated"][i][0])
        
    ax2[y[j],x[j]].plot(axis,dilated, label = "Dilated")
    ax2[y[j],x[j]].plot(axis,total, label = "Total")
    ax2[y[j],x[j]].plot(axis,baseline, label = "Baseline")
    ax2[y[j],x[j]].plot(axis,trunc, label = "Truncated")
    ax2[y[j],x[j]].set_title(vals)
    #print(j)
ax2[0,0].legend()
fig2.tight_layout()
