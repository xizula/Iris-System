from iris import *
import os
import csv
from pathlib import Path


def delete_all():
    folder = Path("ubiris/Sessao_1")
    subfolders = [subfolder for subfolder in folder.iterdir() if subfolder.is_dir()]
    for dir in subfolders:
        path = Path(dir)
        files = list(path.glob('*.pkl'))
        for file in files:
            os.remove(file)

def enroll(path):
    print(path)
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
    ham = round(np.count_nonzero(v),2)
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


# def count_FAR(file_path):
           
delete_all()
enroll_all()
createCSV(0.3)

