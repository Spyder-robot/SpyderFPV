@echo off
echo user pi raspberry>> ftpcmd.dat 			
echo bin>> ftpcmd.dat 			
echo put fpv.py>> ftpcmd.dat			
echo put spyder.py>> ftpcmd.dat
echo cd templates>> ftpcmd.dat
echo put index.html>> ftpcmd.dat
echo cd ..>> ftpcmd.dat
echo quit>> ftpcmd.dat 			
ftp -n -s:ftpcmd.dat 192.168.0.114			
del ftpcmd.dat 	

 		