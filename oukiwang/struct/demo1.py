import struct  
  
str = struct.pack("=cccHic", "a","b","c",500,2000,"F")  
(s1,s2,s3,i1,i2,s4)=struct.unpack("=cccHic",str)
print s1,s2,s3,i1,i2,s4
print repr(str)
print 'len(str):', len(str)
