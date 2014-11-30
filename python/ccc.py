from collections import defaultdict
from heapq import heappush, heappop, heapify

def getInt(bytes):
    out = 0
    for b in bytes:
        out = out << 8
        out |= b
    return out

def getBytes(n, ln):
    out = []
    while ln > 0:
        ln -= 1
        out.append(int((n & (0xFF << ln * 8)) >> ln * 8))
    return out    

def load(path):
    dat = []
    f = open(path)
    for line in f:
        for str in line.strip().split(','):
            try:
                dat.append(int(str, 16))
            except:
                pass
    f.close()            
    return dat

def save(dat, path):
    f = open(path, 'w')
    n = 0
    for d in dat:
        f.write('0x{:02x}, '.format(d))
        n += 1
        if n == 8:
            f.write('\t')
        elif n > 15:
            f.write('\n')
            n = 0
    f.close()        

def huffmanList(dat):
    wt = defaultdict(int)
    for d in dat:
        wt[d] += 1
    heap = [[wt, [sym, 0]] for sym, wt in wt.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for ele in lo[1:] + hi[1:]:
            ele[1] += 1
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    lsmap = defaultdict(list)
    for ele in heappop(heap)[1:]:
        lsmap[ele[1]].append(ele[0])
    llist = []
    slist = []
    for ln in range(1, max(lsmap.keys()) + 1):
        llist.append(len(lsmap[ln]))
        slist += sorted(lsmap[ln])
    return llist, slist;

def huffmanSymbolMap(llist, slist):
    smap = {}
    slitr = iter(slist)
    cd = 0
    for i, n in enumerate(llist):
        ln = i + 1
        for m in range(n):
            smap[slitr.next()] = (ln, cd)
            cd += 1
        cd = cd << 1    
    return smap    

def huffmanCodeMap(llist, slist):
    cmap = defaultdict(dict)
    cd = 0
    slitr = iter(slist)
    for i, n in enumerate(llist):
        ln = i + 1
        for m in range(n):
            cmap[ln][cd] = slitr.next()
            cd += 1
        cd = cd << 1 
    return cmap

def huffmanEncode(smap, dat):
    hln = 0
    hlist = []
    ln = 0
    bits = 0
    for d in dat:
        ln += smap[d][0]
        bits = bits << smap[d][0]
        bits = bits | smap[d][1]
        while ln >= 8:
            hlist.append(bits >> ln - 8)
            hln += 8
            bits = bits & (1 << ln - 8) - 1
            ln -= 8
    if ln > 0:
        hlist.append(bits << 8 - ln)
        hln += ln        
    return hln, hlist

def huffmanDecode(cmap, llist, hln, hlist):
    out = []
    hp = 0
    cln = 1
    cd = 0
    ln = 0
    bits = 0
    hlitr = iter(hlist)
    while hp < hln:
        for i, n in enumerate(llist):
            cln = i + 1
            if n <= 0:
                continue
            if cln > ln:
                bits = bits << 8
                ln += 8
                try:
                    bits = bits | hlitr.next()
                except:
                    print 'No more data !!! \tln =', ln, 'cln =', cln
                    if ln <= 0:
                        return 
            cd = bits >> ln - cln
            try:
                out.append(cmap[cln][cd])
                hp += cln
                bits =  bits & (1 << ln - cln) -1
                ln -= cln
                break
            except:
                pass
    return out

def huffmanPack(dln, hln, llist, slist, hlist):
    out = []
     
    out += list(bytearray('HUFFMAN!HUFFMAN!'))

    out += getBytes(dln, 8)

    out += getBytes(hln, 8)

    out.append(len(llist))
    out += llist

    out.append(len(slist))
    out += slist

    out += hlist

    return out

def huffmanUnpack(dat):
    p = 0

    mgc = ''
    for d in dat[p : p + 16]:
        mgc += chr(d)
    p += 16

    dln = getInt(dat[p : p + 8])
    p += 8

    hln = getInt(dat[p : p + 8])
    p += 8

    llist = dat[p + 1 : p + 1 + dat[p]]
    p += 1 + dat[p]

    slist = dat[p + 1 : p + 1 + dat[p]]
    p += 1 + dat[p]

    hlist = dat[p:]

    return mgc, dln, hln, llist, slist, hlist         

def encodeHuffman(dat):
    llist, slist = huffmanList(dat)
    smap = huffmanSymbolMap(llist, slist)
    hln, hlist = huffmanEncode(smap, dat)
    out = huffmanPack(len(dat), hln, llist, slist, hlist)

    print 'Raw =', len(dat), '\tHuffman =', len(hlist), '\tOut =', len(out)
    print '\t\t', float(len(hlist)) / len(dat), '\t\t', float(len(out)) / len(dat)
    print 'hln =', hln

    return out

def decodeHuffman(dat):
    mgc, dln, hln, llist, slist, hlist = huffmanUnpack(dat)
    cmap = huffmanCodeMap(llist, slist)
    out = huffmanDecode(cmap, llist, hln, hlist)
    return out

def runLengthEncode(dat):
    rlist = [dat[0], 0]
    for d in dat[1:]:
        if rlist[-2] == d:
            if rlist[-1] == 0xFF:
                rlist += [d, 0]
            else:    
                rlist[-1] += 1
        else:
            rlist += [d, 0]
    return rlist

def runLengthDecode(rlist):
    out = []
    rlitr = iter(rlist)
    while True:
        try:
            out += [rlitr.next()] * (rlitr.next() + 1)
        except:
            break    
    return out

def runLengthPack(dln, rlist):
    out = []
     
    out += list(bytearray('RUN_RUN_LENGTH!!'))

    out += getBytes(dln, 8)

    out += getBytes(len(rlist), 8)

    out += rlist

    return out

def runLengthUnpack(dat):
    p = 0

    mgc = ''
    for d in dat[p : p + 16]:
        mgc += chr(d)
    p += 16

    dln = getInt(dat[p : p + 8])
    p += 8

    rln = getInt(dat[p : p + 8])
    p += 8

    rlist = dat[p:]

    return mgc, dln, rln, rlist         

def encodeRunLength(dat):
    rlist = runLengthEncode(dat)
    out = runLengthPack(len(dat), rlist)

    print 'Raw =', len(dat), '\tRunLength =', len(rlist), '\tOut =', len(out)
    print '\t\t', float(len(rlist)) / len(dat), '\t\t', float(len(out)) / len(dat)

    return out

def decodeRunLength(dat):
    mgc, dln, rln, rlist = runLengthUnpack(dat)
    out = runLengthDecode(rlist)

    return out

# -------------------------------------------------------------------------------

f = 'src.h'
enDat = load(f)
'''
txt = 'FFOOORRRRGGGGEEEEETTTTTTT'
txt = 'FFOOORRRRGGGGEEEEETTTTTTTABABABADDDDDDDBBBBBBBB'

# txt = 'FFOOO'
enDat =[]
enWt = defaultdict(int)
for ch in txt:
    enDat.append(ord(ch))
    enWt[ch] += 1
'''

enOut = encodeRunLength(enDat)
save(enOut, 'rl.h')
deDat = load('rl.h')
deOut = decodeRunLength(enOut)
print 'cmp(enDat, deOut) =', cmp(enDat, deOut), '\n'

enOut = encodeHuffman(enDat)
save(enOut, 'huff.h')
deDat = load('huff.h')
deOut = decodeHuffman(enOut)
print 'cmp(enDat, deOut) =', cmp(enDat, deOut), '\n'

enOut = encodeHuffman(encodeRunLength(enDat))
save(enOut, 'rl_huff.h')
deDat = load('rl_huff.h')
deOut = decodeRunLength(decodeHuffman(deDat))
print 'cmp(enDat, deOut) =', cmp(enDat, deOut), '\n'

