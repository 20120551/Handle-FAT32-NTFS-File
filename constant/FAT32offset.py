# READ BOOT SECTOR
BS_FAT_TYPE = {'hex': 0x52, 'byte': 8}
BS_SECTOR_SIZE = {'hex': 0x0B, 'byte': 2}
BS_SECTOR_CLUSTER = {'hex': 0x0D, 'byte': 1}
BS_SECTOR_BOOT = {'hex': 0X0E, 'byte': 2}
BS_FAT= {'hex': 0x10, 'byte': 1}
BS_TOTAL_SECTOR = {'hex': 0x20, 'byte': 4}
BS_SECTOR_FAT = {'hex': 0x24, 'byte': 4}
BS_RDET_CLUSTER_STARTED = {'hex': 0x2C, 'byte': 4}

#MAIN ENTRY
ME_STATE = {'hex': 0xB, 'byte': 1}
ME_MAIN_NAME = {'hex': 0x0, 'byte': 8}
ME_EXPAND_NAME = {'hex': 0x8, 'byte': 3}
ME_CREATE_AT = {'hex': 0x10, 'byte': 2}
ME_UPDATE_AT = {'hex': 0x18, 'byte': 2}
ME_HIGH_WORD = {'hex': 0x14, 'byte': 2}
ME_LOW_WORD = {'hex': 0x1A, 'byte': 2}
ME_CONTENT_SIZE = {'hex': 0x1C, 'byte': 4}

#SUB ENTRY
MS_A = {'hex': 0x1, 'byte': 10}
MS_B = {'hex': 0xE, 'byte': 12}
MS_C = {'hex': 0x1C, 'byte': 4}