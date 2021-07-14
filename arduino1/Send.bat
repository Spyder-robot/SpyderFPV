@echo off			
del arduino1.ino.with_bootloader.eightanaloginputs.hex			
ren arduino1.ino.eightanaloginputs.hex arduino1.hex			
echo user pi raspberry>> ftpcmd.dat 			
echo bin>> ftpcmd.dat 			
echo put arduino1.hex>> ftpcmd.dat			
echo quit>> ftpcmd.dat 			
ftp -n -s:ftpcmd.dat 192.168.0.114		
del ftpcmd.dat 			
del arduino1.hex