import datetime
import time
import ctypes
import subprocess
from win10toast import ToastNotifier
from exclude import Exclude, UNRESTRICTED, FIXED, NOTHING, OFF
from threading import Thread

#Variables for ctypes.windll.user32.MessageBoxW
MB_OK = 0x0
MB_OKCXL = 0x01
MB_YESNOCXL = 0x03
MB_YESNO = 0x04
MB_HELP = 0x4000
ICON_EXLAIM=0x30
ICON_INFO = 0x40
ICON_STOP = 0x10

status = None
status_change_callback = None

def set_status(*sts):
    global status
    status = ''.join(sts)
    if status_change_callback is not None:
        status_change_callback()

class MeteredOnOff:
    def __init__(self, status_change_callback=None) -> None:
        self.status = None
        self.callback = status_change_callback
        self._immediate_refresh = False

    def _set_status(self, *sts):
        self.status = ''.join(sts)
        if self.callback is not None:
            self.callback()

    def immediate_refresh(self):
        self._immediate_refresh = True

    def main(self):
        self.kill = False

        ex = Exclude()

        notifier = ToastNotifier()

        subprocess.CREATE_NO_WINDOW
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE # default

        def FindProfile(ProfileList, CurrentInterface):
            for ci in CurrentInterface:
                if ci.find("Profile") != -1:
                    for pl in ProfileList:
                        if pl in ci:
                            CurrentProfile = pl
                            return CurrentProfile
            return ""

        def excluded(ssid):
            """Returns type of exclude if giver ssid is in excluded list. else returns False"""
            if len(ret:=ex.get_exclude_type(ssid)) is not None and not OFF in ret:
                return ret[0]
            else:
                return False

        def notify(body, title = "Auto Metered Connection", duration = 5):
            print('Notifying - ' + str(body))
            self._set_status('Waiting for Notification...')
            Thread(target=notifier.show_toast, args=(title, body,), kwargs={'duration' : duration}).start()
            
        while True:
            self._set_status('Refreshing...')
            dtime = datetime.datetime.now()
            hour = dtime.hour
            print("Refreshing...")
            print("Current time - " + str(dtime))

            """AllProfiles = subprocess.check_output("netsh wlan show profiles", startupinfo=si)
            ProfileList = str(AllProfiles).replace(r"\r\n","").replace("  '","").split("    All User Profile     : ")
            ProfileList.remove(ProfileList[0])
            print("Profile List - "+str(ProfileList).replace("[","").replace("]","").replace('"',""))

            print("Checking Current Interface.")
            CurrentInterface = subprocess.check_output("netsh wlan show interfaces", startupinfo=si)
            CurrentInterface = str(CurrentInterface).split(r"\r\n")

            CurrentProfile = FindProfile(ProfileList, CurrentInterface)"""

            CurrentProfile = str(subprocess.check_output("powershell.exe (get-netconnectionProfile).Name", shell=True).strip())[2:-1]
            # CurrentProfile = 'Dialog 4G 335'
            # CurrentProfile = 'Rizy'
            
            if CurrentProfile == "":
                print("Profile Finding Error. or Wifi Not Connected...")
            else:
                print("Current Profile - "+CurrentProfile)

                print("Getting "+CurrentProfile+" Status.")
                SavedCurrentProfile = CurrentProfile
                minus_char = 0
                while True:
                    try:
                        CurrentProfile = (CurrentProfile[:-minus_char] if minus_char else CurrentProfile)
                        CurrentProfileStatus = subprocess.check_output('netsh wlan show profile name="'+CurrentProfile+'"', startupinfo=si)
                        break
                    except:
                        minus_char += 1
                CurrentProfileStatus = str(CurrentProfileStatus).replace("'","").split(r"\r\n")

                print("Checking "+CurrentProfile+" Cost.")
                CurrentProfileStatusCost = ""
                for cps in CurrentProfileStatus:
                    if "Fixed" in cps:
                        CurrentProfileStatusCost = "Fixed"
                    elif "Unrestricted" in cps:
                        CurrentProfileStatusCost = "Unrestricted"

                if CurrentProfileStatusCost == "Fixed" or "Unrestricted":
                    print(CurrentProfile+" Cost - "+CurrentProfileStatusCost)
                else:
                    print("Error in checking Cost status in "+CurrentProfile+".")

                exclude = excluded(CurrentProfile)

                if exclude:
                    print(CurrentProfile + ' is in excluded list...')

                if (hour < 8 and not exclude) or (exclude == UNRESTRICTED):
                    if CurrentProfileStatusCost == "Fixed":
                        x = subprocess.call('netsh wlan set profileparameter name="'+CurrentProfile+'" cost=Unrestricted', startupinfo=si)
                        print('Return from action command - ' + str(x))
                        # esult = ctypes.windll.user32.MessageBoxW(0, "Metered connection set to Unrestricted at "+ dtime.strftime("%I:%M:%S %p") +".", "Auto Metered Connection", MB_OK | ICON_INFO)
                        # notifier.show_toast("Auto Metered Connection", "Metered connection option of "+CurrentProfile+" set to Unrestricted at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 7)
                        if not x:
                            notify("Metered connection option of "+CurrentProfile+ (' which is in excluded list' if exclude else '') + " set to Unrestricted at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 10)
                        else:
                            notify("Returned with Error while executing command for change parameter.")

                elif (CurrentProfileStatusCost == "Unrestricted" and not exclude) or (CurrentProfileStatusCost == "Unrestricted" and exclude == FIXED):
                    x = subprocess.call('netsh wlan set profileparameter name="'+CurrentProfile+'" cost=Fixed', startupinfo=si)
                    print('Return from action command - ' + str(x))
                    # result = ctypes.windll.user32.MessageBoxW(0, "Metered connection set to Fixed at "+ dtime.strftime("%I:%M:%S %p") +".", "Auto Metered Connection", MB_OK | ICON_INFO)
                    # notifier.show_toast("Auto Metered Connection", "Metered connection option of "+CurrentProfile+" set to Fixed at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 7)
                    if not x:
                        notify("Metered connection option of "+CurrentProfile+ (' which is in excluded list' if exclude else '') + " set to Fixed at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 10)
                    else:
                        notify("Returned with Error while executing command for change parameter.")
            
            self._immediate_refresh = False
            dtime = datetime.datetime.now()
            print("Current Second - "+str(dtime.second)+". Next Refresh in "+str(60-dtime.second)+" Seconds.")
            for second in range(60-dtime.second, 0, -1):
                self._set_status(f'Next refresh in {second} seconds...')
                time.sleep(1)
                if self._immediate_refresh:
                    break
            # time.sleep(60-dtime.second)
            if self.kill:
                quit()


if __name__ == "__main__":
    MeteredOnOff().main()