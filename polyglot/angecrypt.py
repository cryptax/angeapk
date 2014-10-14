#AngeCryption: getting valid files after encryption

#takes any file as input, and a standard PDF/PNG/JPG as target
#will create a result_file that is source_file with appended 'garbage'
#and once ENcrypted with the chosen algorithm with the supplied script, it will show target_file

#any block cipher is supported as long as the block size matches the target type's header

#Ange Albertini 2014, BSD Licence - with the help of Jean-Philippe Aumasson

# - Added FLV support

import struct
import sys
import binascii

PNGSIG = '\x89PNG\r\n\x1a\n'
JPGSIG = "\xff\xd8"
FLVSIG = "FLV"

source_file, target_file, result_file, encryption_key, algo = sys.argv[1:6]

if algo.lower() == "aes":
    from Crypto.Cipher import AES
    algo = AES
    BS = 16
else:
    from Crypto.Cipher import DES3 # will work only with JPEG as others require 16 bytes block size
    algo = DES3
    BS = 8

pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) # non-standard padding might be preferred for PDF

#from Crypto import Random
#key = Random.new().read(16)
key = encryption_key

with open(source_file, "rb") as f:
    s = pad(f.read())

with open(target_file, "rb") as f:
    t = pad(f.read())

p = s[:BS] # our first plaintext block
ecb_dec = algo.new(key, algo.MODE_ECB)

# we need to generate our first cipher block, depending on the target type

if t.startswith(PNGSIG): #PNG
    assert BS >= 16
    size = len(s) - BS

    # our dummy chunk type
    # 4 letters, first letter should be lowercase to be ignored
    chunktype = 'aaaa'

    # PNG signature, chunk size, our dummy chunk type
    c = PNGSIG + struct.pack(">I",size) + chunktype

    c = ecb_dec.decrypt(c)
    IV = "".join([chr(ord(c[i]) ^ ord(p[i])) for i in range(BS)])
    cbc_enc = algo.new(key, algo.MODE_CBC, IV)
    result = cbc_enc.encrypt(s)

    #write the CRC of the remaining of s at the end of our dummy block
    result = result + struct.pack(">I", binascii.crc32(result[12:]) % 0x100000000)
    #and append the actual data of t, skipping the sig
    result = result + t[8:]

elif t.startswith(JPGSIG): #JPG
    assert BS >= 2

    size = len(s) - BS # we could make this shorter, but then could require padding again

    # JPEG Start of Image, COMment segment marker, segment size, padding
    c = JPGSIG + "\xFF\xFE" + struct.pack(">H",size) + "\0" * 10

    c = ecb_dec.decrypt(c)
    IV = "".join([chr(ord(c[i]) ^ ord(p[i])) for i in range(BS)])
    cbc_enc = algo.new(key, algo.MODE_CBC, IV)
    result = cbc_enc.encrypt(s)

    #and append the actual data of t, skipping the sig
    result = result + t[2:]
elif t.startswith(FLVSIG):
    assert BS >= 9
    size = len(s) - BS # we could make this shorter, but then could require padding again

    # reusing FLV's sig and type, data offset, padding
    c = t[:5] + struct.pack(">I",size + 16) + "\0" * 7

    c = ecb_dec.decrypt(c)
    IV = "".join([chr(ord(c[i]) ^ ord(p[i])) for i in range(BS)])
    cbc_enc = algo.new(key, algo.MODE_CBC, IV)
    result = cbc_enc.encrypt(s)

    #and append the actual data of t, skipping the sig
    result = result + t[9:]
elif t.find("%PDF-") > -1:
    assert BS >= 16
    size = len(s) - BS # we take the whole first 16 bits

    #truncated signature, dummy stream object start
    c = "%PDF-\0obj\nstream"

    c = ecb_dec.decrypt(c)
    IV = "".join([chr(ord(c[i]) ^ ord(p[i])) for i in range(BS)])
    cbc_enc = algo.new(key, algo.MODE_CBC, IV)
    result = cbc_enc.encrypt(s)

    #close the dummy object and append the whole t
    #(we don't know where the sig is, we can't skip anything)
    result = result + "\nendstream\nendobj\n" + t

else:
    print "file type not supported"
    sys.exit()


#we have our result, key and IV

#generate the result file
cbc_dec = algo.new(key, algo.MODE_CBC, IV)
with open(result_file, "wb") as f:
    f.write(cbc_dec.decrypt(pad(result)))

#generate the script
print """from Crypto.Cipher import %(algo)s

algo = %(algo)s.new(%(key)s, %(algo)s.MODE_CBC, %(IV)s)

with open(%(source)s, "rb") as f:
	d = f.read()

d = algo.encrypt(d)

with open("dec-" + %(target)s, "wb") as f:
	f.write(d)""" % {
        'algo': algo.__name__.split(".")[-1],
        'key':`key`,
        'IV':`IV`,
        'source':`result_file`,
        'target':`target_file`}
