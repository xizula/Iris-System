from iris import *
import os

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

def enroll_all():
    for i in range(1, 242):
        folder = "ubiris/Sessao_1/" + str(i)
        probe_name = []
        for image in os.listdir(folder):
            if (image.endswith(".jpg")):
                probe_name.append(image)
        for img in probe_name:
            path = folder + "/" + str(img)
            obj = Iris(path)
            obj.getID()
            obj.generateTemplate()
            if obj.fail == 'yes':
                continue
            else:
                obj.save()

def verify(temp1, temp2):
    v = np.logical_xor(temp1, temp2)
    ham = np.count_nonzero(v)
    ile = temp1.shape[0]*temp2.shape[1]
    value = ham/ile
    if value <= threshold:
        return value, 1
    else:
        return value, 0


# file = open('ubiris/Sessao_1/1/1.pkl', 'rb')
# x = pickle.load(file)
# file.close()
# file = open('ubiris/Sessao_1/2/1.pkl', 'rb')
# y = pickle.load(file)
# file.close()

# value, bo = verify(x.template, y.template)

# print(value, bo)