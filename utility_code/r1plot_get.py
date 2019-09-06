#!/usr/bin/python3
import sys

from lib_py3.scoreboard import Scoreboard
from r1plot_lookup import lut

global_score_cache = None

def from_player(cmd,global_score_cache):
    if len(args) == 0:
        print("\nPlayer name expected after 'player'.")
        sys.exit()

    ign = args.pop(0)

    if global_score_cache is None:
        try:
            scoreboard = Scoreboard('/home/epic/project_epic/plots/Project_Epic-plots/data/scoreboard.dat')
            global_score_cache = scoreboard.get_cache(Objective=['R1Plot','R1Address','plotx','ploty','plotz'])
        except:
            print("\nCould not load Region 1's scoreboard file. Remember to `~select play2`.")
            sys.exit()

    cache = scoreboard.get_cache(Name=ign,Objective=['R1Plot','R1Address','plotx','ploty','plotz'],Cache=global_score_cache)

    score_plot = scoreboard.get_score(ign,'R1Plot',Fallback=0,Cache=cache)
    score_addr = scoreboard.get_score(ign,'R1Address',Fallback=0,Cache=cache)
    score_x = scoreboard.get_score(ign,'plotx',Fallback=0,Cache=cache)
    score_y = scoreboard.get_score(ign,'ploty',Fallback=0,Cache=cache)
    score_z = scoreboard.get_score(ign,'plotz',Fallback=0,Cache=cache)


    ############################################################################
    # According to their plotx, ploty, plotz scores (latest version)
    by_xyz_coords = None
    valid_xyz = score_y != 0 and ( score_x != 0 or score_z != 0 )
    if valid_xyz:
        by_xyz_coords = (score_x,score_y,score_z)

        by_xyz_msg  = "- Judging by plotx,ploty,plotz:\n"
        by_xyz_msg += "  - Coordinates: {}".format( by_xyz_coords )
    else:
        by_xyz_msg = "- Player's plotx,ploty,plotz scores are not set"


    ############################################################################
    # According to their R1Address scor (somewhat trusted, somewhat helpful)
    by_addr_coords = None
    valid_addr = score_addr != 0
    if valid_addr:
        addr = score_addr
        addr_details = lut.unpack_r1address(addr)
        valid_addr = addr_details['valid']
        if valid_addr:
            by_addr_coords = lut.coordinates_from_r1address(addr)

            by_addr_msg  = "- According to player's R1Address score:\n"
            by_addr_msg += "  - Address: {}".format(addr_details['full_address'])
            by_addr_msg += "  - Coordinates: {}".format( by_addr_coords )
        else:
            by_addr_msg  = "- Player's R1Address score is not valid\n"
            by_addr_msg += "  - Address: {}".format(addr_details['full_address'])
            by_addr_msg += "  - Coordinates: Could not determine"
    else:
        by_addr_msg = "- Player's R1Address score is not set"


    ############################################################################
    # According to their R1Plot scor (oldest, most trusted, least helpful)
    by_plot_coords = None
    valid_plot = score_plot in lut.plot_to_address.keys()
    if valid_plot:
        plot = score_plot
        addr = lut.plot_to_address[plot]

        addr_details = lut.unpack_r1address(addr)
        valid_plot = addr_details['valid']
        if valid_plot:
            by_plot_coords = lut.coordinates_from_r1address(addr)

            by_plot_msg  = "- According to player's R1Plot score:\n"
            by_plot_msg += "  - R1Address: {}\n".format(addr)
            by_plot_msg += "  - Address: {}\n".format(addr_details['full_address'])
            by_plot_msg += "  - Coordinates: {}".format( by_plot_coords )
        else:
            by_plot_msg  = "- Player's R1Plot score is not valid\n"
            by_plot_msg += "  - R1Address: {}\n".format(addr)
            by_plot_msg += "  - Address: {}".format(addr_details['full_address'])
            by_plot_msg += "  - Coordinates: Could not determine"
    elif score_plot != 0:
        by_plot_msg = "- Player's R1Plot score is {}, but not on our very outdated, manually updated records. They should have a valid R1Address score, or plotx,ploty,plotz scores.".format( score_plot )
    else:
        by_plot_msg = "- Player's R1Plot score is not set"

    print('- For the player {}:'.format(ign))

    print(by_xyz_msg)
    print(by_addr_msg)
    print(by_plot_msg)

    if by_xyz_coords == by_addr_coords and by_addr_coords == by_plot_coords:
        print('- All interpreted coordinates agree.')
    elif by_xyz_coords == by_addr_coords:
        print('- plotx,ploty,plotz agrees with R1Address.')
    elif by_xyz_coords == by_plot_coords:
        print('- plotx,ploty,plotz agrees with R1Plot.')
    elif by_addr_coords == by_plot_coords:
        print('- R1Address agrees with R1Plot.')
    else:
        print('- None of these agree. Hopefully one of them determined some coordinates?')

