import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MaxNLocator
import time
import os
import subprocess
import re


def execute_traceroute(destination):
    """
    Executes a traceroute to the specified destination and returns the output.

    Args:
        destination (str): The hostname or IP address to trace

    Returns:
        str: The raw output from the traceroute command
        
    
    """
    #Use the subprocess module to run the `traceroute` command and then return the standard output.
    process = subprocess.run(["traceroute", "-I", destination], check=True, capture_output=True, text=True)
    
    output = process.stdout
    
    return output
    

    
    # Your code here
    # Hint: Use the subprocess module to run the traceroute command
    # Make sure to handle potential errors

    # Remove this line once you implement the function,
    # and don't forget to *return* the output
    pass

def parse_traceroute(traceroute_output):
    """
    Parses the raw traceroute output into a structured format.

    Args:
        traceroute_output (str): Raw output from the traceroute command

    Returns:
        list: A list of dictionaries, each containing information about a hop:
            - 'hop': The hop number (int)
            - 'ip': The IP address of the router (str or None if timeout)
            - 'hostname': The hostname of the router (str or None if same as ip)
            - 'rtt': List of round-trip times in ms (list of floats, None for timeouts)

    Example:
    ```
        [
            {
                'hop': 1,
                'ip': '172.21.160.1',
                'hostname': 'HELDMANBACK.mshome.net',
                'rtt': [0.334, 0.311, 0.302]
            },
            {
                'hop': 2,
                'ip': '10.103.29.254',
                'hostname': None,
                'rtt': [3.638, 3.630, 3.624]
            },
            {
                'hop': 3,
                'ip': None,  # For timeout/asterisk
                'hostname': None,
                'rtt': [None, None, None]
            }
        ]
    ```
    """

    #Start with an empty list that we will use to store all of our hops to then be returned when we run the script.
    result = []

    #Split the output we got from using `subprocess.run` to run the `traceroute` command in the first function and then split it at every new line.
    lines = traceroute_output.split('\n')

    #Iterate over those lines and define the first line as the first index in the list of lines.
    #We also want to check if the first line exists and if it is not a digit because it if it isn't a digit then we will start the index after the first line.
    if lines:
        first_line = lines[0].strip()
        if first_line and first_line.isdigit():
            pass
        else:
            lines = lines[1:]

    #Start iterating over the lines and also strip off any unnesecarry whitespace.
    #If there is nothing it will keep the set values of `None` for the hop and continue.
    for line in lines:
        line = line.strip()
        if not line:
            continue

        #Define the dictionary that will be used to format the output of the `traceroute` command.
        hop = {
            "hop" : None,
            "ip" : None, 
            "hostname" : None, 
            "rtt" : [None, None, None]
        }

    
        #Used `re.match` to extract the first number from the line, which is the hop number.
        #Also check if hop_num is `None` and if it is skip the line and move onto the next.
        #Then the hop number is converted into an integer and stored in our dictionary.
        hop_num = re.match(r'^\s*(\d+)', line)
        if not hop_num:
            continue
        hop["hop"] = int(hop_num.group(1))


        #Incase we get three asterisks in a row which means that there was a timeout then we append and move on since those predefined values of `None` will stay the same.
        if "* * *" in line:
            result.append(hop)
            continue

        #Define the regular expression pattern that we will use to find only the IP address without any parentheses.
        ip_address_pattern = r'\(?\b(?:\d{1,3}\.){3}\d{1,3}\b\)?'

        #`re.search` will find the IP address, using the pattern that we defined, anywhere in the `traceroute_output`.
        ip_match = re.search(ip_address_pattern, line)

        #If the `ip_match` actually exists then we have to append the match from the `re.search` using `.group` and strip it for parentheses incase it is incased in them. 
        if ip_match:
            hop["ip"] = ip_match.group(0).strip("()")

            #Since we know that the hostname comes before the ip address to find the hostname we can use `.start()` since it will take the index where the IP address starts and then look through the section before the IP address starts.
            hostname = line[:ip_match.start()].strip()

            #After we get everything that comes before the IP address we should have the number of hops and the hostname so we will need to split at the spaces and take the last index which will be the hostname.
            hostname_parts = hostname.split()

            #Here we run a whole bunch of checks to make sure that the hostname is actually the hostname and not a number or the IP address.
            if hostname_parts and not hostname_parts[-1].isdigit() and hostname_parts != hop["ip"]:
                hop["hostname"] = hostname_parts[-1]
            else:
                hop["hostname"] = None
        else:
            hop["ip"] = None
            hop["hostname"] = None


        #Here we use `re.findall` with a regular expression that will find all instances of a string that has the numbers 0-9 and ms for milliseconds after. 
        rtt_matches = re.findall(r"([0-9.]+\s*ms|\*)", line)

        #iterate over a range of 3 since we know that there will be three RTT values
        for i in range(3):
            if i < len(rtt_matches):

                #Strip off any whitespace
                rtt = rtt_matches[i].strip()

                #If it is an asterisk then set it equal to `None`.
                if rtt == "*":
                    hop["rtt"][i] = None
                else:
                    #Also convert the RTT to a float(decimal) and `None` if it is an asterisk.
                    rtt_number = rtt.replace("ms", "").strip()
                    hop["rtt"][i] = float(rtt_number)

        
        #Finally append the parsed hop data to the results list to be returned.
        result.append(hop)

    return result
    # Your code here
    # Hint: Use regular expressions to extract the relevant information
    # Handle timeouts (asterisks) appropriately

    # Remove this line once you implement the function,
    # and don't forget to *return* the output

