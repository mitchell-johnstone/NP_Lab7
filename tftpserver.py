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
This lab focussed on the Trivial File Transfer Protocol (TFTP), a protocol used to transfer files over a network.
The transfer isn't secure, as the protocol only uses the bare-bones in order to transfer quickly the files, but it is
simple and straighforward.
This lab introduced the TFTP, and had us create a server for files. We were required to implement the GET command
for the protocol, with the PUT command as extra. This meant that we had to receive messages from the sender,
parse what the message is saying through helper methods, take the necessary actions, and formulate the correct
response to send back.


Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)
After reading through the RFC documentation for the TFTP, we split up the tasks, working simultaneously on the helper
methods along with the larger methods to handle the message. After some debugging with bytes literal complications, the
helper methods worked together well to both GET files and PUT files.
From this lab, we learned about how the tftp is used to send files, and why it isn't recommended for general files, only
trivial ones.
And we learned that the "client_address" received from the udp recvfrom method is actually a tuple.
And that b'\x00\x01' is not the same as 1.
Ooooo, and that the TFTP port is reserved as 69. Not super secure, but gotta say, NICE.
Also, we only used 1 loop, in the main method. It was fabulous.


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
    :author: Mitchell Johnstone
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    file_name, response_message, terminate = '', b'temp', False
    while response_message and not terminate:
        client_message, client_address = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)
        response_message, file_name, terminate = handle_client_message(client_message, file_name)
        client_socket.sendto(response_message, client_address)

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


def handle_client_message(message, file_name):
    """
    Takes in the message from the client and the file name. Calls the appropriate method to either read a request, handle an error, or read an acknowledgement.
    :param message: the message received from the client
    :param file_name: the name of the file from the client
    :return: the message, modified by the handle_ack or handle_read method, and the file name, which may be modified by the handle_read method.
    :author: Kayla Yakimisky
    """
    opcode = int.from_bytes(message[:2], 'big')
    message = message[2:]
    terminate = False
    if opcode == 1:
        terminate, file_name, message = handle_read(message)
    elif opcode == 2:
        terminate, file_name, message = handle_write(message)
    elif opcode == 3:
        terminate, message = handle_data(message, file_name)
    elif opcode == 4:
        terminate, message = handle_ack(message, file_name)
    elif opcode == 5:
        terminate, message = handle_error(message)
    else:
        print('An illegal TFT operation was requested.')
        terminate, message = True, b'\x00\x05\x00\x04Illegal TFTP operation\x00'
    return message, file_name, terminate


def handle_read(message):
    """
    Take a bytes object that does not contain the opcode and get 
    the file and the first block based of the file based on the 
    message's filename.
    :param message: the request  without an opcode as a bytes object
    :return: the filename read from and the next request line
    :author: Jonny Keane
    """
    file_name = message[:message.find(b'\x00')].decode()
    print('Received read request for file ', file_name)
    if os.path.isfile(file_name):
        print('Sending block 1')
        return False, file_name, b'\x00\x03\x00\x01' + get_file_block(file_name, 1)
    print('However, the file was not found')
    return True, file_name, b'\x00\x05\x00\x01File not found.\x00'


def handle_write(message):
    """
    Takes a bytes obect that does not contain opcode and get the file
    to write to and make the acknowledgement request for the first data
    block of the file.
    :param message: the request without an opcode as a bytes object
    :return: the filename to write to and the next request line
    :author: Jonny Keane
    """
    file_name = message[:message.find(b'\x00')].decode()
    print('Received write request for file ', file_name)
    if os.path.isfile(file_name):
        print('But the file already exists')
        return True, file_name, b'\x00\x05\x00\x06File already exists.\x00'
    return False, file_name, b'\x00\x04\x00\x00'


def handle_data(message, file_name):
    """
    Takes the filename and append the new bytes to the given file.
    Return the next request line and return if more requests are 
    follow.
    :param message: the request without an opcode as a bytes object
    :param file_name: the name of the file to put the data into
    :return: boolean saying whether there are more requests to come
             and the next request line (acknowledgement)
    :author: Jonny Keane
    """
    block_number = message[:2]
    block_data = message[2:]
    put_file_block(file_name, block_data, int.from_bytes(block_number,'big'))
    print('Received block ', block_number, ' for file ', file_name)
    return bool(len(block_data) != 512), b'\x00\x04' + block_number


def handle_ack(message, file_name):
    """
    Parses the acknowledgement into its opcode and block num. Gets the data block that needs to be sent next.
    If the final ack is received for the last data block, it returns and empty bytes string.
    :param message: the entire acknowledgement that was received
    :param file_name: the file name to use for getting the file block and block count
    :return: data block- opcode of 3 + the next block num + the next data block
    :authors: Kayla Yakimisky, Mitchell Johnstone
    """
    block_num_int = int.from_bytes(message, 'big')
    num_blocks = get_file_block_count(file_name)
    if block_num_int < num_blocks:
        block_num_int += 1
        next_block = get_file_block(file_name, block_num_int)
        block_num_out = block_num_int.to_bytes(2, 'big')
        print('Sent Block ', block_num_int, ' of file ', file_name)
        return False, b'\x00\x03' + block_num_out + next_block
    return True, b''


def handle_error(message):
    """
    Takes in an error message, parses it into its opcode, error code, and error message. Prints the error code and message before quitting.
    :param message: the entire error message received
    :return: True, indicating the program should terminate
    :authors: Kayla Yakimisky, Mitchell Johnstone
    """
    err_code = message[:2]
    err_msg = message[2:len(message) - 1]
    print('Error code: ', err_code)
    print('Error message: ', err_msg)
    return True, b''


main()
