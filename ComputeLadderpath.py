# Written by Yu Liu 2021.12.11 (yu.ernest.liu@bnu.edu.cn)

import numpy as np
import queue
from collections import deque

# The class that stores the target blocks (or target system)
class STRING_BLOCKS(object):
    def __init__(self, blocks, IDs):
        self.blocks = blocks # the set of strings to deal with
        self.IDs = IDs # the corresponding IDs
    
    # For the certain cut scheme (cutsVec), try to find duplications
    def cut_find_dup(self, cutsVec):
        blocksNew, IDsStartNew = [], []
        iCutStart = 0
        for i, x in enumerate(self.blocks): # split cuts for different strings
            cutsNow = cutsVec[iCutStart : iCutStart+len(x)-1]
            IDsNow = self.IDs[i]
            if any(cutsNow): # if there are cuts
                idxToCut = np.where(cutsNow)[0] # get index of cuts
                idxBefore = 0
                for idx in idxToCut:
                    if idxBefore != idx: # if not a single letter, then record
                        blocksNew.append(x[idxBefore : idx+1])
                        IDsStartNew.append(IDsNow[idxBefore])
                    idxBefore = idx+1
                if idx != len(x)-2: # if not a single letter, then record
                    blocksNew.append(x[idx+1:])
                    IDsStartNew.append(IDsNow[idx+1])
            else: # no cut, then record the original
                blocksNew.append(x)
                IDsStartNew.append(IDsNow[0])
            iCutStart += len(x)-1
        # up to here, we get blocksNew & IDsStartNew

        IDsNew = []
        for ii, dupTry in enumerate(blocksNew):
            for jj in range(ii+1, len(blocksNew)):
                if dupTry == blocksNew[jj]:
                    i2d, j2d = 0, 0
                    IDsThis = self.IDs[i2d]
                    for k, IDstart in enumerate(IDsStartNew): # calculate IDs
                        while i2d < len(self.IDs):
                            if j2d >= len(IDsThis):
                                i2d += 1
                                IDsThis = self.IDs[i2d]
                                j2d = 0
                            if IDsThis[j2d] == IDstart:
                                IDsNew.append(IDsThis[ j2d : j2d+len(blocksNew[k]) ])
                                break
                            j2d += 1
                            if i2d == len(self.IDs) and j2d == len(IDsThis):
                                break
                    del IDsNew[ii]
                    del blocksNew[ii]
                    return blocksNew, IDsNew, dupTry, (IDsStartNew[ii], IDsStartNew[jj])
        return None
    
    def init_scheme(self):
        lenScheme = 0
        for block in self.blocks:
            lenScheme += len(block) - 1
        return np.array([0] * lenScheme, dtype=np.int8)


class STACK_LIST_ITEM(object):
    def __init__(self, blocks, IDs, dup, dup2IDstart):
        self.blocks = blocks # blocks to deal with
        self.IDs = IDs # corresponding IDs of each element of the blocks
        self.dup = dup # the found duplications in the blocks
        self.dup2IDstart = dup2IDstart # where the duplication begins


# ====== Associated functions ======
def cal3Index(stackitem):
    targetStrings = stackitem[0].blocks
    SizeIndex = 0
    for block in targetStrings:
        SizeIndex += len(block)
    OrderIndex = 0
    for x in stackitem[1:]:
        OrderIndex += (len(x.dup) - 1)
    LadderpathIndex = SizeIndex - OrderIndex
    return LadderpathIndex, OrderIndex, SizeIndex


# Sort the duplications, in order to compare if two ladderpaths are identical
def SortDups(stackitem): # stackitem is a sequence of operations
    sortedDups = []
    for item in stackitem[1:]:
        sortedDups.append(item.dup)
    sortedDups.sort(key=lambda y: (len(y), y))
    return sortedDups


# Check if a ladderpath has been recorded, if not then record
def unseen(sortedDups, ShortestLadderpathsInfo):
    # check if sortedDups is ever appeared or not
    for _, sortedDups0 in ShortestLadderpathsInfo:
        if sortedDups == sortedDups0:
            return False
    return True


# Check if IDi1 (or IDi2) is the father of IDj1 (or IDj2)
def embraced(IDi1, IDi2, IDj1, IDj2):
    for i in IDi1:
        for j in IDj1:
            if i == j:
                return True
    for i in IDi1:
        for j in IDj2:
            if i == j:
                return True
    for i in IDi2:
        for j in IDj1:
            if i == j:
                return True
    for i in IDi2:
        for j in IDj2:
            if i == j:
                return True
    return False


