'''
     Web Automation of CU-Online Lahore
'''

from script import *
import sys
from selenium.common.exceptions import ElementClickInterceptedException

def main(*args):
    print("Starting...")
    if len(args) == 1:
        try:
            for chunk in generator():
                prettyPrint(chunk)
        except ElementClickInterceptedException:
            print("Recaptcha not solved")
            print("Opening in browser")
            for chunk in generator(headless=False):
                prettyPrint(chunk)
        except FileNotFoundError:
            print("Login details not found")
            setLoginDetails(input("Enter username: "), input("Enter password: "))
            main()
                
    if "offline" in args:
        for chunk in getOffline():
            prettyPrint(chunk)
            
if __name__ == "__main__":
    main(sys.argv)