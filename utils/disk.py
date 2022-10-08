import os
from utils.directory import Directory
from fileHandler.NtfsFile import NtfsFile
from pattern.composite import *

class Disk:
    def __init__(self):
        self.platformName = os.name
        if self.platformName == 'nt':
            print('===============you are running on nt window===============')
        elif self.platformName == 'posix':
            print('===============you are running on posix===============')
        else:
            raise Exception(f'we are not implement in {self.platformName} platform')
    def selectDiskPath(self):
        diskPath = input('type your disk path: ')

        if self.platformName == 'nt':
            self.diskPath = f'\\\\.\\{diskPath}:'
        else:
            self.diskPath = diskPath

    def generateDiskFile(self):
        diskFile = os.open(self.diskPath, os.O_BINARY)
        diskObjectFile = os.fdopen(diskFile, 'rb')
        return diskObjectFile

    def generateNTFSFile(self, file, directory):
        root = CFolder(self.diskPath[-2], f'{self.diskPath[-2]}:')
        ntfsFile = NtfsFile(file, root, directory)
        return ntfsFile
    
    def generateDirectory(self):
        directory = Directory(f'{self.diskPath[-2]}:')
        return directory


