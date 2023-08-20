from iris import *
import os
import csv

threshold = 0.3

def delete_all():
    for i in range(1, 242):
        folder = "ubiris/Sessao_1/" + str(i)
        probe_name = []
        for image in os.listdir(folder):
            if (image.endswith(".pkl")):
                probe_name.append(image)
        for pkl in probe_name:
            os.remove(folder + "/" + str(pkl))

def enroll(path):
    obj = Iris(path)
    obj.getID()
    obj.generateTemplate()
    if obj.fail =='no':
        obj.save()

def enroll_all():
    for i in range(1, 242):
        folder = "ubiris/Sessao_1/" + str(i)
        probe_name = []
        for image in os.listdir(folder):
            if (image.endswith(".jpg")):
                probe_name.append(image)
        for img in probe_name:
            path = folder + "/" + str(img)
            enroll(path)



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
        field = ["passed", "should", "hamming"]
        writer.writerow(field)
        for i in range(1,242):
            folder = "ubiris/Sessao_1/" + str(i)
            probe_name = []
            # **** Find enrolled probe **** #
            for image in os.listdir(folder):
                if (image.endswith(".pkl")):
                    probe_name.append(image)
            if len(probe_name) == 0:
                continue
            else:
                path = folder + "/" + str(probe_name[0]) # enrolled one
                file = open(path, 'rb')
                enrolled = pickle.load(file)
                file.close()
            # **** Verify enrolled with others **** #
            for j in range(1,242):
                folder = "ubiris/Sessao_1/" + str(j)
                probe_name = []
                for image in os.listdir(folder):
                    if (image.endswith(".pkl")):
                        probe_name.append(image)
                for k in range(len(probe_name)):
                    path = folder + "/" + str(probe_name[k])
                    file = open(path, 'rb')
                    ver = pickle.load(file)
                    file.close()
                    if ver.id == enrolled.id and ver.probeID == enrolled.probeID:
                        continue
                    value, res = verify(enrolled.template, ver.template)
                    if ver.id == enrolled.id:
                        writer.writerow([res, 1, value])
                    else:
                        writer.writerow([res, 0, value])

        


# file = open('ubiris/Sessao_1/84/1.pkl', 'rb')
# x = pickle.load(file)
# file.close()
# file = open('ubiris/Sessao_1/84/3.pkl', 'rb')
# y = pickle.load(file)
# file.close()

# value, bo = verify(x.template, y.template)
# print( value, bo)

# print(value, bo)
# createCSV()

enroll_all()