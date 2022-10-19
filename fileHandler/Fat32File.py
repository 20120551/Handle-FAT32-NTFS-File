from datetime import datetime, timedelta
from constant.FAT32offset import *
from utils.buffer import *
from utils.directory import Directory
from utils.factory import *
from constant.attribute import *
from constant.NTFSoffset import *
from constant.document import *
from pattern.composite import *
from build.console import *

class Fat32File:
    def __init__(self, file, root:CItem, directory:Directory):
        self.file = file
        self.root:CItem = root
        self.directory = directory
    def readBootSector(self):
        # đọc sector đầu tiên lên
        buffer = getBufferDataBySector(self.file, 0, 1)
         # đọc size của sector
        self.sectorSize = getValueOfBufferByOffset(buffer, BS_SECTOR_SIZE['hex'], BS_SECTOR_SIZE['byte'])
        # đọc số sector / cluster
        self.sc = getValueOfBufferByOffset(buffer, BS_SECTOR_CLUSTER['hex'], BS_SECTOR_CLUSTER['byte'])
        # đọc số sector thuộc vùng boot sector
        self.sb = getValueOfBufferByOffset(buffer, BS_SECTOR_BOOT['hex'], BS_SECTOR_BOOT['byte'])
        # Đọc số lượng bảng FAT
        self.totalFat = getValueOfBufferByOffset(buffer, BS_FAT['hex'], BS_FAT['byte'])
        # Số sector/fat
        self.sf = getValueOfBufferByOffset(buffer, BS_SECTOR_FAT['hex'], BS_SECTOR_FAT['byte'])
        #kích thước volume
        self.totalSector = getValueOfBufferByOffset(buffer, BS_TOTAL_SECTOR['hex'], BS_TOTAL_SECTOR['byte'])
        # RDET STARTED
        self.startedRDEFCluster = getValueOfBufferByOffset(buffer, BS_RDET_CLUSTER_STARTED['hex'], BS_RDET_CLUSTER_STARTED['byte'])
        #phần bắt đầu của data
        self.startedDataPosition = self.sb + self.sf * self.totalFat

        #in thông tin
        print( '_________________________________________________________________')
        print(f'     Sector size: {self.sectorSize}(bytes)                       ')
        print(f'     Sector/cluster: {self.sc}(s)                                     ')
        print(f'     Sector/boot sector: {self.sb}(s)                                 ')
        print(f'     A number of Fats: {self.totalFat}(s)                             ')
        print(f'     Sector / fat: {self.sf}(s)                                       ')
        print(f'     Total sector: {self.totalSector}(s)                              ')
        print(f'     Started RDET cluster: {self.startedRDEFCluster}(c)               ')
        print(f'     Started data position: {self.startedDataPosition}(s)             ')
        print( '_________________________________________________________________')

    def getFatTable(self):
        fatTable = getBufferDataBySector(self.file, self.sb, self.sf, self.sectorSize)
        return fatTable

    def getRDETTable(self, clusterBegin):
        # do ta sử dụng fat32 nên RDET là không có định kích thước (32 sector) nên ta phải sử dụng bảng 
        # fat để tra cứu
        
        #đọc bảng fat lên
        fatTable = self.getFatTable()        
        #đọc RDET theo thông tin bảng fat và thông tin cluster begin
        clusters = [clusterBegin]

        # FAT 32 mặc định đọc bảng fat là 4 bytes
        cluster = getValueOfBufferByOffset(fatTable, clusterBegin * 4, 4)

        # lặp tới khi nào là cluster kết thúc thì thôi
        while cluster not in [0x00000000, 0xFFFFFF0, 0xFFFFFFF, 0XFFFFFF7, 0xFFFFFF8, 0xFFFFFFF0]:
            print('ooo') 
            clusters.append(cluster)
            # tăng cluster để tiếp tục duyệt tới cluster tiếp theo
            cluster = cluster * 4
            cluster = getValueOfBufferByOffset(fatTable, cluster, 4)
        # trả về đúng vị trí để tiện cho việc lấy buffer từ sector
        return [cluster - 2 for cluster in clusters]

    def getNameBySubEntry(self, subEntry):
        name = b''

        for sub in subEntry:
            name += getBufferDataByOffset(sub, MS_A['hex'], MS_A['byte'])
            name += getBufferDataByOffset(sub, MS_B['hex'], MS_B['byte'])
            name += getBufferDataByOffset(sub, MS_C['hex'], MS_C['byte'])

        name = name.decode('utf-16le')
        # xóa các kí tự kết thúc entry
        if name.find('\x00') > 0:
            name = name[:name.find('\x00')]
        return name
        
    def readDirectoryEntryTable(self):
        # lưu trữ file hoặc folder bằng composite pattern
        subFolder:CItem = None

        #cluster index
        index = 0
        # lấy bảng sdet đầu tiên (dạng cluster)
        SDETCluster = self.getRDETTable(self.startedRDEFCluster)
        # lấy bảng sdet dạng sector để duyệt
        SDETBuffer = getContentByCluster(self.file, self.startedRDEFCluster - 2, len(SDETCluster), self.sc, self.startedDataPosition)
        # lưu trữ các entry phụ
        subEntry = []
        entryType = 1
        
        #duyệt tới entry kết thúc thì dừng
        while entryType != 0:
            # lưu các thông tin lưu trữ của file hoặc folder
            size = 0
            name = ''
            path = ''
            content = ''
            createAt = ''
            updateAt = ''

            # đọc qua các entry
            entryBuffer = getBufferDataByOffset(SDETBuffer, index, 32, self.sectorSize)

            entryType = getValueOfBufferByOffset(entryBuffer, ME_STATE['hex'], ME_STATE['byte'])

            # entry type là folder
            if entryType & 0x10 == 0x10:
                # print('is folder') 
                isFolder = True
            # entry type là tập tin
            elif entryType & 0x20 == 0x20:
                # print('is file') 
                isFolder = False
            #entry type là entry phụ
            elif entryType & 0x0F == 0x0F:
                # print('sub entry')  
                subEntry.append(entryBuffer)
                index = index + 32
                continue
            else:
                index = index + 32
                continue

            createAt = getValueOfBufferByOffset(entryBuffer, ME_CREATE_AT['hex'], ME_CREATE_AT['byte'])
            updateAt = getValueOfBufferByOffset(entryBuffer, ME_UPDATE_AT['hex'], ME_UPDATE_AT['byte'])
            size = getValueOfBufferByOffset(entryBuffer, ME_CONTENT_SIZE['hex'], ME_CONTENT_SIZE['byte'])
            lowWord = getValueOfBufferByOffset(entryBuffer, ME_LOW_WORD['hex'], ME_LOW_WORD['byte'])
            highWord = getValueOfBufferByOffset(entryBuffer, ME_HIGH_WORD['hex'], ME_HIGH_WORD['byte'])
            mainName = getBufferDataByOffset(entryBuffer, ME_MAIN_NAME['hex'], ME_MAIN_NAME['byte']).decode('utf-8', errors='ignore').strip().lower()
            expandName = getBufferDataByOffset(entryBuffer, ME_EXPAND_NAME['hex'], ME_EXPAND_NAME['byte']).decode('utf-8', errors='ignore').strip().lower()

            
            if mainName.startswith('.') or mainName.startswith('..'):
                index = index + 32
                continue

            if len(subEntry) > 0:
                name = self.getNameBySubEntry(subEntry[::-1]).strip()
                subEntry.clear()
            
            # set lại cluster bắt đầu để thực hiện đệ qui
            currentStartedCluster =  highWord * 0x100 + lowWord

            # xử lý trường hợp là folder
            if isFolder:
                # lấy được parent address và address hiện tại
                name = (name if name != '' else mainName + expandName)
                path = self.directory.add(self.startedRDEFCluster, currentStartedCluster, name)  
            # xử lý trường hợp là file    
            else:
                name = (name if name != '' else mainName + '.' + expandName)
                path = f'{self.directory.get(self.startedRDEFCluster)}\{name}'

            # nếu là file thì lấy content luôn, còn không phải là file thì gọi đệ qui
            if name.lower().endswith('.txt') and size > 0:        
                # lấy bảng SDET
                fileSDETCluster = self.getRDETTable(currentStartedCluster)
                # lấy bảng sdet dạng sector để duyệt
                fileSDETBuffer = getContentByCluster(self.file, currentStartedCluster - 2, len(fileSDETCluster), self.sc, self.startedDataPosition).decode('utf-8', errors='ignore')
                # đọc thông tin content
                if fileSDETBuffer.find('\x00') > 0:
                    fileSDETBuffer = fileSDETBuffer[:fileSDETBuffer.find('\x00')]
                content = fileSDETBuffer
            else:
                #trường hợp các .file không được hỗ trợ đọc
                try:
                    extension = document[f'.{expandName}']
                except KeyError:
                    extension = 'Not support'
                content = f'Application to open is: {extension}'

            # print(name, size, content, path, createAt, updateAt)

            subFolder = createItem(isFolder, (name, size, content, path, createAt, updateAt))

            # cần có parent address
            parentFolder = self.root.findByPath(self.directory.get(self.startedRDEFCluster))
            if parentFolder is not None:
                #thêm vào node cha
                parentFolder.add(subFolder)
            
            #gọi đệ qui khi là folder
            if isFolder:
                # gán tạm 
                temp = self.startedRDEFCluster
                # hoán đổi current start RDEF
                self.startedRDEFCluster = currentStartedCluster
                self.readDirectoryEntryTable()
                # gán lại biến ban đầu
                self.startedRDEFCluster = temp
            index = index + 32

    def generateTree(self):
        #self.readBootSector()
        self.readDirectoryEntryTable()
    def build(self):
        self.generateTree()
        console = Console(self.root)
        console.windowShell()