# Find the highest level among the ladderpath's daughters
def findHighestLevel(OneLadderpath, consistof):
    if len(consistof) == 0:
        return 0
    else:
        hLevel = 0 # record the highest level
        for i in consistof:
            if OneLadderpath[i][4] is None:
                return None
            else:
                if hLevel < OneLadderpath[i][4]:
                    hLevel = OneLadderpath[i][4]
        return hLevel


# Display ladderpaths
def displayLadderpath(OneShortestLadderpath, index3, blocks0):
    levelInfo = [None]
    for block, _, _, _, level in OneShortestLadderpath:
        while level >= len(levelInfo):
            levelInfo.append([])
        levelInfo[level].append(block)

    countLetters0 = {} # in the original blocks0, the number of each letter
    for block in blocks0:
        for x in block:
            if x in countLetters0:
                countLetters0[x] += 1
            else:
                countLetters0[x] = 1
    countLetters = {} # among all the ladderons, the number of each letter
    for onelevel in levelInfo[1:]:
        for ladderon in onelevel:
            for x in ladderon:
                if x in countLetters:
                    countLetters[x] += 1
                else:
                    countLetters[x] = 1

    pom = [] # partially ordered multiset representation of the ladderpath
    level0 = []
    for x0, n0 in countLetters0.items():
        if x0 in countLetters:
            level0.append( (x0, n0 - countLetters[x0]) )
        else:
            level0.append( (x0, n0) )
    level0.sort(key=lambda y: (y[1], y[0]))
    pom.append(level0)
    for onelevel in levelInfo[1:]:
        count = {}
        level = []
        for block in onelevel:
            if block in count:
                count[block] += 1
            else:
                count[block] = 1
        for key, val in count.items(): # change format
            level.append( (key, val) )
        level.sort(key=lambda y: (y[1], y[0]))
        pom.append(level)

    print('{ ', end='')
    for level in pom[:-1]:
        for ladderon, m in level[:-1]:
            if m == 1:
                print(ladderon, ', ', sep='', end='')
            else:
                print(ladderon, '(', m, '), ', sep='', end='')
        m = level[-1][1]
        if m == 1:
            print(level[-1][0], ' // ', sep='', end='')
        else:
            print(level[-1][0], '(', m, ') // ', sep='', end='')
    level = pom[-1]
    for ladderon, m in level[:-1]:
        if m == 1:
            print(ladderon, ', ', sep='', end='')
        else:
            print(ladderon, '(', m, '), ', sep='', end='')
    m = level[-1][1]
    if m == 1:
        print(level[-1][0], sep='', end='')
    else:
        print(level[-1][0], '(', m, ')', sep='', end='')
    print(' }', '.  LadderpathIndex=', index3[0], 
          ', OrderIndex=', index3[1], ', SizeIndex=', index3[2], sep='')


# ============== Main ===============
# -------------- INPUT --------------
# Only change this INPUT section, only uncomment one blocks0
# blocks0 is the "target block" (or "target system") in the paper
DisplayProcess = True

blocks0 = ['ABCBCEABC'] # Test1, length = 9

# blocks0 = ['ABCDBCDBCDCDEFEF']
# X, Ex1,2,3, section2, length = 16
# It may take ~10 minutes

# blocks0 = ['ABCDEFCFEDCBFDBA'] 
# W, section2.5, length = 16

# blocks0 = ['ABDEDBED', 'ABDEDBED', 'ABDED', 'ABDABD', 
#            'CAB', 'CAB', 'ED', 'ED', 'ED'] 
# Q, Ex4, section2.6, length = 39
# It is too long to handle, cannot finish in a reasonable time scale
# With pretreatment, simplify to the following:
# blocks0 = ['ABDZBZ', 'ABDZ', 'ABDABD', 'CAB', 'Z']
# Z stands for ED, length = 20
# It may take ~1 hour


# blocks0 = ['12345667890']        # Test2, length=11
# blocks0 = ['1232312']            # Test3, length=7
# blocks0 = ['12345111167890']     # Test4, length=14

# blocks0 = ['12123123412345']     # Test5, length=14, ~30s
# blocks0 = ['12312123451234']     # Test6, length=14, ~30s
# blocks0 = ['11211a1111abCAB']    # Test7, length=15, ~30s