def from_plot(cmd,global_score_cache):
    if len(args) == 0:
        print("\nR1Plot score expected after 'R1Plot'.")
        sys.exit()

    try:
        plot = int( args.pop(0) )
    except:
        print("\nPlot score expected after 'R1Plot'; could not interpret as an integer.")
        sys.exit()

    addr = lut.plot_to_address.get(plot,None)

    if addr is None:
        print("\nThat plot score is not on record. This player may have a plot, as the record of R1Plot scores has been out of date since it was manually created months ago. They should have a valid R1Address score, or plotx,ploty,plotz scores.")

    addr_details = lut.unpack_r1address(addr)

    full_address = addr_details['full_address']
    valid = addr_details['valid']

    print( "\nR1Plot score {}:".format( plot ) )
    print( "- R1Address score {}:".format( addr ) )
    print( "- Address: {}.".format( full_address ) )
    if not valid:
        print( "  - This address appears to be invalid." )
        try:
            coords = lut.coordinates_from_r1address(addr)
            print( "- Coordinates: {}.".format( coords ) )
        except:
            pass
    else:
        coords = lut.coordinates_from_r1address(addr)
        print( "- Coordinates: {}.".format( coords ) )

def from_address(cmd,global_score_cache):
    if len(args) == 0:
        print("\nR1Address score expected after 'R1Address'.")
        sys.exit()

    try:
        addr = int( args.pop(0) )
    except:
        print("\nR1Address score expected after 'R1Address'; could not interpret as an integer.")
        sys.exit()

    addr_details = lut.unpack_r1address(addr)

    full_address = addr_details['full_address']
    valid = addr_details['valid']

    coords = lut.coordinates_from_r1address(addr)

    print( "\nR1Address score {:9}:".format( addr ) )
    print( "- Address: {}.".format( full_address ) )
    if not valid:
        print( "  - This address appears to be invalid." )
        try:
            coords = lut.coordinates_from_r1address(addr)
            print( "- Coordinates: {}.".format( coords ) )
        except:
            pass
    else:
        coords = lut.coordinates_from_r1address(addr)
        print( "- Coordinates: {}.".format( coords ) )

def from_invalid(cmd,global_score_cache):
    print("\nInvalid command '{}'. Please specify a 'player', 'R1Plot', or 'R1Address'.".format(cmd))
    sys.exit()

commands = {
    'player': from_player,
    'R1Plot': from_plot,
    'R1Address': from_address,
}

print('''========================
Player Address Lookup
========================
In the event of conflict:
- If R1Address says it's wrong, it's probably wrong.
- plotx, ploty, plotz are the newest system, and I trust them if they work;
  should be the coordinates just inside the plots.
- R1Plot is usually trusted, but it's a pain to figure out where these are.
''')

args = sys.argv
args.pop(0)
if len(sys.argv) == 0:
    print("Please specify a 'player', 'R1Plot', or 'R1Address'.")
    sys.exit()

print("Getting addresses and coordinates...")

while len(args) >= 1:
    cmd = args.pop(0)
    commands.get(cmd,from_invalid)(cmd,global_score_cache)

