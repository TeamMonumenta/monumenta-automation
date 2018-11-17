#!/usr/bin/python3
import sys

from r1plot_lookup import lut

args = sys.argv
args.pop(0)
if len(sys.argv) == 0:
    print("Please specify at least one R1Plot score.")

while len(args) > 0:
    addr=int(args.pop(0))
    addr_details = lut.unpack_r1address(addr)

    tile_x = addr_details['tile_x']
    tile_z = addr_details['tile_z']
    street_id = addr_details['street_id']
    street_num = addr_details['street_num']

    full_address = "{:9}: {}".format(
        addr,
        addr_details['full_address']
    )

    print(fullAddress)
    if StreetName == "Unknown Street":
        print('')
        print('0b{1}{0:028b}{2}: {0:9d}: R1Addr'.format(addr,'',''))
        print('0b{1}{3:08b}{2}: {0:9d}: TileX'.format(tile_x,'',' '*20,tile_x & 0xff))
        print('0b{1}{3:08b}{2}: {0:9d}: TileZ'.format(tile_z,' '*8,' '*12,tile_z & 0xff))
        print('0b{1}{0:05b}{2}: {0:9d}: StreetId'.format(street_id,' '*16,' '*7))
        print('0b{1}{0:07b}{2}: {0:9d}: StreetNum'.format(street_num,' '*21,''))

