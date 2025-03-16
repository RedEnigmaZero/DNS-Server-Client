import socket
import time
import os

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
SERVER_ADDRESS = ("localhost", 5001)
TIMEOUT = 1

def create_packet(seq_id, data):
    return int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big') + data

def send_file(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        file_size = os.path.getsize(filename)  
        udp_socket.settimeout(TIMEOUT)
        transmission_start_time = None
        packet_delay = 0
        packets_sent = 0
        seq_id = 0

        with open(filename, "rb") as f:
            while True:
                # Read data in file in chunks of packet size minus sequence ID size (so that there is room for SEQ_ID in packet)
                data = f.read(PACKET_SIZE - SEQ_ID_SIZE)
                if not data:
                    break  # Breaks at end of file

                # Creates packet with
                packet = create_packet(seq_id, data)
                packet_send_time = None

                while True:
                    # Sets transmission start time so that total transmission time can be calculated
                    if transmission_start_time is None:
                        transmission_start_time = time.time()
                    # Sets time packet is sent so that individual packet delay can be calculated
                    if packet_send_time is None:
                        packet_send_time = time.time()
                    # Sends packet to server address
                    udp_socket.sendto(packet, SERVER_ADDRESS)

                    try:
                        ack, _ = udp_socket.recvfrom(PACKET_SIZE)
                        ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], signed=True, byteorder='big')
                        if ack_id == seq_id + len(data):  # Correct ACK received
                            seq_id = ack_id
                            # Calculated packet_delay time from acknowledgement time and send time, resets send time
                            packet_ack_time = time.time()
                            packet_delay += (packet_ack_time - packet_send_time)
                            packets_sent += 1
                            packet_send_time = None
                            break
                    except socket.timeout:
                        print(f"Timeout for packet {seq_id}, retransmitting...")
                        
            # Get total transmission time
            transmission_end_time = time.time()
            total_transmission_time = transmission_end_time - transmission_start_time

            # Calculate all necessary output
            throughput = file_size / total_transmission_time if total_transmission_time > 0 else 0
            avg_packet_delay = (packet_delay / packets_sent) if packets_sent > 0 else 0
            performance_metric = .3 * (throughput / 1000) + .7 * avg_packet_delay

            # Print metrics
            print(f"Throughput: {round(throughput, 7)}\nAverage Packet Delay: {round(avg_packet_delay, 7)}\nMetric: {round(performance_metric, 7)}")  

        # Send termination signal
        udp_socket.sendto(create_packet(seq_id, b''), SERVER_ADDRESS)

        # Wait for receiver's FIN acknowledgment before sending FINACK
        try:
            fin_msg, _ = udp_socket.recvfrom(PACKET_SIZE)
            if b'fin' in fin_msg:
                udp_socket.sendto(b"==FINACK==", SERVER_ADDRESS)
        except socket.timeout:
            print("Timeout waiting for FIN message.")

if __name__ == "__main__":
    send_file("file.mp3")

"""
Instructions
-------------
● For each UDP sender, you will measure and report the throughput 
(size of transmitted data/time taken to send data) in the units of bytes per second and the
average per-packet delay in the units of seconds.

● To measure throughput, start your timer as soon as you create your socket and stop your timer once
you have received acknowledgments for all packets. You have to include sequence numbers in your packets
to keep track of acknowledgments.

● To measure the per-packet delay, you will start your timer when you send the packet and stop the timer
when you receive an acknowledgment from the receiver for that packet. In case of retransmissions, you should
consider the timer to start when you send the packet the first time and stop the timer when you finally receive
the acknowledgement.

● Should output throughput (in bytes per second), average packet delay (in seconds),
and the performance metric separated by a comma.

● All numbers should be reported as floating points, rounded up to 7 decimal points with no units.
"""
