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

        #generate directory
        directory = disk.generateDirectory()
        #create new tnfs file system
        ntfsFile = disk.generateNTFSFile(file, directory)

        #demo handle PARTITION BOOT SECTOR
        print('\n\n--------------PARTITION BOOT SECTOR--------------')
        ntfsFile.readPartitionRootSector()

        print('\n\nPress enter to switch to READ MASTER FILE TABLE function demo')
        input()

        #demo handle READ MASTER FILE TABLE
        #build DIRECTORY TREE by console
        ntfsFile.build()
    except:
        pass
if __name__ == '__main__':
    main()