import argparse

def input_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--Download', help='If you want to download the Ranked Battle data, set it to True.', type=str, required=False)
    args = parser.parse_args()
    arguments = vars(args)
    return arguments