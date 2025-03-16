import csv

def analyze_bgp(filename, function):
    with open(filename, 'r') as bgp_file:
        bgp_reader = csv.DictReader(bgp_file, delimiter=";")
        bgp_data = list(bgp_reader)

    print(f"Number of BGP RIBs: {len(bgp_data)}")

    if function == "aspath":
        get_longest_aspath(bgp_data)
    elif function == "bgp_36992":
        construct_bgp_36992_table(bgp_data, "bgp_36992.csv")
    elif function == "forwarding":
        construct_forwarding_table(bgp_data, "bgp_36992.csv", "forwarding-table.csv")
    else:
        print("Invalid function name passed, please try again.")

def get_longest_aspath(bgp_data):
    longest_aspath_rib = None
    max_aspath_length = 0
    for entry in bgp_data:
        aspath = entry["ASPATH"].split()
        aspath_length = len(aspath)

        if aspath_length > max_aspath_length:
            max_aspath_length = aspath_length
            longest_aspath_rib = entry

    print(f"RIB with the longest ASPATH:")
    print(f"Longest ASPATH Length: {max_aspath_length}")
    print(f"Fully Entry: {longest_aspath_rib}")

def construct_bgp_36992_table(bgp_data, output_filename):
    entry_list = []
    prefix_lengths = []
    for entry in bgp_data:
        aspath = entry["ASPATH"].split()
        if aspath and aspath[-1] == "36992":
            entry_list.append(entry)
            prefix_lengths.append(int(entry["PREFIX"].split("/")[1]))

    # Count prefixes and find prefix length range
    num_prefixes = len(entry_list)
    min_prefix_length = min(prefix_lengths) if prefix_lengths else None
    max_prefix_length = max(prefix_lengths) if prefix_lengths else None

    # Save the filtered BGP table to CSV
    if entry_list:
        with open(output_filename, "w", newline="") as csvfile:
            fieldnames = entry_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(entry_list)

    print(f"BGP table for AS 36992 saved to {output_filename}")
    print(f"Number of prefixes: {num_prefixes}")
    print(f"Prefix length range: {min_prefix_length} - {max_prefix_length}")

def construct_forwarding_table(bgp_data, input_filename, output_filename):
    # Select the shortest ASPATH for each prefix
    forwarding_table = {}
    
    for entry in bgp_data:
        prefix = entry["PREFIX"]
        next_hop = entry["NEXT_HOP"]
        aspath_length = len(entry["ASPATH"].split())

        # Store only the shortest path
        if prefix not in forwarding_table or aspath_length < forwarding_table[prefix][1]:
            forwarding_table[prefix] = (next_hop, aspath_length)

    # Write to forwarding-table.csv
    with open(output_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Destination Prefix", "Next Hop"])
        for prefix, (next_hop, _) in forwarding_table.items():
            writer.writerow([prefix, next_hop])

    print(f"Forwarding table saved to {output_filename}")

if __name__ == "__main__":
    filename = "bgp_rib.csv"
    function = "bgp_36992" # Can be "aspath", "bgp_36992", or "forwarding"
    analyze_bgp(filename, function)