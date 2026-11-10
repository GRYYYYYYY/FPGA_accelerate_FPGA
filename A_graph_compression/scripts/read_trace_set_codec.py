"""Independent canonical lossless sorted-u64 run decoder."""
from read_search_trace import require,U64

def rle_byte_count(keys):
    total=0;previous=0;i=0
    while i<len(keys):
        first=i;start=keys[i];i+=1
        while i<len(keys) and keys[i]==keys[i-1]+1:i+=1
        gap=start-previous if first else start
        total+=max(1,(gap.bit_length()+6)//7)+max(1,((i-first).bit_length()+6)//7)
        previous=keys[i-1]
    return total

def decode(words,encoding,byte_count,count,maximum=1100754):
    require(0<=count<=maximum and encoding in [0,1] and byte_count>=0 and len(words)==(byte_count+7)//8,'Invalid set header')
    require(all(isinstance(w,int) and 0<=w<=U64 for w in words),'Invalid payload words')
    if byte_count%8:require(words[-1]>>(8*(byte_count%8))==0,'Nonzero set padding')
    if encoding==0:
        require(byte_count==8*count and all(a<b for a,b in zip(words,words[1:])) and rle_byte_count(words)>=byte_count,'Invalid/noncanonical raw set');return words.copy()
    raw=b''.join(w.to_bytes(8,'little') for w in words)[:byte_count];at=0;keys=[]
    def leb():
        nonlocal at
        value=0
        for lane in range(10):
            require(at<len(raw),'Truncated varint');b=raw[at];at+=1
            require(lane<9 or b<=1,'Overflow varint');value|=(b&127)<<(7*lane)
            if b<128:
                require(lane==0 or b!=0,'Nonminimal varint');return value
        raise ValueError('Unterminated varint')
    while at<len(raw):
        gap=leb();length=leb()
        require(length>0 and length<=count-len(keys) and (not keys or gap>=2),'Invalid/nonmaximal run')
        start=keys[-1]+gap if keys else gap;end=start+length-1
        require(end<=U64,'Run overflow');keys.extend(range(start,end+1))
    require(len(keys)==count and byte_count<8*count,'Noncanonical RLE/count')
    return keys
