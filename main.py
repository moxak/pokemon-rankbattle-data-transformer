from module.load import *
from module.utility import *

if __name__ == "__main__":
    arguments = input_arg()
    Data_transformer(download=arguments['Download'])
