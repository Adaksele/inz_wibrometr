#https://www.raspberrypi-spy.co.uk/2015/05/adding-a-ds3231-real-time-clock-to-the-raspberry-pi/

#sudo hwclock -r
import os
import subprocess
def get_time():
    time = subprocess.check_output(["sudo", "hwclock -r"])
    #time = os.system("sudo hwclock -r")
    #rtc_time=subprocess.run("sudo hwclock -r")
    #print(rtc_time)
    return time

if __name__ == "__main__":
    get_time()
    pass