@echo off
echo STARTING DEBUG > debug_out.txt
echo PATH is %PATH% >> debug_out.txt
python --version >> debug_out.txt 2>&1
if errorlevel 1 echo PYTHON FAILED >> debug_out.txt
echo DONE DEBUG >> debug_out.txt
