#!/usr/bin/python3
import sys

args = sys.argv
args.pop(0)
if len(sys.argv) == 0:
    print("Please specify at least one R1Plot score.")

StreetNames={
    0:{
        0:"Axtan Avenue",
        1:"Narsen Blvd",
        2:"Cypresswood Drive",
        3:"Swiftwood Lane",
        4:"King's Court",
        5:"Verdant Street",
        6:"Farland Drive",
        7:"Tlaxan Trail",
        8:"Soulvenom Trail",
        9:"Highlands Avenue",
       10:"Plagueroot St",
    },
}

while len(args) > 0:
    R1Addr=int(args.pop(0))
    addr=R1Addr

    StreetNum = addr & 0x7f
    addr >>= 7
    StreetId = addr & 0x1f
    addr >>= 5
    TileZ = addr & 0xff
    addr >>= 8
    TileX = addr & 0xff

    if TileX > 127:
        TileX -= 256
    if TileZ > 127:
        TileZ -= 256

    StreetName = StreetNames.get(TileX,{}).get(StreetId,"Unknown Street")

    fullAddress = "{:9}: {} {}, Section {},{}".format(
        R1Addr,
        StreetNum,
        StreetName,
        TileX,
        TileZ
    )

    print(fullAddress)
    if StreetName == "Unknown Street":
        print('')
        print('0b{1}{0:028b}{2}: {0:9d}: R1Addr'.format(R1Addr,'',''))
        print('0b{1}{3:08b}{2}: {0:9d}: TileX'.format(TileX,'',' '*20,TileX%256))
        print('0b{1}{3:08b}{2}: {0:9d}: TileZ'.format(TileZ,' '*8,' '*12,TileZ%256))
        print('0b{1}{0:05b}{2}: {0:9d}: StreetId'.format(StreetId,' '*16,' '*7))
        print('0b{1}{0:07b}{2}: {0:9d}: StreetNum'.format(StreetNum,' '*21,''))

