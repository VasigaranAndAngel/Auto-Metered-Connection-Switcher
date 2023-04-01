import datetime
import time
import ctypes
import subprocess
try:
    from win10toast import ToastNotifier
except ImportError:
    print("win10toast module not found. Download it? (Yes/No)")
    yes_or_no = ""
    while yes_or_no.lower() != "yes" and yes_or_no.lower() != "no":
        yes_or_no = input("- ")
        if yes_or_no.lower() == "yes":
            x = subprocess.call('pip install win10toast')
            from win10toast import ToastNotifier
        elif yes_or_no.lower() == "no":
            print("Exiting...")
            quit()
        else:
            print("Your input is missmatching.")

#Variables for ctypes.windll.user32.MessageBoxW
MB_OK = 0x0
MB_OKCXL = 0x01
MB_YESNOCXL = 0x03
MB_YESNO = 0x04
MB_HELP = 0x4000
ICON_EXLAIM=0x30
ICON_INFO = 0x40
ICON_STOP = 0x10

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
    excludes = open("Exclude.txt")
    excluded_lines = excludes.readlines()
    excludes.close()
    list_no = -1
    excluded_list = [[], [], []]
    for i in excluded_lines:
        i = i.replace('\n', '')
        if i == '#Unrestricted':
            list_no = 0
        elif i == '#Fixed':
            list_no = 1
        elif i == '#Nothing':
            list_no = 2
        elif list_no != -1 and i:
            excluded_list[list_no].append(i)
        
    for list_no in range(0, len(excluded_list)):
        for i in excluded_list[list_no]:
            if str(ssid) == i:
                return list_no + 1  #coz 0 returns false in if statement
    return False

def notify(body, title = "Auto Metered Connection", duration = 5):
    print('Notifying - ' + str(body))
    notifier.show_toast(title, body, duration = duration)

while True:
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

        if (hour < 8 and not exclude) or (exclude == 1):
            if CurrentProfileStatusCost == "Fixed":
                x = subprocess.call('netsh wlan set profileparameter name="'+CurrentProfile+'" cost=Unrestricted', startupinfo=si)
                print('Return from action command - ' + str(x))
                # esult = ctypes.windll.user32.MessageBoxW(0, "Metered connection set to Unrestricted at "+ dtime.strftime("%I:%M:%S %p") +".", "Auto Metered Connection", MB_OK | ICON_INFO)
                # notifier.show_toast("Auto Metered Connection", "Metered connection option of "+CurrentProfile+" set to Unrestricted at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 7)
                if not x:
                    notify("Metered connection option of "+CurrentProfile+ (' which is in excluded list' if exclude else '') + " set to Unrestricted at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 10)
                else:
                    notify("Returned with Error while executing command for change parameter.")

        elif (CurrentProfileStatusCost == "Unrestricted" and not exclude) or (CurrentProfileStatusCost == "Unrestricted" and exclude == 2):
            x = subprocess.call('netsh wlan set profileparameter name="'+CurrentProfile+'" cost=Fixed', startupinfo=si)
            print('Return from action command - ' + str(x))
            # result = ctypes.windll.user32.MessageBoxW(0, "Metered connection set to Fixed at "+ dtime.strftime("%I:%M:%S %p") +".", "Auto Metered Connection", MB_OK | ICON_INFO)
            # notifier.show_toast("Auto Metered Connection", "Metered connection option of "+CurrentProfile+" set to Fixed at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 7)
            if not x:
                notify("Metered connection option of "+CurrentProfile+ (' which is in excluded list' if exclude else '') + " set to Fixed at "+ dtime.strftime("%I:%M:%S %p") +".", duration = 10)
            else:
                notify("Returned with Error while executing command for change parameter.")
    
    dtime = datetime.datetime.now()
    print("Current Second - "+str(dtime.second)+". Next Refresh in "+str(60-dtime.second)+" Seconds.")
    time.sleep(60-dtime.second)