# ============================================================================ #
#                    DO NOT MODIFY THE CODE BELOW THIS LINE                    #
# ============================================================================ #
def visualize_traceroute(destination, num_traces=3, interval=5, output_dir='output'):
    """
    Runs multiple traceroutes to a destination and visualizes the results.

    Args:
        destination (str): The hostname or IP address to trace
        num_traces (int): Number of traces to run
        interval (int): Interval between traces in seconds
        output_dir (str): Directory to save the output plot

    Returns:
        tuple: (DataFrame with trace data, path to the saved plot)
    """
    all_hops = []

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print(f"Running {num_traces} traceroutes to {destination}...")

    for i in range(num_traces):
        if i > 0:
            print(f"Waiting {interval} seconds before next trace...")
            time.sleep(interval)

        print(f"Trace {i+1}/{num_traces}...")
        output = execute_traceroute(destination)
        hops = parse_traceroute(output)

        # Add timestamp and trace number
        timestamp = time.strftime("%H:%M:%S")
        for hop in hops:
            hop['trace_num'] = i + 1
            hop['timestamp'] = timestamp
            all_hops.append(hop)

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(all_hops)

    # Calculate average RTT for each hop (excluding timeouts)
    df['avg_rtt'] = df['rtt'].apply(lambda x: np.mean([r for r in x if r is not None]) if any(r is not None for r in x) else None)

    # Plot the results
    plt.figure(figsize=(12, 6))

    # Create a subplot for RTT by hop
    ax1 = plt.subplot(1, 1, 1)

    # Group by trace number and hop number
    for trace_num in range(1, num_traces + 1):
        trace_data = df[df['trace_num'] == trace_num]

        # Plot each trace with a different color
        ax1.plot(trace_data['hop'], trace_data['avg_rtt'], 'o-',
                label=f'Trace {trace_num} ({trace_data.iloc[0]["timestamp"]})')

    # Add labels and legend
    ax1.set_xlabel('Hop Number')
    ax1.set_ylabel('Average Round Trip Time (ms)')
    ax1.set_title(f'Traceroute Analysis for {destination}')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Make sure hop numbers are integers
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    # Save the plot to a file instead of displaying it
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    safe_dest = destination.replace('.', '-')
    output_file = os.path.join(output_dir, f"trace_{safe_dest}_{timestamp}.png")
    plt.savefig(output_file)
    plt.close()

    print(f"Plot saved to: {output_file}")

    # Return the dataframe and the path to the saved plot
    return df, output_file

# Test the functions
if __name__ == "__main__":
    # Test destinations
    destinations = [
        "google.com",
        "amazon.com",
        "bbc.co.uk"  # International site
    ]

    for dest in destinations:
        df, plot_path = visualize_traceroute(dest, num_traces=3, interval=5)
        print(f"\nAverage RTT by hop for {dest}:")
        avg_by_hop = df.groupby('hop')['avg_rtt'].mean()
        print(avg_by_hop)
        print("\n" + "-"*50 + "\n")
