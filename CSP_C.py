# Author: Jieying Lin
import sys

# This class will store the infomation for each unassigned position
class PointInfo:
    def __init__(self, domains):
        self.domains = domains
        self.dependencyList = []

def mainF(filePath):
    Sudo = []
    emptyIndexs = []
    UnassignIndexs = [[]]
    emptyIndexsDomain = []
    dependencyDictionary = {}
    # since we want to use the value in inner function, we make it a list
    UnassignIndexs = [[]]
    NumTryNode = [0]

    f = open(filePath, "r")
    lines = f.readlines()
    for i in range(0, 9):
        row = []
        j = 0
        for num in lines[i].split():
            row.append(int(num))
            if int(num) == 0:
                # store all empty indexs
                emptyIndexs.append((i, j))
                # conbine empty indexs with heuristics
                # index, minimun remaining value, most constraining variable
                UnassignIndexs[0].append(((i, j), 0, 0))
            j += 1
        Sudo.append(row)
    f.close()

    # precheck the domain given
    for emptyIndex in emptyIndexs:
        row = emptyIndex[0]
        column = emptyIndex[1]
        rowStart = 0
        rowEnd = 0
        columnStart = 0
        columnEnd = 0
        # check row
        possibleDomain = []
        for possibleVal in range(1, 10):
            isFind = True
            if possibleVal in Sudo[row]: continue
            # check column
            for rowIndex in range(0,9):
                if Sudo[rowIndex][column] == possibleVal:
                    isFind = False
                    break
            if row <= 2:
                rowStart = 0
                rowEnd = 2
            elif row >= 6:
                rowStart = 6
                rowEnd = 8
            else:
                rowStart = 3
                rowEnd = 5

            if column <= 2:
                columnStart = 0
                columnEnd = 2
            elif column >= 6:
                columnStart = 6
                columnEnd = 8
            else:
                columnStart = 3
                columnEnd = 5
            for i in range(rowStart, rowEnd+1):
                for j in range(columnStart, columnEnd+1):
                    if Sudo[i][j] == possibleVal: 
                        isFind = False
                        break
                if not isFind: 
                    break
            if isFind: possibleDomain.append(possibleVal)
        # create a PointInfo for this point
        I = PointInfo(possibleDomain)
        # conbine the index with their information and add it to dictionary
        dependencyDictionary[emptyIndex] = I

    # create the dependency dictionary, only create once
    # for each of two indexs, check whether they are depend on each other
    def IsDepend(assignRow, assignCol, checkRow, checkColumn):
        if (assignRow == checkRow) or (assignCol == checkColumn): return True
        isSameBlockRow = False
        isSameBlockCol = False
        if (assignRow <= 2 and checkRow <= 2)\
            or (assignRow >= 6 and checkRow >= 6)\
            or (assignRow >= 3 and assignRow <= 5 and checkRow >= 3 and checkRow <= 5):
            isSameBlockRow = True
        if (assignCol <= 2 and checkColumn <= 2)\
            or (assignCol >= 6 and checkColumn >= 6)\
            or (assignCol >= 3 and assignCol <= 5 and checkColumn >= 3 and checkColumn <= 5):
            isSameBlockCol = True
        return isSameBlockRow and isSameBlockCol

    for firstIndex in range(0, len(emptyIndexs)-1):
        for secondIndex in range(1, len(emptyIndexs)):
            # if they are depend on each other, add them to each other's dictionary
            if IsDepend(emptyIndexs[firstIndex][0], emptyIndexs[firstIndex][1], emptyIndexs[secondIndex][0], emptyIndexs[secondIndex][1]):
                dependencyDictionary[emptyIndexs[firstIndex]].dependencyList.append(emptyIndexs[secondIndex])
                dependencyDictionary[emptyIndexs[secondIndex]].dependencyList.append(emptyIndexs[firstIndex])

    def RefreshHer():
        # refresh minimun remaining value and most constraining variable
        newUnsignIndexs = []
        for index in UnassignIndexs[0]:
            info = dependencyDictionary[index[0]]
            deList = info.dependencyList
            # update minimun remaining value
            NumofDe = 0
            for dependEle in deList:
                if dependEle in emptyIndexs:
                    NumofDe += 1
            # index, minimun remaining value, most constraining variable
            newUnsignIndexs.append((index[0], len(info.domains), NumofDe))
        UnassignIndexs[0] = newUnsignIndexs
        # sort the tie breaker first
        UnassignIndexs[0].sort(key=lambda x: x[2], reverse = True)
        # sort according to minimun remaining value
        UnassignIndexs[0].sort(key=lambda x: x[1])

    def SortDomainVal(point):
        info = dependencyDictionary[point]
        # get all the domain val
        domainList = info.domains
        depenList = info.dependencyList
        # store the frquency of each number shows up in dependency list
        frequency = [0] * 10
        if len(domainList) == 1:
            return domainList
        for pointVal in depenList:
            # find the domain of pointVal
            if pointVal in emptyIndexs:
                depenInfoDomain = dependencyDictionary[pointVal].domains
                for do in depenInfoDomain:
                    frequency[do] += 1
        tempList = []
        for do in domainList:
            tempList.append((do, frequency[do]))
        # move least constraining value to the front
        tempList.sort(key=lambda x: x[1], reverse = True)
        # returnDo only contains domain numbers
        returnDo = []
        for temp in tempList:
            returnDo.append(temp[0])
        return returnDo

    # After assign a new val, check other's domain
    def ForwardChecking(curPoint, tryVal, removeValIndexInArray):
        info = dependencyDictionary[curPoint]
        depenList = info.dependencyList
        creatEmpty = False
        for pointVal in depenList:
            if pointVal in emptyIndexs:
                depenInfoDomain = dependencyDictionary[pointVal].domains
                if tryVal in depenInfoDomain:
                    depenInfoDomain.remove(tryVal)
                    # store all indexs been modified because of this assignment
                    removeValIndexInArray.append(pointVal)
                    if len(depenInfoDomain) == 0: creatEmpty = True
        return creatEmpty


    def recursive():
        if len(UnassignIndexs[0]) == 0: return True
        # sort the unassigned index
        RefreshHer()
        # pop the first
        herInfo = UnassignIndexs[0].pop(0)
        curPoint = herInfo[0]
        # update unassign value
        emptyIndexs.remove(curPoint)
        # sort the curDomain
        curDomain = SortDomainVal(curPoint)
        isAccept = False
        for tryVal in curDomain:
            NumTryNode[0] = NumTryNode[0] +  1
            # check is this operation create empty domain
            removeValIndexInArray = []
            creatEmpty = ForwardChecking(curPoint, tryVal, removeValIndexInArray)
            if creatEmpty:
                # restore
                for index in removeValIndexInArray:
                    dependencyDictionary[index].domains.append(tryVal)
            else:
                if recursive():
                    isAccept = True
                    Sudo[curPoint[0]][curPoint[1]] = tryVal
                    return True
                else:
                    # restore
                    for index in removeValIndexInArray:
                        dependencyDictionary[index].domains.append(tryVal)
        if not isAccept:
            UnassignIndexs[0].append(herInfo)
            emptyIndexs.append(curPoint)
            return False

    if not recursive():
        print("Program gives up since it need to take more than 10,000 steps")
    else:
        print("The final Sudo is:")
        for i in range(0, 9):
            print(Sudo[i])
        print("The number of Nodes assignment is " + str(NumTryNode[0]))

# call main function
mainF(sys.argv[1])
