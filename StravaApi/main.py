import sys
from MainWindow import MainWindow

def main():

    #api = StravaApi()
    #if(checkUser(api)):
    #    api.uploadActivitiesFromDirectory()
    #else:
    #    print("User not ok.")
    try:

        gui = MainWindow()
        gui.startGui()
    except ValueError:
        print("Unexpected error: ", sys.exc_info()[0])


if __name__ == "__main__":
    main()
