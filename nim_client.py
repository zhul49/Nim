import socket, sys

def send_line(sock, s: str):
    sock.sendall((s + "\n").encode())

def recv_line(sock) -> str:
    buf = []
    while True:
        ch = sock.recv(1)
        if not ch:
            return ""
        if ch == b"\n":
            return "".join(part.decode() if isinstance(part, bytes) else part for part in buf).rstrip("\r")
        buf.append(ch)

def render_board(msg):
    # msg is like: "BOARD 3 5 2"
    parts = msg.split()
    rows = list(map(int, parts[1:]))
    print("\nBoard:")
    for i, n in enumerate(rows, start=1):
        print(f"{i}: " + "|" * n)
    print()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 nim_client.py <SERVER_HOST> <PORT>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[client] Connecting to {host}:{port} ...")
    s.connect((host, port))
    print("[client] Connected.")

    player_num = None

    try:
        while True:
            line = recv_line(s)
            if not line:
                print("[client] Server closed the connection.")
                break

            if line.startswith("ASSIGN"):
                # "ASSIGN 1" or "ASSIGN 2"
                player_num = int(line.split()[1])
                print(f"[client] You are Player {player_num}.")
            elif line.startswith("BOARD"):
                render_board(line)
            elif line.startswith("MSG"):
                print(line[4:])
            elif line.startswith("ERROR"):
                print("Error:", line[6:])
            elif line.startswith("YOUR_TURN"):
                # prompt once, send one line "row count"
                try:
                    raw = input("Enter move '<row> <count>': ").strip()
                except EOFError:
                    raw = ""
                if not raw:
                    raw = "0 0"
                s.sendall((raw + "\n").encode())
            elif line.startswith("WIN"):
                print("\n" + line[4:])
                break
            else:
                # Unknown line; print for debugging
                print("[client] <<", line)
    except KeyboardInterrupt:
        print("\n[client] Bye.")
    finally:
        try:
            s.close()
        except:
            pass

if __name__ == "__main__":
    main()
