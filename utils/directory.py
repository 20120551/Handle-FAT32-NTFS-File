class Directory: 
    def __init__(self, default):
        self.default = default
        self.listOfDirectory = {}

    def add(self, parentIndex, index, name)->None:
        try:
            result = self.listOfDirectory[str(parentIndex)]
        except KeyError:
            self.listOfDirectory[str(parentIndex)] = self.default

        if int(index) == parentIndex:
            return self.default

        self.listOfDirectory[str(int(index))] = f'{self.listOfDirectory[str(parentIndex)]}\{name}'

        result = self.listOfDirectory[str(int(index))]
        return result

    def get(self, parentIndex):
        try:
            result = self.listOfDirectory[str(parentIndex)]
        except KeyError:
            self.listOfDirectory[str(parentIndex)] = self.default

        result = self.listOfDirectory[str(parentIndex)]
        return result
