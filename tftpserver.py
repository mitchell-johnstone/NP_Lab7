"""
- CS2911 - 0NN
- Fall 2020
- Lab 7
- Names:
  - Mitchell Johnstone
  - Jonathan Keane
  - Kayla Yakimisky

A Trivial File Transfer Protocol Server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

# import modules -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket
import os
import math

# Helpful constants used by TFTP
TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


def main():
    """
    Processes a single TFTP request
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    file_name = ''
    s = socket_setup()





    ####################################################
    # Your code ends here                              #
    ####################################################

    client_socket.close()

def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: The name of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        #   This function throws an exception if the file doesn't exist
        file_size = os.stat(filename).st_size
        return math.ceil(file_size / TFTP_BLOCK_SIZE)
    except:
        return -1


def get_file_block(filename, block_number):
    """
    Get the file block data for the given file and block number
    :param filename: The name of the file to read
    :param block_number: The block number (1 based)
    :return: The data contents (as a bytes object) of the file block
    """
    file = open(filename, 'rb')
    block_byte_offset = (block_number-1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    block_data = file.read(TFTP_BLOCK_SIZE)
    file.close()
    return block_data


def put_file_block(filename, block_data, block_number):
    """
    Writes a block of data to the given file
    :param filename: The name of the file to save the block to
    :param block_data: The bytes object containing the block data
    :param block_number: The block number (1 based)
    :return: Nothing
    """
    file = open(filename, 'wb')
    block_byte_offset = (block_number-1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    file.write(block_data)
    file.close()


def socket_setup():
    """
    Sets up a UDP socket to listen on the TFTP port
    :return: The created socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', TFTP_PORT))
    return s


####################################################
# Write additional helper functions starting here  #
####################################################



def handle_client_message(message, file_name, data_socket):
    return


def handle_read(data_socket):
    return


def handle_write(data_socket):
    return


def handle_data(file_name, data_socket):
    return

def handle_ack(message, file_name):
    """
    Parses the acknowledgement into its opcode and block num. Gets the data block that needs to be sent next.
    If the final ack is received for the last data block, it returns and empty bytes string.
    :param message: the entire acknowledgement that was received
    :param file_name: the file name to use for getting the file block and block count
    :return: data block- opcode of 3 + the next block num + the next data block
    :authors: Kayla Yakimisky, Mitchell Johnstone
    """
    opcode = message[:2]
    block_num = message[2:]
    block_num_int = int.from_bytes(block_num, 'big')
    num_blocks = get_file_block_count(file_name)
    if block_num < num_blocks:
        block_num_int += 1
        next_block = get_file_block(file_name, block_num_int)
        block_num_out = block_num_int.to_bytes(2, 'big')
        return b'\x00\x03' + block_num_out + next_block
    return b''


def handle_error(message):
    """
    Takes in an error message, parses it into its opcode, error code, and error message. Prints the error code and message before quitting.
    :param message: the entire error message received
    :return: void
    :authors: Kayla Yakimisky, Mitchell Johnstone
    """
    opcode = message[:2]
    err_code = message[2:4]
    err_msg = message[4:len(message) - 1]
    print('Error code: ', err_code)
    print('Error message: ', err_msg)
    quit()


def send_ack(byte):
    return


main()
