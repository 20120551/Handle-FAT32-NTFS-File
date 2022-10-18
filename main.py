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

        volumeType = input('1:       NTFS\nOther:   FAT32\nchoose your volume type: ')

        if volumeType == '1':
            ######=========================DEMO NTFS========================###
            ntfsFile = disk.generateNTFSFile(file, directory)

            #demo handle PARTITION BOOT SECTOR
            print('\n\n--------------PARTITION BOOT SECTOR--------------')
            ntfsFile.readPartitionRootSector()

            print('\n\nPress enter to switch to READ MASTER FILE TABLE function demo')
            input()

            #demo handle READ MASTER FILE TABLE
            #build DIRECTORY TREE by console
            ntfsFile.build()
            
        else:
            ######=========================DEMO FAT32========================###
            #create fat32 file system
            fat32File = disk.generateFat32File(file, directory)
            fat32File.readBootSector()

            print('\n\nPress enter to switch to RDET function demo')
            input()

            #demo handle RDET
            #build DIRECTORY TREE by console
            fat32File.build()
    except:
        pass
if __name__ == '__main__':
    main()