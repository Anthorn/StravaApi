from GUI import *
import sys
import os

def main():

    #api = StravaApi()
    #if(checkUser(api)):
    #    api.uploadActivitiesFromDirectory()
    #else:
    #    print("User not ok.")
    try:

        gui = GUI()
        gui.startGui()
    except:
        print ("Unexpected error: ", sys.exc_info()[0])


if __name__ == "__main__":
    main()
