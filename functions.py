from iris import *
import os
import csv
# from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import itertools

font = {'size'   : 18}
matplotlib.rc('font', **font)

def delete_all():
    folder = Path("ubiris/Sessao_1")
    subfolders = [subfolder for subfolder in folder.iterdir() if subfolder.is_dir()]
    for dir in subfolders:
        path = Path(dir)
        files = list(path.glob('*.pkl'))
        for file in files:
            os.remove(file)

def enroll(path):
    try:
        obj = Iris(path)
        obj.generateTemplate()
        obj.getTweak()
        obj.generateBloom()
        obj.getHashKey()
        obj.generateBiohash()
    except:
        print(f"fte {obj.id} {obj.probeID}")
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
    ile = temp1.shape[0]*temp1.shape[1]
    value = ham/ile
    if value <= threshold:
        return value, 1
    else:
        return value, 0

def verifyBloom(temp1, temp2, threshold):
    value = 0
    for i in range(30):
        v = np.logical_xor(temp1[i], temp2[i])
        o1 = np.count_nonzero(temp1[i])
        o2 = np.count_nonzero(temp2[i])
        ham = np.count_nonzero(v)
        value += ham/(o1+o2)
    value = value/30
    
    if value <= threshold:
        return value, 1
    else:
        return value, 0
    
def verifyBiohash(temp1, temp2, threshold):
    v = np.logical_xor(temp1,temp2)
    ham = np.count_nonzero(v)
    value = ham / len(temp1)
    if value <= threshold:
        return value, 1
    else:
        return value, 0

def createCSV(threshold):
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["Sample 1", "Sample 2", "Passed?", "Should?", "Hamming"]
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
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Próg akceptacji")
    plt.ylabel("Wartość błędu")
    plt.title("FAR oraz FRR")
    plt.legend()
    plt.show()
    plt.figure(figsize=[15,8])
    plt.plot(frrs, fars, color='green')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("FRR")
    plt.ylabel("FAR")
    plt.title("FAR(FRR)")
    plt.show()


