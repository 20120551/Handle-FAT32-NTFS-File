from abc import ABC, abstractmethod

class CItem(ABC):
    @property
    def name(self):
        '''
            name of this folder or file
        '''

    @property
    def name(self):
        '''
            name of this folder or file
        '''

    def add(self, item) -> None:
        '''
            add file on folder
        '''

    @abstractmethod
    def findByPath(self, path) -> None:
        '''
            file folder or file by path
        '''
    @abstractmethod
    def getSize(self) -> int:
        '''
            get size of file or folder
        '''
    @abstractmethod
    def print(self) -> None:
        '''
            print information of file or folder
        '''
    def printContent(self):
        '''
            print content
        '''
        
    def printDetail(self): 
        '''
            print detail
        '''
    def printCurrentItem(self):
        '''
            print current item
        '''
        
class CFile(CItem):
    #override name property
    name = None
    path = None
    def __init__(self, name, path, content, size, createAt, updateAt):
        #init default size for file
        #constructor
        self.name = name
        self.path = path
        self.content = content
        self.size = size
        self.createAt = createAt
        self.updateAt = updateAt



    def findByPath(self, path) -> None:
        if path == self.path:
            return self
        return None

    def getSize(self) -> int:
        return self.size

    def print(self, space) -> None:
        print(f'{space}Name: {self.name}, size: {self.size}')
        
    def printContent(self):
        print(self.content)
        
    def printDetail(self): 
        print(f'FileName: {self.name}')
        print(f'Size: {self.size}')
        print(f'CreateAt: {self.createAt}')
        print(f'UpdateAt: {self.updateAt}')

    def printCurrentItem(self):
        print(self.name)

class CFolder(CItem):
    name = None
    path = None
    def __init__(self, name, path, createAt = 0, updateAt = 0) -> None:
        #init for list of subitem
        self.subItem:list[CItem] = []
        self.name = name
        self.path = path
        self.size = 0
        self.createAt = createAt
        self.updateAt = updateAt

    def add(self, item:CItem) -> None:
        self.subItem.append(item)

    def findByPath(self, path) -> None:
        result = None
        if self.path == path:
            return self
        
        for item in self.subItem:
            if item.path == path:
                return item

            result = item.findByPath(path)
            if result:
                return result
        return None

    def getSize(self) -> int:
        size = 0
        for item in self.subItem:
            size = size + item.getSize()
        return size

    def printCurrentItem(self):
        for item in self.subItem:
            print(item.name)

    def print(self, space='----') -> None:
        
        print(f'{space}Folder: {self.name}, size: {self.getSize()}')

        for item in self.subItem:
            item.print(space*2)

