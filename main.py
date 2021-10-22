from logging import error
from types import LambdaType
import requests as req 
import time 
import random 
import math 

def FetchProxyList() -> list:
    result = list() 
    try:
        response = req.get("https://www.proxy-list.download/api/v1/get?type=http&anon=elite")
        if response.status_code == 200 and response.text.replace(" ", "") != "":
            for line in response.text.split("\n"):
                if line.replace(" ", "") == "":
                    continue 
                result.append(f"http://{line}")
        else:
            raise Exception()
    except:
        print("Failed to get Proxy-List")
    return result 

allProxies = FetchProxyList()

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def GetProxy():
    return {"http":allProxies[clamp(0, round(random.random() * len(allProxies)), len(allProxies) - 1)]} 

attemptCounter = 0
def IsAvailableGitHubName(name: str, useAlternative: bool = False) -> bool:
    defaultApi = f"https://api.github.com/users/{name}"

    try:
        if useAlternative == False:
            response = req.get(defaultApi, proxies=GetProxy())
        else:
            response = req.get(f"https://github.com/{name}", proxies=GetProxy())

        if response == None:
            return True 

        # if we are rate limited, fall back to just requesting the profile itself via github.com 
        if response.status_code == 403: 
            return IsAvailableGitHubName(name, True)

        if response.status_code == 404:
            return True 
    except:
        return True

    return False 

def BruteThroughNames(initialString: str, callback, minLength: int = 0, maxLength: int = 9, charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    if len(initialString) >= maxLength:
        return

    for char in charset:
        temp = initialString + char

        if len(temp) >= maxLength:
            return

        if(len(temp) >= minLength):
            callback(temp)

        BruteThroughNames(temp, callback, minLength, maxLength, charset)

    return None 

availableNames = []
nameCounter = 0
def BruteCallback(text: str):
    
    global nameCounter

    if IsAvailableGitHubName(text) == True:
        print(f"{text} is available")
        availableNames.append(text)
    else:
        print(f"{text} is unavailable")
        if nameCounter % 10 == 0 and nameCounter != 0:
            print(f"{nameCounter} names checked.")

    nameCounter += 1

print("Checking names...")

BruteThroughNames("", BruteCallback, 3, 5, "abcdefghijklmnopqrstuvwxyz0123456789")

if len(availableNames) > 0:
    print("All available Names:")
    for name in availableNames:
        print(name)
else: 
    print("No names found.")