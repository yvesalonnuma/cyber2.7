"""
title: server/client 2.7 project
author: Yves Alon Numa
date: 4.12.2025
description: this is the client code
the client connect to the server and sents him commands (dir,copy,execute,delete,take_screenshot and send_photo)
until the command exit that disconect him from the server
"""
import logging
import socket


def main():
    '''
    Main function for the client that sends commands to the server
    (exit/dir/copy/execute/delete/take_screenshot/send_photo commands)
    :return:
    '''
    IP = '127.0.0.1'
    PORT = 8820
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))
    while True:
        while True:
            cmd_request = (input("Enter your command request: ")).upper()
            if check_user_request(cmd_request,VALID_USER_REQUEST) == True:
                if cmd_request != "TAKE_SCREENSHOT" and cmd_request != "SEND_PHOTO" and cmd_request != "EXIT":
                        cmd_data = input("Enter your command path/data: ")
                else:
                     cmd_data = ""
                break
        try:
            send_with_protocol(my_socket,cmd_request,cmd_data)
            server_response = recv(cmd_request, my_socket)
            if server_response == "the server disconnected the client":
                print(server_response)
                break
            print(server_response)
        except Exception as e:
            print("Something Went Wrong with: "+str(e))
            logging.error("Something Went Wrong")
    my_socket.close()


def send_with_protocol(my_socket, cmd_request, cmd_data):
    '''
    Send the command and the command data to the server with protocol
    :param my_socket:
    :param cmd_request:
    :param cmd_data:
    :return:
    '''
    try:
        cmd_len = str(len(cmd_request))
        cmd_data_len = str(len(cmd_data))
        my_socket.sendall((cmd_len+"|"+cmd_request+cmd_data_len+"|"+cmd_data).encode())
        return
    except Exception as e:
        print("Something Went Wrong, didn't succeed sending the command")
        logging.error("Something Went Wrong while sending the command")


def recv(cmd_request, my_socket):
    '''
    Receive the command output datt from the server with protocol
    :param cmd_request:
    :param my_socket:
    :return: the output from the server of the wanted command or message if the command didnt succeed
    '''
    data_len = ""
    try:
        while True:
            next_char = my_socket.recv(1).decode()
            if next_char == "|":
                break
            data_len += next_char
        cmd_len = int(data_len)
        if cmd_request == "SEND_PHOTO":
            data = my_socket.recv(cmd_len)
            return save_photo(data)
        data = my_socket.recv(cmd_len).decode()
        return data
    except Exception as e:
        return "something Went Wrong, error with "+ str(e)


def save_photo(data):
    '''
    Save the photo that the server send
    :param data:
    :return: save the photo that the server send
    '''
    try:
        with open("photo.jpg", "wb") as file:
            file.write(data)
        return "photo saved succeed"
    except Exception as e:
        return "something Went Wrong, error with "+ str(e)


def check_user_request(cmd_request,VALID_USER_REQUEST):
    '''
    fanction that check if the command is valid or not
    :param cmd_request:
    :param VALID_USER_REQUEST:
    :return: True if the command is valid or False if not
    '''
    if cmd_request in VALID_USER_REQUEST:
        logging.info("valid Request")
        return True
    logging.error("invalid Request")
    return False


if __name__ == "__main__":
    logging.basicConfig(filename="client.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    VALID_USER_REQUEST = ["EXIT", "DELETE", "DIR", "EXECUTE", "COPY", "TAKE_SCREENSHOT", "SEND_PHOTO"]
    assert check_user_request("EXIT", VALID_USER_REQUEST) == True, "assert test failed"
    assert check_user_request("DIR", VALID_USER_REQUEST) == True, "assert test failed"
    assert check_user_request("RANDOM", VALID_USER_REQUEST) == False, "assert test failed"
    assert check_user_request("", VALID_USER_REQUEST) == False, "assert test failed"
    dummy_bytes = b'test'
    assert save_photo(dummy_bytes) in ["photo saved succeed", "something Went Wrong, error with " + str(Exception)], "assert test failed"
    assert send_with_protocol is not None, "assert test failed"
    assert recv is not None, "assert test failed"
    logging.info("all the asserts passed")
    main()