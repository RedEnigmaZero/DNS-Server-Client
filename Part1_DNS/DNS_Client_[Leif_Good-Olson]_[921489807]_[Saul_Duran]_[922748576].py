import socket
import struct
import random
import time

class DNSClient:
    def __init__(self, server="8.8.8.8", port=53):
        self.server = server
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5)  # 5 second timeout

    def create_dns_header(self):
        ID = random.randint(0, 65535)
        flags = 0x0100  # Standard query
        qdcount = 1    # One question
        ancount = 0    # No answers
        nscount = 0    # No authority records
        arcount = 0    # No additional records
        
        header = struct.pack('!HHHHHH', ID, flags, qdcount, ancount, nscount, arcount)
        return header

    def create_dns_question(self, domain_name):
        # Convert domain name to DNS format
        parts = domain_name.split('.')
        question = b''
        for part in parts:
            length = len(part)
            question += struct.pack('!B', length)
            question += part.encode()
        question += b'\x00'  # End with null byte
        
        qtype = 1   # A record
        qclass = 1  # IN class
        question += struct.pack('!HH', qtype, qclass)
        return question

    def send_query(self, domain_name):
        # Create DNS query
        header = self.create_dns_header()
        question = self.create_dns_question(domain_name)
        query = header + question

        start_time = time.time()
        try:
            # Send query
            self.socket.sendto(query, (self.server, self.port))
            
            # Receive response
            response, _ = self.socket.recvfrom(512)
            end_time = time.time()
            
            # Parse response
            answers = self.parse_response(response)
            rtt = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return answers, rtt
            
        except socket.timeout:
            return None, None

    def parse_response(self, response):
        # Parse DNS header
        header = struct.unpack('!HHHHHH', response[:12])
        ancount = header[3]  # Number of answers
        
        # Skip header and question section
        offset = 12
        # Skip question name
        while response[offset] != 0:
            offset += 1
        offset += 5  # Skip null byte, qtype, and qclass
        
        # Parse answers
        answers = []
        for _ in range(ancount):
            # Handle compression
            if (response[offset] & 0xC0) == 0xC0:
                offset += 2
            else:
                while response[offset] != 0:
                    offset += 1
                offset += 1
            
            # Get answer type, class, TTL, and data length
            ans_type, ans_class, ttl, rdlength = struct.unpack('!HHIH', response[offset:offset+10])
            offset += 10
            
            # Get IP address if it's an A record
            if ans_type == 1:  # A record
                ip = '.'.join(str(x) for x in response[offset:offset+rdlength])
                answers.append(ip)
            
            offset += rdlength
            
        return answers

def main():
    client = DNSClient()
    domains = [
        "google.com",
        "facebook.com",
        "youtube.com",
        "baidu.com",
        "wikipedia.org"
    ]
    
    print("Domain Name\tIP Addresses\tRTT (ms)")
    print("-" * 50)
    
    for domain in domains:
        answers, rtt = client.send_query(domain)
        if answers:
            print(f"{domain}\t{', '.join(answers)}\t{rtt:.2f}")
        else:
            print(f"{domain}\tTimeout\tN/A")

if __name__ == "__main__":
    main()