from logging import error
from types import FunctionType, LambdaType, MethodType
import requests as req 
import random 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

MAX_NAMES = 25
MIN_NAME_LENGHT = 4
MAX_NAME_LENGHT = 4

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

class ProxyCollection:  
    def __init__(self):
        self.__proxies = list()


    def UpdateProxyList(self): 
        try:
            response = req.get("https://www.proxy-list.download/api/v1/get?type=http&anon=elite")

            if response.status_code == 200 and response.text.replace(" ", "") != "":
                for line in response.text.split("\n"):
                    if line.replace(" ", "") == "":
                        continue 

                    self.__proxies.append(f"http://{line}")
            else:
                raise Exception()
        except:
            print("Failed to get Proxy-List")

    def GetRandomProxy(self):
        return {"http":self.__proxies[clamp(0, round(random.random() * len(self.__proxies)), len(self.__proxies) - 1)]} 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

class GitHubNameChecker:
    OnAvailableFound   = lambda self,name:print(f"'> {name}' is available.") 
    OnUnavailableFound = lambda self,name:None  
    On25Checked        = lambda self,count:print(f"> {count} names checked.") 
    OnDone             = lambda self:None 

    def __init__(self):
        self.__proxyManager = ProxyCollection()
        self.__proxyManager.UpdateProxyList()
        self.__availableNames = []
        self.__nameCounter = 0


    def GetNames(self) -> list:
        return self.__availableNames


    def __isAvailableGitHubName(self, name: str, useAlternative: bool = False) -> bool:
        try:
            httpProxy = self.__proxyManager.GetRandomProxy()

            if useAlternative == False:
                response = req.get(f"https://api.github.com/users/{name}", proxies=httpProxy)
            else:
                response = req.get(f"https://github.com/{name}", proxies=httpProxy)

            if response == None:
                return True 

            # if we are rate limited, fall back to just requesting the profile itself via github.com 
            if response.status_code == 403: 
                return self.__isAvailableGitHubName(name, True)

            if response.status_code == 404:
                return True 
        except:
            return True

        return False 


    def __bruteForceRecursive(self, limit: int, builder: str, minLength: int, maxLength: int, charset: str):
        for char in charset:
            if len(self.__availableNames) >= limit:
                break

            temp = builder + char

            if len(temp) > maxLength:
                break 

            if(len(temp) >= minLength):
                self.__bruteCallback(temp)

            self.__bruteForceRecursive(limit, temp, minLength, maxLength, charset)


    def Bruteforce(self, limit:int = 20, minLength: int = 0, maxLength: int = 9, charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
        self.__availableNames = list()
        self.__bruteForceRecursive(limit, "", minLength, maxLength, charset)
        self.OnDone()

    def __bruteCallback(self, text: str):
        if self.__isAvailableGitHubName(text) == True:
            self.OnAvailableFound(text)
            self.__availableNames.append(text)
        else:
            self.OnUnavailableFound(text)
            
            if self.__nameCounter % 25 == 0 and self.__nameCounter != 0:
                self.On25Checked(self.__nameCounter)

        self.__nameCounter += 1

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

print("Checking names...")

# 4 is the smallest number avaiable in 2021 

bruteforce = GitHubNameChecker()

def OnFinished():
    print("\nFinished.\n")

    names = bruteforce.GetNames()

    if len(names) > 0:
        print("Available Names:")
    
        for name in names:
            print(f"> '{name}'")
    else:
        print("No available Names.")

bruteforce.OnDone = OnFinished
bruteforce.Bruteforce(MAX_NAMES, MIN_NAME_LENGHT, MAX_NAME_LENGHT, "abcdefghijklmnopqrstuvwxyz0123456789")