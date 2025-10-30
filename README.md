# DNS, Congestion Control, and BGP Analysis Project

This repository contains a multi-part project covering fundamental networking concepts. It includes implementations for a DNS client, various congestion control algorithms, and BGP route analysis.

## Authors

* **Saul Duran** 
* **Leif Good-Olson** 

---

## Part 1: DNS Client

This script implements a simple DNS client in Python. It manually constructs a DNS query packet, sends it to a specified DNS server (defaulting to Google's `8.8.8.8`), and parses the response.

### Features

* Creates standard DNS query headers and questions.
* Sends queries over UDP.
* Measures and reports the Round-Trip Time (RTT) for the DNS query.
* Parses responses for multiple record types:
    * `A` (IPv4 Address)
    * `AAAA` (IPv6 Address)
    * `CNAME` (Canonical Name)
    * `NS` (Name Server)
    * `MX` (Mail Exchange)
    * `TXT` (Text)
* Handles DNS name compression (pointers) in the response.
* Attempts to make an HTTPS request to the first resolved 'A' record to get the HTTP status and RTT.

### How to Run

1.  Navigate to the `Part1_DNS_Client` directory.
2.  Run the script using Python 3:

    ```bash
    python3 DNS_Client.py
    ```

3.  The script will, by default, query for `www.google.com` and `www.wikipedia.org` and print the results to the console.

---

## Part 2: Congestion Control

This section implements and evaluates different congestion control mechanisms for a reliable file transfer over an unreliable UDP. The sender transmits a file (`file.mp3`) to a receiver over an emulated network, and reports on performance.

**Sender Implementations:**

* `sender_stop_and_wait.py`: A simple Stop-and-Wait sender. It sends one packet and waits for its specific acknowledgment before sending the next.
* `sender_fixed_sliding_window.py`: (File not provided in full, but assumed) A sender using a fixed-size sliding window protocol.
* `sender_reno.py`: (File not provided in full, but assumed) A sender implementing a TCP Reno-like congestion control algorithm (Slow Start, Congestion Avoidance, Fast Retransmit).

### Instructions

(Based on `Part2_Congestion_Control/2024_congestion_control_ecs152a-main/README.md`)

1.  **Start the Receiver/Simulator:**
    * Navigate to the `Part2_Congestion_Control/2024_congestion_control_ecs152a-main/docker` directory.
    * Run the simulator script: `./start-simulator.sh`.
    * Wait for the `Receiver running` message. The receiver listens on `localhost:5001`.

2.  **Run the Sender:**
    * Open a **new terminal**.
    * Navigate to the root `Part2_Congestion_Control` directory.
    * Run one of the sender scripts (e.g., Stop-and-Wait):

        ```bash
        python3 sender_stop_and_wait.py
        ```

3.  **Termination:**
    The sender will send the complete file, then an empty message to signal the end. It waits for a `fin` message from the receiver and replies with `==FINACK==` to complete the transfer and shut down both processes.

4.  **Output:**
    The sender script will print the final:
    * Throughput (bytes per second)
    * Average Packet Delay (seconds)
    * A combined performance metric

---

## Part 3: BGP Analysis

**File:** `Part3_BGP_Analysis/bgp_analysis.py`

This script analyzes a BGP (Border Gateway Protocol) RIB (Routing Information Base) dump provided in a CSV file (`bgp_rib.csv`).

### Features

The script can be configured to perform one of three functions:

1.  **`aspath`:** Finds and prints the RIB entry with the longest AS-PATH.
2.  **`bgp_36992`:** Filters the RIB for all routes originating from AS 36992.
    * Prints the total number of prefixes found.
    * Prints the range of prefix lengths.
    * Saves the filtered entries to `bgp_36992.csv`.
3.  **`forwarding`:** Constructs a basic forwarding table.
    * For each prefix, it selects the route with the **shortest AS-PATH**.
    * Saves the resulting `(Destination Prefix, Next Hop)` pairs to `forwarding-table.csv`.

### How to Run

1.  Ensure the BGP data file (`bgp_rib.csv`) is in the `Part3_BGP_Analysis` directory.
2.  Edit `bgp_analysis.py` and modify the `function` variable in the `if __name__ == "__main__"` block to one of the following strings:
    * `"aspath"`
    * `"bgp_36992"` (This is the default in the provided file)
    * `"forwarding"`
3.  Navigate to the `Part3_BGP_Analysis` directory and run the script:

    ```bash
    python3 bgp_analysis.py
    ```

4.  The script will print results to the console and/or generate new CSV files (`bgp_36992.csv`, `forwarding-table.csv`) based on the selected function.
