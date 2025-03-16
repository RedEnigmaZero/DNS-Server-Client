import socket
import struct
import random
import time
import http.client

class DNSClient:
    def __init__(self, server="8.8.8.8", port=53):
        self.server = server
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(10)  # 10 second timeout

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
        
        # Skip header
        offset = 12
        # Skip question name
        while response[offset] != 0:
            if (response[offset] & 0xC0) == 0xC0:
                offset += 2
            else:
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
            
            
            # Process different record types
            if ans_type == 1:  # A record
                ip = '.'.join(str(b) for b in response[offset:offset+rdlength])
                answers.append(('A', ip))
            elif ans_type == 2:  # NS record
                ns_name = self._extract_name(response, offset)
                answers.append(('NS', ns_name))
            elif ans_type == 5:  # CNAME record
                cname = self._extract_name(response, offset)
                answers.append(('CNAME', cname))
            elif ans_type == 15:  # MX record
                # Extract preference and MX name
                preference = struct.unpack('!H', response[offset:offset+2])[0]
                mx_name = self._extract_name(response, offset+2)
                answers.append(('MX', f"{preference} {mx_name}"))
            elif ans_type == 16:  # TXT record
                # Extract TXT data
                txt_len = response[offset]
                txt_data = response[offset+1:offset+1+txt_len].decode('utf-8', errors='ignore')
                answers.append(('TXT', txt_data))
            elif ans_type == 28:  # AAAA record
                ipv6 = ':'.join(f"{response[offset+i*2]*256+response[offset+i*2+1]:x}" for i in range(8))
                answers.append(('AAAA', ipv6))
            else:
                answers.append((f'TYPE{ans_type}', f'<data length: {rdlength}>'))
            
            offset += rdlength
            
        return answers
        
    def _extract_name(self, response, offset):
        name = ""
        # Check for compression
        if (response[offset] & 0xC0) == 0xC0:
            pointer = ((response[offset] & 0x3F) << 8) | response[offset + 1]
            name = self._extract_name(response, pointer)
            return name
        
        # Regular name extraction
        current_offset = offset
        while response[current_offset] != 0:
            if (response[current_offset] & 0xC0) == 0xC0:
                pointer = ((response[current_offset] & 0x3F) << 8) | response[current_offset + 1]
                name += self._extract_name(response, pointer)
                break
            else:
                length = response[current_offset]
                current_offset += 1
                name += response[current_offset:current_offset+length].decode('utf-8', errors='ignore') + '.'
                current_offset += length
        
        if name and name[-1] == '.':
            name = name[:-1]
        
        return name


def main():
    client = DNSClient()
    domains = [
        "www.google.com",
        "www.wikipedia.org"
    ]
    
    print("Domain Name\tRecord Type\tRecord Data\tRTT (ms)")
    print("-" * 70)
    
    for domain in domains:
        answers, rtt = client.send_query(domain)
        if answers:
            for record_type, record_data in answers:
                print(f"{domain}\t{record_type}\t{record_data}\t{rtt:.2f}")
            
            # HTTP Request 
            try:
                # Get the first A record IP address
                ip_address = None
                for record_type, record_data in answers:
                    if record_type == 'A':
                        ip_address = record_data
                        break
                
                if ip_address:
                    # Create a TCP socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    sock.connect((ip_address, 443))
                    
                    # Create an HTTP connection using the IP address
                    conn = http.client.HTTPConnection(ip_address)
                    
                    # Measure HTTP RTT
                    http_start_time = time.time()
                    
                    # Send the request with proper Host header
                    conn.request("GET", "/", headers={"Host": domain})
                    
                    # Get and print the response
                    response = conn.getresponse()
                    
                    # Calculate HTTP RTT
                    http_end_time = time.time()
                    http_rtt = (http_end_time - http_start_time) * 1000  # Convert to milliseconds
                    
                    print(f"HTTPS Response for {domain}: {response.status} {response.reason} {http_rtt:.2f} ms")
                    
                    # Close the connection
                    conn.close()
                else:
                    print(f"No A record found for {domain}, cannot make HTTPS request")
            except Exception as e:
                print(f"HTTPS Request Error for {domain}: {e}")
        else:
            print(f"{domain}\tN/A\tTimeout\tN/A")
            print(f"HTTPS Request for {domain}: Not attempted (DNS resolution failed)")


if __name__ == "__main__":
    main()