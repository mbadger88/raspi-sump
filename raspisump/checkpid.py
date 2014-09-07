#!/usr/bin/python
# Check to make sure process raspi-sump is running and restart if required.

import subprocess
import time

def check_pid():
    '''Check status of raspisump.py process.'''
    cmdp1 = "ps aux"
    cmdp2 = "grep -v grep"
    cmdp3 = "grep -v sudo"
    cmdp4 = "grep -c /home/pi/raspi-sump/raspisump.py"
    cmdp1list = cmdp1.split(' ')
    cmdp2list = cmdp2.split(' ')
    cmdp3list = cmdp3.split(' ')
    cmdp4list = cmdp4.split(' ')
    part1 = subprocess.Popen(cmdp1list, stdout=subprocess.PIPE)
    part2 = subprocess.Popen(cmdp2list, stdin=part1.stdout, stdout=subprocess.PIPE)
    part1.stdout.close()
    part3 = subprocess.Popen(cmdp3list, stdin=part2.stdout,stdout=subprocess.PIPE)
    part2.stdout.close()
    part4 = subprocess.Popen(cmdp4list, stdin=part3.stdout,stdout=subprocess.PIPE)
    part3.stdout.close()
    x = int(part4.communicate()[0])
    if x == 0:
        log_check("Process stopped, restarting")
        restart()  
    elif x == 1:
        exit(0)
    else:
        log_check("Multiple Processes...Killing and Restarting")
        kill_start()
        
def restart():
    '''Restart raspisump.py process.'''
    restart_cmd = "/home/pi/raspi-sump/raspisump.py &"
    restart_now = restart_cmd.split(' ')
    subprocess.Popen(restart_now)
    exit(0)

def kill_start():
    '''Kill all instances of raspisump.py process.'''
    kill_cmd = "killall 09 raspisump.py"
    kill_it = kill_cmd.split(' ')
    subprocess.call(kill_it)
    restart()    

def log_check(reason):
    logfile = open("/home/pi/raspi-sump/logs/process_log", 'a')
    logfile.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
    logfile.write(reason),
    logfile.write("\n")
    logfile.close

if __name__ == "__main__":
    check_pid()
