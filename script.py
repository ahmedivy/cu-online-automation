import json
import os
from sys import path
from datetime import datetime
from tabulate import tabulate
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException

CUONLINE_LINK = "https://cuonline.cuilahore.edu.pk:8091/"
POPUP_XPATH = '//*[@id="myModal"]/div/div/div[1]/button'
CAPTCHA_XPATH = '//*[@id="rc-anchor-container"]/div[3]'
CAPTCHA_CLASS = 'recaptcha-checkbox-checkmark'
CAPTCHA_ID = 'rc-anchor-container'
IFRAME_XPATH = '/html/body/iframe'
DB_TABLE_XPATH = '/html/body/div/div/div/div[2]/div/table/tbody'
ATT_PATH = '//div[@class="progress-bar bg-success"]'
ATT_PB_DIV = 'div[role="progressbar"]'

def writeJson(data):
    if not os.path.exists("cookies"):
        os.makedirs("cookies")
    with open(os.path.join(path[0], "cookies", f'{data["tag"]}.json'), "w") as file:
        json.dump(data, file, indent=4)
        
def readJson(name):
    with open(os.path.join(path[0], "cookies", f"{name}.json"), "r") as file:
        return json.load(file)
    
def isUpdated(newData):
    oldData = readJson(newData["tag"])
    if oldData["data"] == newData["data"]:
        return False
    else:
        return True

def setLoginDetails(username, password):
    with open(os.path.join(path[0], "login.txt"), "w") as file:
        file.write(f'{username}\n{password}')
        
def getLoginDetails():
    try:
        with open(os.path.join(path[0], "login.txt"), "r") as file:
            return file.read().splitlines()
    except:
        print("Login details not found")
        setLoginDetails(input("Enter username: "), input("Enter password: "))
        return getLoginDetails()
    
def setExtras():
    with open(os.path.join(path[0], "vars.txt"), "w") as file:
        file.write(input("Enter web driver path: "))

def getExtras():
    try:
        with open(os.path.join(path[0], "vars.txt"), "r") as file:
            return file.read().splitlines()[0]
    except:
        print("Chrome webdriver path not set")
        setExtras()
        return getExtras()
    
def generator(headless=True):
    
    # Initializing driver and getting CUOnline Page
    options = Options()
    options.add_argument("--headless") if headless else None
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(getExtras(), options=options)
    driver.get(CUONLINE_LINK)
    
    # Closing the popup
    driver.find_element(By.XPATH, POPUP_XPATH).click()

    # Entering the username and password
    username, password = getLoginDetails()

    driver.find_element(By.ID, "MaskedRegNo").send_keys(username)
    driver.find_element(By.ID, "Password").send_keys(password)
    
    # Clicking the recaptcha button
    driver.switch_to_frame(driver.find_element(By.TAG_NAME, "iframe"))
    driver.find_element(By.XPATH, CAPTCHA_XPATH).click()
    sleep(12) if not headless else sleep(2)
    driver.switch_to.default_content()

    try:
        driver.find_element(By.ID, "LoginSubmit").click()
    except ElementClickInterceptedException:
        driver.quit()
        raise ElementClickInterceptedException("Recaptcha not solved")
        
    driver.find_element(By.ID, "Dash_Board").click()    
    
    # Get table
    table = driver.find_element(By.XPATH, DB_TABLE_XPATH)

    sleep(2)

    rows = []
    for row in table.find_elements(By.TAG_NAME, "tr"):
        rows.append(row.find_elements(By.TAG_NAME, "td"))

    serializedData = {}
    serializedData["tag"] = "Main"
    innerDict = {}

    for row in rows:
        courseCode = row[0].text
        title = row[1].text
        credits = int(row[2].text)
        attendance = row[5].text.split("\n")
        innerDict[title] = {
            "title": title,
            "courseCode": courseCode,
            "credits": credits,
            "labAttendance": attendance[0] if len(attendance) > 1 else None,
            "theoryAttendance": attendance[1] if len(attendance) > 1 else attendance[0]
        }
    serializedData["data"] = innerDict
    serializedData["lastUpdated"] = datetime.now().strftime("%d %B, %Y - %I:%M:%S %p")
        
    writeJson(serializedData)
    yield serializedData
        
    # Getting details about each course
    for index,row in enumerate(rows):
        marksData = {}
        innerDict = {}
        findRow(index, driver).click() # Clicking the row to expand it
        marksData["tag"] = driver.find_element(By.XPATH, "/html/body/div/header/div[3]/div/div[1]/h3").text
        driver.find_element(By.CSS_SELECTOR, "a[title='Marks Summary']").click()
        
        count = 0
        for table in driver.find_elements(By.TAG_NAME, "tbody"):
            for row in table.find_elements(By.TAG_NAME, "tr"):
                details = row.find_elements(By.TAG_NAME, "td")
                innerDict[count] = {
                    "name": details[0].text,
                    "obtainedMarks": details[1].text,
                    "totalMarks": details[2].text,
                    "date": details[3].text,
                }
                count += 1
        
        marksData["data"] = innerDict
        marksData["lastUpdated"] = datetime.now().strftime("%d %B, %Y - %I:%M:%S %p")
        writeJson(marksData)
        
        yield marksData
        
        driver.back()
        driver.back()
        sleep(1)
        
def findRow(index, driver):  # Just a helper function
        table = driver.find_element(By.XPATH, DB_TABLE_XPATH)
        return table.find_elements(By.TAG_NAME, "tr")[index]
            
def prettyPrint(data):
    if data["tag"] == "Main":
        print("Main Details")
        header = ["Name", "Course Code", "Credits", "Theory Attendance", "Lab Attendance"]
        tabulatedData = []
        for key, value in data["data"].items():
            tabulatedData.append([value["title"], value["courseCode"],
                                value["credits"], value["theoryAttendance"],
                                "N/A" if value["labAttendance"] == None else value["labAttendance"]])
        print(tabulate(tabulatedData, headers=header, tablefmt="fancy_grid"))
        print(f"Last Updated: {data['lastUpdated']}\n")
        
    else:
        print(data["tag"])
        time = data["lastUpdated"]
        if not data["data"]:
            print("No data found")
        else:
            tabulatedData = []
            header = ["Name", "Obtained Marks", "Total Marks", "Date"]
            for data in data["data"].values():
                tabulatedData.append([data["name"], data["obtainedMarks"], data["totalMarks"], data["date"]])
            print(tabulate(tabulatedData, headers=header, tablefmt="fancy_grid"))
        print(f'Last Updated: {time}\n')
            
def getOffline():
    data = readJson("Main")
    yield data
    for course in data["data"].keys():
        yield readJson(course)
            
                

