#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <malloc.h>
#include "huff.h"
#include "rl.h"
#include "rl_huff.h"



#define MGC_LEN 16
#define NUM_LEN 8
#define HUFF_MGC "HUFFMAN!HUFFMAN!"
#define RLEN_MGC "RUN_RUN_LENGTH!!"

struct rawdata
{   
    uint8_t *dat;
    uint64_t len;
};

uint64_t getUint64_t(uint8_t *dat);
int decodeHuffman(uint8_t *dat, struct rawdata *out);
int decodeRunLength(uint8_t *dat, struct rawdata *out);
void printlist(uint8_t *dat, int ln);

int main(){
    printf("****************************************\n\n");

    struct rawdata raw;
    
    printf("decodeRunLength(rl_encode, &raw) = %d\n", decodeRunLength(rl_encode, &raw));
    printf("memcmp(raw.dat, rl_raw, raw.len) = %d\n", memcmp(raw.dat, rl_raw, raw.len));
    printf("sizeof(rl_encode) = %d\traw.len = %d\n\n", sizeof(rl_encode), raw.len);

    printf("decodeHuffman(huff_encode, &raw) = %d\n", decodeHuffman(huff_encode, &raw));
    printf("memcmp(raw.dat, huff_raw, raw.len) = %d\n", memcmp(raw.dat, huff_raw, raw.len));
    printf("sizeof(huff_encode) = %d\traw.len = %d\n\n", sizeof(huff_encode), raw.len);

    printf("decodeHuffman(rl_huff_encode, &raw) = %d\n", decodeHuffman(rl_huff_encode, &raw));
    printf("decodeRunLength(raw.dat, &raw) = %d\n", decodeRunLength(raw.dat, &raw));
    printf("memcmp(raw.dat, rl_huff_raw, raw.len) = %d\n", memcmp(raw.dat, rl_huff_raw, raw.len));
    printf("sizeof(rl_huff_encode) = %d\traw.len = %d\n\n", sizeof(rl_huff_encode), raw.len);

    return 0;
}

int decodeRunLength(uint8_t *dat, struct rawdata *out)
{
    uint64_t dln, rln;
    uint8_t *p, *rlist;

    p = dat;
    if(memcmp(p, RLEN_MGC, MGC_LEN) != 0)
    {
        printf("decodeRunLength Wrong magic number!!!\n");
        return 1;
    }
    p += MGC_LEN;

    dln = getUint64_t(p);
    p += NUM_LEN;
    rln = getUint64_t(p);
    p += NUM_LEN;

    uint8_t *olist, s;
    int ln;
    uint64_t n = 0;
    olist = malloc(dln);
    rlist = p;
    p = olist;
    while(n < rln)
    {
        s = *(rlist++);
        ln = *(rlist++);
        n += 2;
        while(ln-- >= 0)
        {
            *(p++) = s;
        }
    }

    out->dat = olist;
    out->len = dln;

    return 0;
}

int decodeHuffman(uint8_t *dat, struct rawdata *out){
    uint64_t dln, hln, hlnb;
    uint32_t i, j;
    uint8_t  *p, *hlist;

    p = dat;
    if(memcmp(p, HUFF_MGC, MGC_LEN) != 0)
    {
        printf("decodeHuffman Wrong magic number!!!\n");
        return 1;
    }
    p += MGC_LEN;

    dln = getUint64_t(p);
    p += NUM_LEN;
    hln = getUint64_t(p);
    p += NUM_LEN;
    hlnb = hln % 8 ? hln / 8 + 1 : hln / 8;

    uint8_t llist[*(p++) + 1];
    llist[0] = 0;
    memcpy(llist + 1, p, sizeof(llist) - 1);
    p += sizeof(llist) - 1;

    uint8_t slist[*(p++)];
    memcpy(slist, p, sizeof(slist));
    p += sizeof(slist);

    uint8_t lsumlist[sizeof(llist)], lcdlist[sizeof(llist)], cd = 0;
    memset(lsumlist, 0, sizeof(lsumlist));
    memset(lcdlist, 0, sizeof(lcdlist));
    for(i=1; i<sizeof(llist); i++)
    {
        for(j=i; j<sizeof(lsumlist); j++)
        {
            lsumlist[j] += llist[i];
        }
        lcdlist[i] = cd;
        cd += llist[i];
        cd = cd << 1;
    }

    hlist = p;

    uint8_t *olist, ln = 0, cln = 1, s;
    uint64_t bits = 0, n = 0;
    olist = malloc(dln);
    p = olist;
    while(n < hln)
    {
        if(cln > ln)
        {
            bits = bits << 8;
            bits = bits | *(hlist++);
            ln += 8;
        }
        cd = bits >> (ln - cln);
        if(cd - lcdlist[cln] + 1 <= llist[cln])
        {
            s = slist[lsumlist[cln -1] + cd - lcdlist[cln]];
            *(p++) = s;
            bits = bits & (1 << ln - cln) - 1;
            ln -= cln;
            n += cln;
            cln = 1;
        }
        else
        {
            cln++;
        }
    }

    out->dat = olist;
    out->len = dln;

    return 0;
}

uint64_t getUint64_t(uint8_t *dat)
{
    uint64_t out = 0;
    int i;
    for(i=0; i<8; i++)
    {
        out = out << 8;
        out = out | *(dat++);
    }
    return out;
}

void printlist(uint8_t *dat, int ln)
{
    int i;
    for(i=0; i<ln; i++)
    {
        printf("%d, ", *(dat++));
    }
    printf("\n");
}