def createCSV_bloom(threshold):
    with open('results_bloom.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["Sample 1", "Sample 2", "Passed?", "Should?", "Hamming"]
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
                    value, res = verifyBloom(enrolled.bloom, ver.bloom, threshold)
                    if ver.id == enrolled.id:
                        writer.writerow(["`" + enrolled.id + "/" + enrolled.probeID, "'" +ver.id + "/" + ver.probeID, res, 1, value])
                    else:
                        writer.writerow(["`" +enrolled.id + "/" + enrolled.probeID,"'" + ver.id + "/" + ver.probeID, res, 0, value])

def save_rates_bloom(fars, frrs):
    file = open('fars_bloom.pkl', 'wb')
    pickle.dump(fars, file)
    file.close()
    file = open('frrs_bloom.pkl', 'wb')
    pickle.dump(frrs, file)
    file.close()

def create_plots_bloom(load: bool, save: bool): # load -> True (from file), False (new); save -> True (save values to file), False (don't save)
    if not ((isinstance(load, bool) and isinstance(save, bool)) or (load in (0, 1)) and (save in (0, 1))):
         raise ValueError("Input variables must be boolean (True/False) or 0/1")
    thres = np.linspace(0.01, 0.99, 99)
    if load == True:
        file = open('fars_bloom.pkl', 'rb')
        fars = pickle.load(file)
        file.close()
        file = open('frrs_bloom.pkl', 'rb')
        frrs = pickle.load(file)
        file.close()    
    else:    
        fars = []
        frrs = []
        for t in thres:
            createCSV_bloom(t)
            FAR, FRR = count_FAR_FRR('results_bloom.csv')
            fars.append(FAR)
            frrs.append(FRR)
        if save == True:
            save_rates_bloom(fars, frrs)
    plt.figure(figsize=[15,8])
    plt.plot(thres, fars, color='red', label ='FAR')
    plt.plot(thres, frrs, color='blue', label = 'FRR')
    # plt.xscale('log')
    # plt.yscale('log')
    plt.xlabel("Próg akceptacji")
    plt.ylabel("Wartość błędu")
    plt.title("FAR oraz FRR (Bloom Filters)")
    plt.legend()
    plt.show()
    plt.figure(figsize=[15,8])
    plt.plot(frrs, fars, color='green')
    # plt.xscale('log')
    # plt.yscale('log')
    plt.xlabel("FRR")
    plt.ylabel("FAR")
    plt.title("FAR(FRR) (Bloom Filters)")
    plt.show()


def createCSV_biohash(threshold):
    with open('results_biohash.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["Sample 1", "Sample 2", "Passed?", "Should?", "Hamming"]
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
                    value, res = verifyBiohash(enrolled.biohash, ver.biohash, threshold)
                    if ver.id == enrolled.id:
                        writer.writerow(["`" + enrolled.id + "/" + enrolled.probeID, "'" +ver.id + "/" + ver.probeID, res, 1, value])
                    else:
                        writer.writerow(["`" +enrolled.id + "/" + enrolled.probeID,"'" + ver.id + "/" + ver.probeID, res, 0, value])


           
def save_rates_biohash(fars, frrs):
    file = open('fars_biohash.pkl', 'wb')
    pickle.dump(fars, file)
    file.close()
    file = open('frrs_biohash.pkl', 'wb')
    pickle.dump(frrs, file)
    file.close()

def create_plots_biohash(load: bool, save: bool): # load -> True (from file), False (new); save -> True (save values to file), False (don't save)
    if not ((isinstance(load, bool) and isinstance(save, bool)) or (load in (0, 1)) and (save in (0, 1))):
         raise ValueError("Input variables must be boolean (True/False) or 0/1")
    thres = np.linspace(0.01, 0.99, 99)
    if load == True:
        file = open('fars_biohash.pkl', 'rb')
        fars = pickle.load(file)
        file.close()
        file = open('frrs_biohash.pkl', 'rb')
        frrs = pickle.load(file)
        file.close()    
    else:    
        fars = []
        frrs = []
        for t in thres:
            createCSV_biohash(t)
            FAR, FRR = count_FAR_FRR('results_biohash.csv')
            fars.append(FAR)
            frrs.append(FRR)
        if save == True:
            save_rates_biohash(fars, frrs)
    plt.figure(figsize=[15,8])
    plt.plot(thres, fars, color='red', label ='FAR')
    plt.plot(thres, frrs, color='blue', label = 'FRR')
    # plt.xscale('log')
    # plt.yscale('log')
    plt.xlabel("Próg akceptacji")
    plt.ylabel("Wartość błędu")
    plt.title("FAR oraz FRR (Biohashing)")
    plt.legend()
    plt.show()
    plt.figure(figsize=[15,8])
    plt.plot(frrs, fars, color='green')
    # plt.xscale('log')
    # plt.yscale('log')
    plt.xlabel("FRR")
    plt.ylabel("FAR")
    plt.title("FAR(FRR) (Biohashing)")
    plt.show()


def distribution(file):
    df = pd.read_csv(file)
    same = []
    diff = []
    for i in range(len(df)):
        id1 = df['Sample 1'][i].index('/')
        id2 = df['Sample 2'][i].index('/')
        if id1 != id2:
            diff.append(df['Hamming'][i])
        else:
            if df['Sample 1'][i][1:(id1+1)] == df['Sample 2'][i][1:(id1+1)]:
                same.append(df['Hamming'][i])
            else:
                diff.append(df['Hamming'][i])

    plt.figure(figsize=[15,8])
    plt.hist(diff, color='#C70039', bins=100, label="Próbki różnych osób")
    plt.hist(same, color='green', bins=20, label ="Próbki jednakowych osób")
    plt.title("Rozkład podobieństwa")
    plt.xlabel("Dystans Hamminga")
    plt.ylabel("Liczba próbek")
    plt.legend()
    plt.show()
    return same, diff


def unlikability_bloom(path):
    templates = []
    hamming = []
    obj = Iris(path)
    obj.generateTemplate()
    for i in range(1000):
        obj.tweak = str(secrets.token_hex(7))
        obj.generateBloom()
        templates.append(obj.bloom)
        print(i)
    
    for a, b in itertools.combinations(templates, 2):
        h, _ = verifyBloom(a, b, 0.3)
        hamming.append(h)
    
    _,diff = distribution('results_bloom.csv')
    plt.figure(figsize=[15,8])
    plt.hist(hamming, color='green', bins=100, label ='Różne tożsamośći użytkownika')
    plt.hist(diff, color='#C70039', bins=100, label="Różni użytkownicy")
    plt.title("Nielinkowalność (Bloom Filetrs)")
    plt.xlabel("Dystans Hamminga")
    plt.ylabel("Liczba próbek")
    plt.legend()
    plt.show()

def unlikability_biohashing(path):
    templates = []
    hamming = []
    obj = Iris(path)
    obj.generateTemplate()
    for i in range(1000):
        obj.hashkey = int(secrets.token_hex(16), 16)
        obj.generateBiohash()
        templates.append(obj.biohash)
        print(i)
    
    for a, b in itertools.combinations(templates, 2):
        h, _ = verifyBiohash(a, b, 0.3)
        hamming.append(h)
        
    _,diff = distribution('results_biohash.csv')
    plt.figure(figsize=[15,8])
    plt.hist(hamming, color='green', bins=100, label ='Różne tożsamośći użytkownika')
    plt.hist(diff, color='#C70039', bins=100, label="Różni użytkownicy")
    plt.title("Nielinkowalność (Biohashing)")
    plt.xlabel("Dystans Hamminga")
    plt.ylabel("Liczba próbek")
    plt.legend()
    plt.show()

# enroll_all()
# create_plots_biohash(True, False)
# distribution('results_biohash.csv')
unlikability_biohashing('ubiris/Sessao_1/1/Img_1_1_1.jpg')

