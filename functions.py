from iris import *
import os
import csv
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def delete_all():
    folder = Path("ubiris/Sessao_1")
    subfolders = [subfolder for subfolder in folder.iterdir() if subfolder.is_dir()]
    for dir in subfolders:
        path = Path(dir)
        files = list(path.glob('*.pkl'))
        for file in files:
            os.remove(file)

def enroll(path):
    obj = Iris(path)
    obj.getID()
    obj.generateTemplate()
    if obj.fail =='no':
        obj.save()

def enroll_all():
    folder = Path("ubiris/Sessao_1")
    subfolders = [subfolder for subfolder in folder.iterdir() if subfolder.is_dir()]
    for dir in subfolders:
        path = Path(dir)
        files = list(path.glob('*.jpg'))
        for file in files:
            file = file.as_posix()
            enroll(file)



def verify(temp1, temp2, threshold):
    v = np.logical_xor(temp1, temp2)
    ham = np.count_nonzero(v)
    ile = temp1.shape[0]*temp2.shape[1]
    value = ham/ile
    if value <= threshold:
        return value, 1
    else:
        return value, 0

def createCSV(threshold):
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["Probe 1", "Probe 2", "Passed?", "Should?", "Hamming"]
        writer.writerow(field)
        folder = Path("ubiris/Sessao_1")
        subfolders = [subfolder for subfolder in folder.iterdir() if subfolder.is_dir()]
        for dir in subfolders:
            path = Path(dir)
            files = list(path.glob('*.pkl'))
            probe = open(files[0], 'rb')
            enrolled = pickle.load(probe)
            probe.close()
            for i in subfolders:
                path = Path(i)
                files = list(path.glob('*.pkl'))
                for file in files:
                    probe = open(file.as_posix(), 'rb')
                    ver = pickle.load(probe)
                    probe.close()
                    if ver.id == enrolled.id and ver.probeID == enrolled.probeID:
                        continue
                    value, res = verify(enrolled.template, ver.template, threshold)
                    if ver.id == enrolled.id:
                        writer.writerow(["`" + enrolled.id + "/" + enrolled.probeID, "'" +ver.id + "/" + ver.probeID, res, 1, value])
                    else:
                        writer.writerow(["`" +enrolled.id + "/" + enrolled.probeID,"'" + ver.id + "/" + ver.probeID, res, 0, value])


def count_FAR_FRR(file_path):
    file = pd.read_csv(file_path)
    FP = len(file[(file["Passed?"] == 1) & (file["Should?"] == 0)]) # False Positive
    FN = len(file[(file["Passed?"] == 0) & (file["Should?"] == 1)]) # False Negative
    TP = len(file[(file["Passed?"] == 1) & (file["Should?"] == 1)]) # True Positive
    TN = len(file[(file["Passed?"] == 0) & (file["Should?"] == 0)]) # True Negative
    FAR = FP/(FP+TN)
    FRR = FN/(FN+TP)
    return FAR, FRR
           
def save_rates(fars, frrs):
    file = open('fars.pkl', 'wb')
    pickle.dump(fars, file)
    file.close()
    file = open('frrs.pkl', 'wb')
    pickle.dump(frrs, file)
    file.close()

def create_plots(load: bool, save: bool): # load -> True (from file), False (new); save -> True (save values to file), False (don't save)
    if not ((isinstance(load, bool) and isinstance(save, bool)) or (load in (0, 1)) and (save in (0, 1))):
         raise ValueError("Input variables must be boolean (True/False) or 0/1")
    thres = np.linspace(0.01, 0.99, 99)
    if load == True:
        file = open('fars.pkl', 'rb')
        fars = pickle.load(file)
        file.close()
        file = open('frrs.pkl', 'rb')
        frrs = pickle.load(file)
        file.close()    
    else:    
        fars = []
        frrs = []
        for t in thres:
            createCSV(t)
            FAR, FRR = count_FAR_FRR('results.csv')
            fars.append(FAR)
            frrs.append(FRR)
        if save == True:
            save_rates(fars, frrs)
    plt.figure(figsize=[15,8])
    plt.plot(thres, fars, color='red', label ='FAR')
    plt.plot(thres, frrs, color='blue', label = 'FRR')
    plt.xlabel("Threshold")
    plt.ylabel("Error value")
    plt.title("FAR and FRR")
    plt.legend()
    plt.show()
    plt.figure(figsize=[15,8])
    plt.plot(frrs, fars, color='green')
    # plt.xscale('log')
    plt.xlabel("FRR")
    plt.ylabel("FAR")
    plt.title("FAR(FRR)")
    plt.show()

create_plots(0, False)