# blocks0 = ['111111111111']       # Test8, length=12, ~50s
# blocks0 = ['GACUUGACAUGACCUC']   # Test9, length=16, ~2mins
# blocks0 = ['127961234123b4523A'] # Test10, length=18, ~15mins
# -----------------------------------


IDs0 = []
i = 0
for block in blocks0:
    IDs0.append( list(range(i,i+len(block))) )
    i += len(block)

ShortestLadderpathsInfo = []
minLadderpathIndex = np.inf
index3final = None
stack = deque()
stack.append( [STACK_LIST_ITEM(blocks0, IDs0, None, None)] )
while stack: # for each loop, deal with a operation sequence, until no duplication found
    if DisplayProcess:    
        print('.', sep='', end='')
    stackitem0 = stack.pop()
    blocksTodo = STRING_BLOCKS(stackitem0[-1].blocks, stackitem0[-1].IDs) # to deal with the last item
    
    scheme = blocksTodo.init_scheme()
    lenScheme = len(scheme)
    schemeTodo = queue.Queue() # the schemes to deal with
    for i in range(lenScheme): # initialize schemes
        scheme[i] = 1
        schemeTodo.put( scheme.copy() )
        scheme[i] = 0
        
    foundYesNo = False
    while not schemeTodo.empty(): # loop until go through every scheme
        scheme = schemeTodo.get()
        found = blocksTodo.cut_find_dup(scheme) # cut and find duplications
        if found is not None:
            if not foundYesNo:
                foundYesNo = True
            stack.append( stackitem0 + [STACK_LIST_ITEM(found[0], found[1], found[2], found[3])] )
        
        for ii, xx in enumerate(scheme): # get index of first 1
            if xx:
                first1id = ii
                break
        i = 0
        while i < first1id:
            scheme[i] = 1 # make the next new scheme
            schemeTodo.put( scheme.copy() )
            scheme[i] = 0
            i += 1
            
    if not foundYesNo: # collect stack (a sequence of opearations) information
        if DisplayProcess:    
            print('|', sep='', end='')
        index3 = cal3Index(stackitem0)
        if index3[0] < minLadderpathIndex:
            index3final = index3
            minLadderpathIndex = index3[0]
            ShortestLadderpathsInfo = [ (stackitem0, SortDups(stackitem0)) ]
        elif index3[0] == minLadderpathIndex:
            sortedDups = SortDups(stackitem0)
            if unseen(sortedDups, ShortestLadderpathsInfo):
                ShortestLadderpathsInfo.append( (stackitem0, sortedDups) )

# From the complete information of ShortestLadderpathsInfo, 
# compute the partial order information, etc
ShortestLadderpaths = []
for stackitem, _ in ShortestLadderpathsInfo:
    OneShortestLadderpath = [] 
    # record the information of each block: 0th element is the duplication (substring)
    # 1nd element is IDs of the first duplication; 2rd element is IDs of the second duplication 1
    # 3rd element records which elements it consists of
    # 4th element if which level this block belongs to
    # 5th element records the three indices
    
    for x in stackitem[1:]:
        # collect OneLadderpath's complete information
        OneShortestLadderpath.append([x.dup, tuple( range(x.dup2IDstart[0], x.dup2IDstart[0]+len(x.dup)) ),
                                      tuple( range(x.dup2IDstart[1], x.dup2IDstart[1]+len(x.dup)) ), 
                                      [], None] )
    for i, dupi in enumerate(OneShortestLadderpath): # find which consists of which
        for j, dupj in enumerate(OneShortestLadderpath):
            if len(dupi[1]) > len(dupj[1]):
                if embraced(dupi[1], dupi[2], dupj[1], dupj[2]):
                    dupi[3].append(j)
    ThereIsStillNone = True
    while ThereIsStillNone:
        ThereIsStillNone = False
        for i, dup in enumerate(OneShortestLadderpath): # calculate which level each block belongs to
            if dup[4] is None:
                ThereIsStillNone = True
                hLevel = findHighestLevel(OneShortestLadderpath, dup[3])
                if hLevel is not None:
                    dup[4] = hLevel+1
    ShortestLadderpaths.append(OneShortestLadderpath)

# display
print('')
for OneShortestLadderpath in ShortestLadderpaths:
    displayLadderpath(OneShortestLadderpath, index3final, blocks0)
