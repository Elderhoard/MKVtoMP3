'''
This program converts MKV files into MP3 files with metadata and album artwork embeded
Uses FFMPEG registered as a system variable and Mutagen module for Python
https://github.com/quodlibet/mutagen
'''
import os, glob, subprocess
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3

#Variables
#Current working directory
path = os.getcwd()

#Create no window value
CREATE_NO_WINDOW = 0x08000000

#Counters
num_files = len(glob.glob("*.mkv"))
curr_file = 1
num_errors = 0

#Functions
#Reset counters 
def reset_counters(FType):
    global num_files
    global curr_file
    
    num_viles = len(glob.glob(FType))
    curr_file = 1

#Append faiure to end of error log file
def addError(name, failtype):
    #with open("errorlog.txt", "a+") as file_object
    filename = "errorlog.txt"
    
    if os.path.exists(filename):
        append_write = 'a'
    else:
        append_write = 'w'

    errorlog = open(filename, append_write)
    errorlog.write("Failed to {0}: {1}".format(failtype, name) + '\n')
    errorlog.close()

#Trim extention from file
def trim(file):
    return file[:-4]

#Execute command without showing shell
def execute(command):
    subprocess.call(command, creationflags=CREATE_NO_WINDOW)
    

print('Starting conversion from MKV to MP3')

print('Extracting album art')
print('-----------------------------------\n')
#Conversion Process
#Extract a jpg from the MKV from 30 seconds in
for file in os.listdir(path):
    fullfilepath = path + '\\' + file
    if(file.endswith(".mkv")):
        print('{0}/{1} Creating thumnail for: {2}'.format(curr_file, num_files, file))
        try:
            execute("ffmpeg -ss 30 -i \"{0}\" -qscale:v 3 -frames:v 1 \"{1}.jpg\"".format(fullfilepath, trim(file)))
            curr_file += 1
        except:
            print('!!!!Error creating jpg for: {0}!!!!'.format(file))
            addError(file, 'extract jpg from MKV')
            num_errors += 1
            curr_file += 1
    elif not any(file.endswith('.mkv') for file in os.listdir('.')):
        print('!!!!!No .MKV files to take pictures from!!!!!')

reset_counters("*.mkv")

print('\nConverting from MKV to MP3')
print('-----------------------------------\n')

#Convert from MKV to MP3
for file in os.listdir(path):
    fullfilepath = path + '\\' + file
    if(file.endswith(".mkv")):
        print('{0}/{1} Converting to MP3: {2}'.format(curr_file, num_files, file))
        try:
            execute("ffmpeg -i \"{0}\" -id3v2_version 3 -b:a 192K -vn \"{1}.mp3\"".format(fullfilepath, trim(file)))
            curr_file += 1
        except:
            print('!!!!Error converting to MP3: {0}!!!!'.format(file))
            addError(file, 'convert to MP3')
            num_errors += 1
            curr_file += 1
    elif not any(file.endswith('.mkv') for file in os.listdir('.')):
        print('!!!!!No .MKV files to convert!!!!!')

reset_counters("*.mp3")

print('\nAdding Metadata')
print('-----------------------------------\n')

#Add metadata to MP3
for file in os.listdir(path):
    fullfilepath = path + '\\' + file
    if file.endswith(".mp3"):
        try:
            artist, song = trim(file).split("-")
            artist = artist.strip()
            song = song.strip()
        except:
            print('!!!!Error splitting file: {0}!!!!'.format(file))
            addError(file, 'split file into artist and song')
            num_errors += 1
            curr_file += 1
    if file.endswith(".mp3"):
        print('{0}/{1} Adding metadata to MP3: {2}'.format(curr_file, num_files, file))
        try:
            audio = MP3(fullfilepath, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            audio = EasyID3(file)
            audio["title"] = u"{}".format(song)
            audio["artist"] = u"{}".format(artist)
            audio.save()
            curr_file += 1
        except:
            print('!!!!!Error adding metadata!!!!!')
            addError(file, 'add metadata')
            num_errors += 1
            curr_file += 1
    elif not any(file.endswith('.mp3') for file in os.listdir('.')):
        print('!!!!!No MP3 files to add metadata to!!!!!')

reset_counters("*.mp3")
print('\nAdding Artwork')
print('-----------------------------------\n')
#Add picture
for file in os.listdir(path):
    fullfilepath = path + '\\' + file
    if(file.endswith(".mp3")):
        print('{0}/{1} Converting to MP3: {2}'.format(curr_file, num_files, file))
        try:
            execute("ffmpeg -i \"{0}\" -i \"{1}.jpg\" -map 0:0 -map 1:0 -c copy -id3v2_version 3 \"UPDATED{1}.mp3\"".format(fullfilepath, trim(file)))
            curr_file += 1
        except:
            print('!!!!Error adding artwork: {0}!!!!'.format(file))
            addError(file, 'add artwork')
            num_errors += 1
            curr_file += 1
    elif not any(file.endswith('.mkv') for file in os.listdir('.')):
        print('!!!!!No MP3 to add artwork!!!!!')

print('\nDeleting old MP3s.....')
#Delete non converted
for file in os.listdir(path):
    if(file.endswith(".mp3") and not file.startswith('UPDATED')):
        try:
            os.remove(file)
        except:
            print("!!!!!Error deleting file {}!!!!!".format(file))

print('\nRe-Naming updated.....')
#Rename converted MP3s
for file in os.listdir(path):
    if(file.endswith(".mp3") and file.startswith('UPDATED')):
        try:
            os.rename(r'{}'.format(file),r'{}'.format(file[7:]))
        except:
            print("!!!!!Error renaming file {}!!!!!".format(file))
        
print('-----------------------------------\n')
print('Errors: {}'.format(num_errors))

#Hold so you can review the log
input('Press any key to continue...')
