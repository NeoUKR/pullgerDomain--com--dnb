import squirrel
from pullgerFootPrint.com.dnb import search
import time

class Root():
    authorizated = None
    squirrel = None
    currentObject = None

    def __init__(self):
        self.squirrel = SquairrelCore.Squirrel('selenium')
        if self.squirrel.initialize() != True:
            raise Exception("Initialization Error")

    def getRoot(self):
        result = None

        if self.squirrel_initialized != None:
            result = self.squirrel.get('https://www.dnb.com/')

        if result == True:
            self.currentObject = self

        return result

    def getSearch(self, searchString = None):
        self.currentObject = _Search(self, searchString)

        return self.currentObject

class _Search(Root):

    fetch = None

    class fenchingSeach():
        _currentList = None
        _curElement = None
        _parentObject = None
        name = None
        href = None
        idName = None
        idUUID = None

        def __init__(self, parent):
            self._parentObject = parent
            self._currentList = search.getListOfCompany(self._parentObject.squirrel)

        def __iter__(self):
            self._curElement = 0
            return self

        def __next__(self):
            if self._curElement >= len(self._currentList):
                raise StopIteration
            else:
                self.name = self._currentList[self._curElement]['name']
                self.href = self._currentList[self._curElement]['href']
                splitedHREF = self.href.split('/')
                if splitedHREF[-2] == 'business-directory':
                    splitedID = splitedHREF[-1].split('.')
                    if splitedID[0] == 'company-profiles' and splitedID[-1] == 'html':
                        self.idName = splitedID[1]
                        self.idUUID = splitedID[2]
                    else:
                        raise Exception('Error on fetch result')
                else:
                    raise Exception('Error on fetch result')

                self._curElement += 1
                return self

        def __len__(self):
            return len(self._currentList)

        def __list__(self):
            pass

        def getOrganization(self):
            return Organization(self._parentObject, self.idName, self.idUUID)

    def __init__(self, parent, searchString = None):
        self.authorizated = parent.authorizated
        self.squirrel = parent.squirrel
        self.currentObject = self
        self.getSearch(searchString)

    def getSearch(self, searchString = None):
        if searchString == None:
            self.squirrel.get('https://www.dnb.com/site-search-results.html')
        else:
            self.squirrel.get(f'https://www.dnb.com/site-search-results.html#AllSearch={searchString}&tab=Company%20Profiles')

            if self.isLoadCorrect():
                time.sleep(2)
                self.fetch = self.fenchingSeach(self)
            else:
                raise Exception('incorrect search loaded')

    def isLoadCorrect(self):
        webELEM = self.squirrel.find_XPATH('//div[@class="SinglePageSearch basecomp parbase section"]')

        if webELEM != None:
            return True
        else:
            return False


class Organization(Root):
    idName = None
    idUUID = None
    authorizated = None
    squirrel = None
    currentObject = None
    #####
    website = None
    revenue = None
    href = None


    def __init__(self, parent, idName, idUUID):
        self.authorizated = parent.authorizated
        self.squirrel = parent.squirrel
        self.currentObject = self

        self.idName = idName
        self.idUUID = idUUID

        self.getOrganization()

    def isLoadCorrect(self):
        webELEM = self.squirrel.find_XPATH('//div[@class="main_content"]')

        if webELEM != None:
            return True
        else:
            return False

    def getOrganization(self, idName = None, idUUID = None):
        if idName == None and idUUID == None:
            if self.idName != None and self.idUUID != None:
                url = f'https://www.dnb.com/business-directory/company-profiles.{self.idName}.{self.idUUID}.html'
                self.squirrel.get(url)
                if self.isLoadCorrect():
                    self.href = url
                    time.sleep(2)
                    self.renewDATA()
                else:
                    Exception("Loading ERROR.")

    def renewDATA(self):
        webELEM = self.squirrel.find_XPATH('//a[@id="hero-company-link"]')

        if webELEM != None:
            self.website = webELEM.get_attribute('href')

        revtnueValue = None
        revenueELEM = self.squirrel.find_XPATH('//span[@name="revenue_in_us_dollar"]/span')
        if revenueELEM != None:
            revenueSPITED = list(filter(None, revenueELEM.text.strip().split(' ')))

            if len(revenueSPITED) != 0:
                if len(revenueSPITED) == 2:
                    revenueValueText = revenueSPITED[0].replace('$', '')
                    try:
                        revtnueValue = float(revenueValueText)
                    except:
                        test = 1
                        pass

                    if revtnueValue != None:
                        if revenueSPITED[1] == 'billion':
                            revtnueValue = int(revtnueValue * 1000000000)
                        elif revenueSPITED[1] == 'million':
                            revtnueValue = int(revtnueValue * 1000000)
                        else:
                            test = 1
                            pass
                else:
                    test = 1
                    pass
        else:
            pass

        self.revenue = revtnueValue