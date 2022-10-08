def getBufferDataBySector(file, begin, sector, bts=512):
    file.seek(begin*bts)

    result = file.read(sector*bts)
    return result

def getBufferDataByOffset(buffer, begin, offset, bts=512):
    '''
        get sub buffer
    '''
    result = buffer[begin: begin+offset]
    return result

def getValueOfBufferByOffset(buffer, begin, offset, bts=512):
    '''
        get sub buffer in byte type
    '''
    subBuffer = getBufferDataByOffset(buffer, begin, offset, bts)
    result = int(subBuffer[::-1].hex(), 16)
    return result

def getContentByCluster(file, begin, clusters, sc, bts=512):
    listOfSector = []
    for cluster in range(begin, begin+clusters):
        for i in range(sc):
            sector = cluster*sc + i
            listOfSector.append(sector)
    
    content = b''
    for sector in listOfSector:
        content = content + getBufferDataBySector(file, sector, 1, bts)

    return content
