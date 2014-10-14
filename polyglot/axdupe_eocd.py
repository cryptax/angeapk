# duplicate & adjust the EoCD of a ZIP archive at the bottom of the file
# to increase compatibility in the case of big appended data

#Ange Albertini, BSD Licence 2014
#Axelle Apvrille, modif to use from command line

import struct
import sys

def GetExtraEoCD(data, delta):
    """returns the adjusted EoCD of a ZIP file"""
    #Locate the signature of End of Central Directory
    eocdoff = data.find("PK\5\6")

    #read the comment length to get the full EoCD length
    cmtlen = struct.unpack("<H", data[eocdoff + 5 * 4: eocdoff + 5 * 4 + 2])[0]

    #grab the EoCD data
    eocdlen = cmtlen + 5 * 4 + 2
    eocd = data[eocdoff: eocdoff + eocdlen + 1]

    #the relative offset of the EoCD to the CD needs to be read
    reloff = struct.unpack("<L", eocd[3 * 4: 3 * 4 + 4]) [0]

    #then adjusted
    reloff += DELTA + eocdlen # the previous EoCD is now irrelevant
    eocd = eocd[:3 * 4] + struct.pack("<L", reloff) + eocd[3 * 4 + 4:]

    return eocd

if __name__ == "__main__":
    fn = sys.argv[1]

    DELTA = 256 * 1024

    with open(fn, "rb") as f:
        d = f.read()

    with open("eocd2_" + fn, "wb") as f:
        f.write(d + "\0" * DELTA + GetExtraEoCD(d, DELTA))
