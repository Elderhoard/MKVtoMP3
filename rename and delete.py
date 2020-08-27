##TODO more imports to come
import os

#Current working directory
path = os.getcwd()

#Delete non converted
for file in os.listdir(path):
    if(file.endswith(".txt") and not file.startswith('UPDATED')):
        try:
            os.remove(file)
        except:
            print("!!!!!Error deleting file {}!!!!!".format(file))

#Rename converted MP3s
for file in os.listdir(path):
    if(file.endswith(".txt") and file.startswith('UPDATED')):
        try:
            os.rename(r'{}'.format(file),r'{}'.format(file[7:]))
        except:
            print("!!!!!Error renaming file {}!!!!!".format(file))
        
input("Press any key to continue...")
