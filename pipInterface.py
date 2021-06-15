#modules
import requests
from lxml import html
import pandas as pd
import subprocess

#pip interface class
class pipInterface:
    def __init__(self):
        self.allPackages = self.getAllPackages()
        self.installedPackages = self.getInstalledPackages()

    def getAllPackages(self) -> pd.DataFrame:
        #get and parse raw html from pypi site
        rawPage = requests.get("https://pypi.org/simple/")
        pageTree = html.fromstring(rawPage.content)
        
        #scrape data from html
        packageNames = pageTree.xpath("//a/text()")
        return packageNames
        
        #put data collected into dataframe
        packageData = {"Package Name": packageNames}
        return pd.DataFrame(data=packageData)

    def getInstalledPackages(self) -> dict:
        #get response to command 'pip list' and extract module names and versions
        rawListResponse = subprocess.run(["pip3", "list"], capture_output=True).stdout.decode("utf-8")
        modulesOnly = rawListResponse.split("\n")[2:-1]
  
        nameAndVersions = [text.split() for text in modulesOnly]
        return nameAndVersions

    def searchPackages(self, searchTerm: str):
        #search all packages for their name's closeness to the search term
        allPackagesDF = pd.DataFrame({"Package Name": self.allPackages})

        #check if search term in package name, then sort by proportion of name made up by the search term
        searchResults = allPackagesDF.loc[allPackagesDF["Package Name"].str.contains(searchTerm, regex=False, case=False)]
        searchResults["sortValue"] = searchResults["Package Name"].apply(lambda text: len(searchTerm)/len(text))
        sortedResults = searchResults.sort_values("sortValue", ascending=False)
        
        return sortedResults.drop("sortValue", axis=1)

    def installedModuleInfo(self, moduleName: str) -> dict:
        #get module info from command 'pip show <moduleName>'
        showCommandResponse = subprocess.run(["pip3", "show", moduleName], capture_output=True).stdout.decode("utf-8")
        moduleData = dict(line.split(": ") for line in showCommandResponse.split("\n")[:-1])
        
        #create lists of dependencies from comma-separated strings
        moduleData["Requirements"] = moduleData.pop("Requires").split(", ")
        moduleData["Required By"] = moduleData.pop("Required-by").split(", ")
        moduleData.pop("Location")
        
        #replace bad values
        for key in moduleData:
            if moduleData[key] == "UNKNOWN":
                moduleData[key] = None
            elif moduleData[key] == ['']:
                moduleData[key] = []
        
        return moduleData

    def getModuleInfo(self, moduleName: str) -> dict:
        #get JSON data on module from pypi API
        moduleDataJSON = requests.get(f"https://pypi.org/pypi/{moduleName}/json").json()
        moduleInfo = moduleDataJSON["info"]
        
        #extract required data from JSON response into dictionary
        requiredInfo = dict()
        
        for key in ["author", "author_email", "description", "description_content_type", 
                    "home_page", "license", "name", "package_url", "platform", 
                    "requires_dist", "requires_python", "summary", "version"]:
            requiredInfo[key] = moduleInfo[key]

        #replace bad values
        for key in requiredInfo:
            if requiredInfo[key] == "UNKNOWN": 
                requiredInfo[key] = None

        if requiredInfo["requires_dist"] == None: requiredInfo["requires_dist"] = []
        
        return requiredInfo

    def updateInstalledPackages(self):
        self.installedPackages = self.getInstalledPackages()

    def installPackage(self, packageName):
        return subprocess.run(["pip3", "install", packageName], capture_output=True).stdout.decode("utf-8")

    def uninstallPackage(self, packageName):
        return subprocess.run(["pip3", "uninstall", "-y", packageName], capture_output=True).stdout.decode("utf-8")

    def updatePackage(self, packageName):
        return subprocess.run(["pip3", "install", "--upgrade", packageName], capture_output=True).stdout.decode("utf-8")

    def updatePip(self):
        return subprocess.run(["pip3", "install", "--upgrade", "pip"], capture_output=True).stdout.decode("utf-8")