from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt

from pipInterface import pipInterface

class pipGUI(QMainWindow):
    def __init__(self):
        #ui setup
        super().__init__()
        uic.loadUi("pip_ui.ui", self)
        self.messageBox = QMessageBox()
        
        #set up top bar
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowMinimizeButtonHint
        )

        #signals and slots
        self.installedPackagesTable.cellDoubleClicked.connect(self.selectInstalledPackage)
        self.packageTable.cellDoubleClicked.connect(self.selectSearchedPackage)

        self.packageSearchEntry.returnPressed.connect(self.updateSearchTable)
        self.searchButton.clicked.connect(self.updateSearchTable)

        self.installButton.clicked.connect(self.installPackage)
        self.uninstallButton.clicked.connect(self.uninstallPackage)
        self.updateButton.clicked.connect(self.updatePackage)
        self.updatePipButton.clicked.connect(self.updatePip)

        #pip interface setup
        self.pipInterface = pipInterface()
        self.selectedPackage = None

        #tables setup
        self.populateInstalledTable()

        #info text setup
        self.packageInfoTextArea.setMarkdown("## Information about selected packages will appear here.")
        self.packageInfoTextArea.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)

    def populateInstalledTable(self):
        installedPackages = self.pipInterface.installedPackages

        self.setTableRows(installedPackages, self.installedPackagesTable)

    def setTableRows(self, values: list, tableWidget):
        tableWidget.setRowCount(0)

        for row in values:
            rowPosition = tableWidget.rowCount()
            tableWidget.insertRow(rowPosition)

            for index, item in enumerate(row):
                tableWidget.setItem(rowPosition, index, QTableWidgetItem(item))

    def selectInstalledPackage(self):
        selectedTableRow = self.installedPackagesTable.currentRow()
        selectedPackageName = self.installedPackagesTable.item(selectedTableRow, 0).text()

        self.setButtonStates(False, True, True)

        self.selectedPackage = selectedPackageName
        self.displayInstalledPackage(selectedPackageName)

    def selectSearchedPackage(self):
        selectedPackageName = self.packageTable.currentItem().text()

        try:
            packageData = self.pipInterface.getModuleInfo(selectedPackageName)
        except: #sometimes packages are not available on PyPi
            self.displayMessage("Error", f"Unfortunately the package '{selectedPackageName}' is no longer available from PyPi")
            return

        if self.isInstalled(selectedPackageName):
            self.setButtonStates(False, True, True)
        else:
            self.setButtonStates(True, False, False)

        self.selectedPackage = selectedPackageName
        self.displayPackage(selectedPackageName)

    def updateSearchTable(self):
        searchTerm = self.packageSearchEntry.text()
        if not searchTerm: return #if no search term is entered, do not search

        #getting and parsing search results
        searchResults = [[name] for name in self.pipInterface.searchPackages(searchTerm)["Package Name"]] 
        self.setTableRows(searchResults, self.packageTable)

    def displayInstalledPackage(self, packageName):
        packageData = self.pipInterface.installedModuleInfo(packageName)
        self.packageInfoTextArea.clear()

        #extracting variables for f-string substition
        name = packageData["Name"]
        author = packageData["Author"]
        version = packageData["Version"]
        url = packageData["Home-page"]
        email = packageData["Author-email"]
        packageLicense = packageData["License"]
        summary = packageData["Summary"]
        requirementsString = ", ".join(packageData["Requirements"])
        requiredBysString = ", ".join(packageData["Required By"])

        #constructing html (given certain items have a non-None value)
        self.packageInfoTextArea.insertHtml(f"<h1>{name}<br/></h1>")
        self.packageInfoTextArea.insertHtml(f"<h3>Version: {version}<br/></h3>")
        self.packageInfoTextArea.insertHtml(f'<h3>Author: <a href="{email}">{author}</a><br/></h3>')

        if packageLicense: self.packageInfoTextArea.insertHtml(f"<h3>License: {packageLicense}<br/></h3>")

        self.packageInfoTextArea.insertHtml(f'<a href="https://pypi.org/project/{name}/"><br/>PyPi Link<br/></a>')
        
        if url: self.packageInfoTextArea.insertHtml(f'<a href="{url}">Package Home Page<br/></a>')

        if summary: self.packageInfoTextArea.insertHtml(f"<p><br/>{summary}<br/></p>")

        if requirementsString: self.packageInfoTextArea.insertHtml(f"<p><br/><b>Requirements:</b> {requirementsString}</p>")

        if requiredBysString: self.packageInfoTextArea.insertHtml(f"<p><br/><b>Required By:</b> {requiredBysString}</p>")

    def displayPackage(self, packageName):
        packageData = self.pipInterface.getModuleInfo(packageName)

        self.packageInfoTextArea.clear()
        
        #extracting variables for f-string substition
        name = packageData["name"]
        author = packageData["author"]
        version = packageData["version"]
        url = packageData["home_page"]
        email = packageData["author_email"]
        packageLicense = packageData["license"]
        summary = packageData["summary"]
        packageUrl = packageData["package_url"]
        platform = packageData["platform"]
        requirementsString = "<br/>".join(packageData["requires_dist"])
        pythonRequired = packageData["requires_python"]

        #constructing html (given certain items have a non-None value)
        #self.packageInfoTextArea.insertHtml(
        self.packageInfoTextArea.insertHtml(f"<h1>{name}<br/></h1>")
        self.packageInfoTextArea.insertHtml(f"<h3>Version: {version}<br/></h3>")
        self.packageInfoTextArea.insertHtml(f'<h3>Author: <a href="{email}">{author}</a><br/></h3>')

        if packageLicense: self.packageInfoTextArea.insertHtml(f"<h3>License: {packageLicense}<br/></h3>")

        self.packageInfoTextArea.insertHtml(f'<a href="{packageUrl}"><br/>PyPi Link<br/></a>')

        if url: self.packageInfoTextArea.insertHtml(f'<a href="{url}">Package Home Page<br/></a>')

        if summary: self.packageInfoTextArea.insertHtml(f"<p><br/>{summary}<br/></p>")

        if platform: self.packageInfoTextArea.insertHtml(f"<p><br/><b>Platform:</b> {platform}</p>")
        if pythonRequired: self.packageInfoTextArea.insertHtml(f"<p><br/><b>Python Version/s:</b> {pythonRequired}</p>")
        if requirementsString: self.packageInfoTextArea.insertHtml(f"<p><br/><b>Requirements:</b> <br/>{requirementsString}</p>")

    def displayMessage(self, title, message):
        self.messageBox.setText(title)
        self.messageBox.setInformativeText(message)
        self.messageBox.exec_()
    
    def setButtonStates(self, installButton, uninstallButton, updateButton):
        self.installButton.setEnabled(installButton)
        self.uninstallButton.setEnabled(uninstallButton)
        self.updateButton.setEnabled(updateButton)

    def isInstalled(self, packageName):
        if packageName in [package[0] for package in self.pipInterface.installedPackages]:
            return True
        return False

    def installPackage(self):
        self.pipInterface.installPackage(self.selectedPackage)
        self.pipInterface.updateInstalledPackages()

        self.displayMessage("Installation Complete", f"{self.selectedPackage} has been successfully installed.")
        self.setButtonStates(False, True, True)

        self.populateInstalledTable()

    def uninstallPackage(self):
        self.pipInterface.uninstallPackage(self.selectedPackage)
        self.pipInterface.updateInstalledPackages()

        self.displayMessage("Uninstallation Complete", f"{self.selectedPackage} has been successfully uninstalled.")
        self.setButtonStates(True, False, False)

        self.populateInstalledTable()

    def updatePackage(self):
        self.pipInterface.updatePackage(self.selectedPackage)
        self.pipInterface.updateInstalledPackages()
        
        self.displayMessage("Update Complete", f"{self.selectedPackage} has been successfully updated.")

        self.populateInstalledTable()

    def updatePip(self):
        self.pipInterface.updatePip()
        self.displayMessage("Update Complete", "pip has been successfully updated.")