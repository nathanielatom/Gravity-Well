""" Contains all of the game's constant parameters. To see how they're used, see engine.py. To edit or create
new levels, see levels.py. Also see levels.py for the game description.
"""


class Settings():

    # window size when not fullscreen mode (edit levels.py to disable fullscreen mode)
    screen_size = (1074, 768)
    # max fps
    fps = 30
    # number of levels until end of game
    total_lvls = 9
    # constants used to determine text size and formatting
    text_size = 3e-5
    vel_info_x_gap = 35
    vel_info_y_down = 6
    vel_info_angle_width = 130
    replay_info_relative_pos = (18, 50)
    pause_reset_info_x = 30
    pause_info_y_up = 74
    observe_launch_info_x = 350
    observe_info_y_down = 50
    # user-interface clickable text colour
    widget_colour = (232, 192, 8)
    # number of past trajectories shown
    instant_replays = 5
    # colour and formatting for past trajectories
    replay_colours = (1.2, 1.3, 2.8)
    previous_attempts_info_pos = (32, 20)
    y_info_gap = 10
    # controls rate of change of angle/speed when using keyboard to modify
    angle_modifier = 1.0
    speed_modifier = 0.1
    # min and max launch speeds
    max_speed = 24.0
    min_speed = 12.0
    # used to determine if the hero body escapes earth's gravity well
    min_escape_speed = 4.0
    max_escape_well_time = 0.08
    # controls rate of change and limits for G when using keyboard to modify
    G_modifier = 0.5
    G_max = 8.0
    G_min = 0.5
    G_default = 3.0
    # constants used to determine how points are accumulated (score for displaying info-bits)
    percent_point_modifier = 0.075
    point_modifier = 1000
    point_max_increment_distance = 75
    # time in seconds hero is offcreen before the level is reset
    offscreen_reset_time = 8
    # determines crash/death screen
    crash_delay = 1200
    shade_of_death = 42
    colour_of_death = (236, 30, 20)
