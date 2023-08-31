from iris import *
import os
import csv
from pathlib import Path

threshold = 0.3

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



def verify(temp1, temp2):
    v = np.logical_xor(temp1, temp2)
    ham = np.count_nonzero(v)
    ile = temp1.shape[0]*temp2.shape[1]
    value = ham/ile
    if value <= threshold:
        return value, 1
    else:
        return value, 0

def createCSV():
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
                    value, res = verify(enrolled.template, ver.template)
                    if ver.id == enrolled.id:
                        writer.writerow(["`" + enrolled.id + "/" + enrolled.probeID, "'" +ver.id + "/" + ver.probeID, res, 1, value])
                    else:
                        writer.writerow(["`" +enrolled.id + "/" + enrolled.probeID,"'" + ver.id + "/" + ver.probeID, res, 0, value])

    # with open('results.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     field = ["Probe 1", "Probe 2", "Passed?", "Should?", "Hamming"]
    #     writer.writerow(field)
    #     for i in range(1,242):
    #         folder = "ubiris/Sessao_1/" + str(i)
    #         probe_name = []
    #         # **** Find enrolled probe **** #
    #         for image in os.listdir(folder):
    #             if (image.endswith(".pkl")):
    #                 probe_name.append(image)
    #         if len(probe_name) == 0:
    #             continue
    #         else:
    #             path = folder + "/" + str(probe_name[0]) # enrolled one
    #             file = open(path, 'rb')
    #             enrolled = pickle.load(file)
    #             file.close()
    #         # **** Verify enrolled with others **** #
    #         for j in range(1,242):
    #             folder = "ubiris/Sessao_1/" + str(j)
    #             probe_name = []
    #             for image in os.listdir(folder):
    #                 if (image.endswith(".pkl")):
    #                     probe_name.append(image)
    #             for k in range(len(probe_name)):
    #                 path = folder + "/" + str(probe_name[k])
    #                 file = open(path, 'rb')
    #                 ver = pickle.load(file)
    #                 file.close()
    #                 if ver.id == enrolled.id and ver.probeID == enrolled.probeID:
    #                     continue
    #                 value, res = verify(enrolled.template, ver.template)
    #                 if ver.id == enrolled.id:
    #                     writer.writerow([res, 1, value])
    #                 else:
    #                     writer.writerow([res, 0, value])

        


# file = open('ubiris/Sessao_1/5/1.pkl', 'rb')
# x = pickle.load(file)
# file.close()
# file = open('ubiris/Sessao_1/5/4.pkl', 'rb')
# y = pickle.load(file)
# file.close()

# value, bo = verify(x.template, y.template)
# print( value, bo)

# print(value, bo)
# createCSV()
# print(verify(x.template, y.template))
# delete_all()
# enroll_all()
createCSV()
