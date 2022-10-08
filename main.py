from msilib.schema import Directory
from utils.disk import Disk

def main():
    try:
        #init root path for folder
        disk = Disk()
        #generate object file for disk driver
        disk.selectDiskPath()
        file = disk.generateDiskFile()
        #main

        directory = disk.generateDirectory()
        ntfsFile = disk.generateNTFSFile(file, directory)

        ntfsFile.readPartitionRootSector()
        ntfsFile.readMasterFileTable()

        ntfsFile.build()
    except:
        pass
if __name__ == '__main__':
    main()