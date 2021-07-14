@echo off			
del arduino2.ino.with_bootloader.eightanaloginputs.hex			
ren arduino2.ino.eightanaloginputs.hex arduino2.hex			
echo user pi raspberry>> ftpcmd.dat 			
echo bin>> ftpcmd.dat 			
echo put arduino2.hex>> ftpcmd.dat			
echo quit>> ftpcmd.dat 			
ftp -n -s:ftpcmd.dat 192.168.0.102		
del ftpcmd.dat 			
del arduino2.hex