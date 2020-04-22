#!/usr/bin/python3
import sys

from lib_py3.redis_scoreboard import RedisScoreboard
from r1plot_lookup import lut

global_score_cache = None

def from_player(cmd,global_score_cache):
    if len(args) == 0:
        print("\nPlayer name expected after 'player'.")
        sys.exit()

    ign = args.pop(0)

    if global_score_cache is None:
        try:
            scoreboard = RedisScoreboard("play", redis_host="redis")
            global_score_cache = scoreboard.get_cache(Objective=['R1Plot','R1Address','plotx','ploty','plotz'])
        except:
            print("\nCould not load Plots' scoreboard file. Are you running this on build?")
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

def find_free(cmd, global_score_cache):
    print("\nFinding free plots...")

    known_plots = set()
    shore_tiles = [(0, -1), (0, 0), (0, 1)]
    for plot_x,plot_y,plot_z in lut.address_to_coord.values():
        for tile_x, tile_z in shore_tiles:
            x, y, z = plot_x, plot_y, plot_z
            x += 768 * tile_x
            z += 768 * tile_z
            known_plots.add((x, y, z))

    unused_plots = set(known_plots)

    if global_score_cache is None:
        try:
            scoreboard = Scoreboard('/home/epic/project_epic/plots/Project_Epic-plots/data/scoreboard.dat')
            global_score_cache = scoreboard.get_cache(Objective=['R1Plot','R1Address','plotx','ploty','plotz'])
        except:
            print("Could not load Plots' scoreboard file. Are you running this on build?")
            sys.exit()

    x_cache = scoreboard.get_cache(Objective='plotx', Cache=global_score_cache)
    y_cache = scoreboard.get_cache(Objective='ploty', Cache=global_score_cache)
    z_cache = scoreboard.get_cache(Objective='plotz', Cache=global_score_cache)

    for y_score in scoreboard.search_scores(Score={"min":1}, Cache=y_cache):
        ign = y_score.at_path('Name').value
        y = y_score.at_path('Score').value

        x = scoreboard.get_score(Name=ign, Objective='plotx', Cache=x_cache)
        z = scoreboard.get_score(Name=ign, Objective='plotz', Cache=z_cache)

        coords = (x, y, z)

        unused_plots.discard(coords)
        if coords not in known_plots:
            print("Bad player plot scores! Could accidentally '/tp {} {} {} {}'!".format(ign, x, y, z))

    print("There are {} plots in total, {} of which are unused:\n".format(len(known_plots), len(unused_plots)))
    for plot in sorted(unused_plots):
        print("  {} {} {}".format(plot[0], plot[1], plot[2]))

def from_invalid(cmd,global_score_cache):
    print("\nInvalid command {!r}. Please specify a 'player', 'plot', or 'address' - or 'free' for free plots.".format(cmd))
    sys.exit()

commands = {
    'player': from_player,
    'plot': from_plot,
    'address': from_address,
    'free': find_free,
}

print('''========================
Player Address Lookup
========================
In the event of conflict:
- plotx, ploty, plotz are the  coordinates just inside the plots.
  This is the only one that matters now.
- Failing that, if R1Address says it's wrong, it's probably wrong.
- R1Plot is usually trusted, but it's a pain to figure out where these are.
''')

args = sys.argv
args.pop(0)
if len(sys.argv) == 0:
    print("Please specify a 'player', 'plot', or 'address' - or 'free' for free plots.")
    sys.exit()

print("Getting addresses and coordinates...")

while len(args) >= 1:
    cmd = args.pop(0)
    commands.get(cmd,from_invalid)(cmd,global_score_cache)

