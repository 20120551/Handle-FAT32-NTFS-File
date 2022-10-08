from datetime import datetime, timedelta
from utils.buffer import *
from utils.directory import Directory
from utils.factory import *
from constant.attribute import *
from constant.offset import *
from constant.document import *
from pattern.composite import *
from build.console import *

class NtfsFile:
    def __init__(self, file, root:CItem, directory:Directory):
        self.file = file
        self.root:CItem = root
        self.directory = directory

    def readPartitionRootSector(self):
        #get first sector to read prs
        buffer = getBufferDataBySector(self.file, 0, 1)

        self.sectorSize = getValueOfBufferByOffset(buffer, PDS_SECTOR_SIZE['hex'], PDS_SECTOR_SIZE['byte'])
        self.sc = getValueOfBufferByOffset(buffer, PDS_SECTOR_CLUSTER['hex'], PDS_SECTOR_CLUSTER['byte'])
        self.totalSector = getValueOfBufferByOffset(buffer, PDS_TOTAL_SECTOR['hex'], PDS_TOTAL_SECTOR['byte'])
        self.startedMFTCluster = getValueOfBufferByOffset(buffer, PDS_STARTED_MFT_CLUSTER['hex'], PDS_STARTED_MFT_CLUSTER['byte'])
        self.mirrorMFTCluster = getValueOfBufferByOffset(buffer, PDS_MIRROR_MFT_CLUSTER['hex'], PDS_MIRROR_MFT_CLUSTER['byte'])

        print(f'Sector size: {self.sectorSize}(bytes)')
        print(f'Sector/cluster: {self.sc}(s)')
        print(f'Total Sector: {self.totalSector}(s)')
        print(f'Started MFT Cluster: {self.startedMFTCluster * self.sc}(s)')
        print(f'Mirror MFT Cluster: {self.mirrorMFTCluster * self.sc}(s)')

    def readMasterFileTable(self):
        sector = 0
        subFolder:CItem = None

        size = 0
        name = ''
        content = ''
        createAt = ''
        updateAt = ''

        total_skip_signature = 0

        while sector <= self.totalSector:
            skip = False
            #read 2 sector = 1024 byte 
            buffer = getBufferDataBySector(self.file, sector + self.startedMFTCluster * self.sc, 2)

            signature = getBufferDataByOffset(buffer, MFT_SIGNATURE['hex'], MFT_SIGNATURE['byte'])

            if b'FILE' != signature:
                sector = sector + 2
                total_skip_signature +=1

                if total_skip_signature > 100: break
                continue

            isFolder = getValueOfBufferByOffset(buffer, MFT_ATTRIBUTE_TYPE['hex'], MFT_ATTRIBUTE_TYPE['byte']) & 0x02

            attributeOffsetStarted = getValueOfBufferByOffset(buffer, MFT_STARTED_ATTRIBUTE['hex'], MFT_STARTED_ATTRIBUTE['byte'])

            index = 0
            attributeType = 0x00
            while index <= 1024 and attributeType != 0xFFFFFFFF:
                attributeType = getValueOfBufferByOffset(
                    buffer, 
                    attributeOffsetStarted + ATB_TYPE['hex'], 
                    ATB_TYPE['byte']
                )
                attributeSize = getValueOfBufferByOffset(
                    buffer,
                    attributeOffsetStarted + ATB_ATTRIBUTE_SIZE['hex'], 
                    ATB_ATTRIBUTE_SIZE['byte']
                )
                
                resident = getValueOfBufferByOffset(
                    buffer,
                    attributeOffsetStarted +  ATB_IS_RESIDENT['hex'], 
                    ATB_IS_RESIDENT['byte']
                )
                
                contentStarted = getValueOfBufferByOffset(
                    buffer,
                    attributeOffsetStarted +  ATB_STARTED_CONTENT['hex'], 
                    ATB_STARTED_CONTENT['byte']
                )

                contentSize = getValueOfBufferByOffset(
                    buffer,
                    attributeOffsetStarted + ATB_CONTENT_SIZE['hex'],
                    ATB_CONTENT_SIZE['byte']
                )

                currentContent = contentStarted + attributeOffsetStarted
                if attributeType == FILENAME:
                    # print('FILENAME')
                    nameLength = getValueOfBufferByOffset(
                        buffer,
                        currentContent + FN_NAME_LENGTH['hex'], 
                        FN_NAME_LENGTH['byte']
                    )
                    rawName = getBufferDataByOffset(
                        buffer, 
                        currentContent +  FN_NAME['hex'], 
                        FN_NAME['byte'] + nameLength * 2
                    )
                    name = rawName.decode('utf-16le')

                    if name.startswith('$'):
                        skip = True
                        break

                    parentIndex = getValueOfBufferByOffset(buffer, currentContent, 6)

                    createAt = getValueOfBufferByOffset(
                        buffer, 
                        currentContent +  FN_CREATE_AT['hex'], 
                        FN_CREATE_AT['byte']
                    )

                    updateAt = getValueOfBufferByOffset(
                        buffer, 
                        currentContent +  FN_UPDATE_AT['hex'], 
                        FN_UPDATE_AT['byte']
                    )
                elif attributeType == DATA:
                    # print('DATA')

                    #get actually size
                    if resident == 0:
                        size = contentSize
                    else:
                        size = getValueOfBufferByOffset(buffer, attributeOffsetStarted + 0x30, 7)

                    #handle content
                    if name.endswith('.txt'): 
                        if resident == 0:
                            rawContent = getBufferDataByOffset(buffer, currentContent, contentSize)
                        else:
                            offsetRunList = getValueOfBufferByOffset(buffer, attributeOffsetStarted + 0x20, 2)
                            totalCluster = getValueOfBufferByOffset(buffer, attributeOffsetStarted + offsetRunList + 1, 1)
                            clusterStarted = getValueOfBufferByOffset(buffer, attributeOffsetStarted + offsetRunList + 2, 2)
                            rawContent = getContentByCluster(self.file, clusterStarted, totalCluster, self.sc)
                        content = rawContent.decode('utf-8')
                    else:
                        try:
                            extension = document[f'.{name.split(".")[-1]}']
                        except KeyError:
                            extension = 'Not support'

                        content = f'extension - {extension}'

                attributeOffsetStarted = attributeOffsetStarted + attributeSize
                index = index + attributeSize

            if not name.startswith('$') and not skip:
                if isFolder:
                    path = self.directory.add(parentIndex, sector / 2, name)
                else:
                    path = f'{self.directory.get(parentIndex)}\{name}'

                subFolder = createItem(isFolder, (name, size, content, path, createAt, updateAt))
                parentFolder = self.root.findByPath(self.directory.get(parentIndex))

                if parentFolder is not None:
                    parentFolder.add(subFolder)

            sector = sector + 2

    def build(self):
        console = Console(self.root)
        console.windowShell()
            
