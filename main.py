'''
     Web Automation of CU-Online Lahore
'''

from script import *
import sys
from selenium.common.exceptions import ElementClickInterceptedException

def main(offline=False):
    print("Starting...")
    if not offline:
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
                
    else:
        for chunk in getOffline():
            prettyPrint(chunk)

if "--offline" in sys.argv or "-o" in sys.argv: 
    main(offline=True)
else:
    main()