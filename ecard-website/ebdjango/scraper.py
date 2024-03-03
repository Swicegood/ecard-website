#!/home/atourcit/.linuxbrew/Homebrew/bin/python3

import os.path
import ftplib
import ftputil
import re
from secrets import ftpsite, ftpuser, ftppasswd
from datetime import datetime

dir_dest = 'static/' # Directory where the files needs to be downloaded to
rm_pattern = r'^[a-z]+.*\.(jpg|jpeg)' #clear out all image files
pattern = r'^[a-z]+.*\-768x512\.(jpg|jpeg)' #filename pattern for what the script is looking for
print ('Looking for this pattern :', pattern) # print pattern
number_of_pics = 40 #number of pics to grab


today = datetime.today()
month = str(today.month)
if len(month) == 1:
    month = "0"+month
i = 0

rm_list = [f for f in os.listdir('static/') if re.match(rm_pattern, f)] #list of files to remove
for f in rm_list:
    os.remove("static/"+f)

with ftputil.FTPHost(ftpsite, ftpuser, ftppasswd, session_factory=ftplib.FTP_TLS) as host: # ftp host info
    recursive = host.walk("/wp/wp-content/uploads/"+str(today.year)+"/"+month,topdown=True,onerror=None) # recursive search )
    for root, dirs, files in recursive:
        for file in files:
            if re.match(pattern, file) and i < number_of_pics:    # collect all files that match pattern into variable:image_list
                fpath = host.path.join(root, file)
                if host.path.isfile(fpath):
                    host.download_if_newer(fpath, os.path.join(dir_dest, file))
                    print("Downloaded: "+file)
                    i += 1
            elif i >= number_of_pics:
                break
        if i >= number_of_pics:
            break
host.close()


