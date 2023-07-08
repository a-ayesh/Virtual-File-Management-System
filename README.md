# Virtual File Management System
Operating Systems Project: "Create a Linux-Mockup Remote Multi-Threaded Virtual File Management System". 

**Documentation.doxc** contains all necessary information about the purpose, functionality, as well as a user guide.

**VFMS_threaded.py** was created with the intention of remotely feeding multiple command requests from various users. For testing the program I utilized **input_thread#.txt** files containing several commands; the files were taken as Command-Line Args and fed the commands to their corresponding thread number. You may make any amount of **input_thread#.txt** files with any number of commands in any order, but the number of threads must correspond to the number of files.

**output_thread#.txt** files are output files generated after program execution showing our individual thread command responses.

**VFMS.json** loads the system state from its most recent execution. 

You may delete all **output_thread#.txt** files and **VFMS.json** if you wish to test the VFMS from scratch.

**VFMS_unthreaded.py** is a previous iteration of **VFMS_threaded.py** before any threading or remote concept was introduced. It is much simpler and proper to run it on a local system with no multi-threading.
