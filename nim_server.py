import socket, threading, sys

# ---------- Tiny line protocol helpers ----------
def send_line(sock, s: str):
    sock.sendall((s + "\n").encode())

def recv_line(sock) -> str:
    buf = []
    while True:
        ch = sock.recv(1)
        if not ch:
            return ""  # disconnected
        if ch == b"\n":
            return b"".join(buf).decode().rstrip("\r")
        buf.append(ch)

# ---------- Game state ----------
board = []
player = 1  # 1 or 2
game_continue = True

def print_board_console():
    for i, sticks in enumerate(board, start=1):
        print(f"{i}: " + "|" * sticks)
    print()

def board_to_str():
    # send as space-separated integers
    return " ".join(str(x) for x in board)

def total_sticks():
    return sum(board)

def valid_move(section: int, num_sticks: int) -> (bool, str):
    if section < 1 or section > len(board):
        return False, f"Row must be 1..{len(board)}"
    if num_sticks < 1:
        return False, "You must remove at least 1 stick"
    if num_sticks > board[section - 1]:
        return False, "Cannot remove more than the remaining sticks in that row"
    # keep your rule: cannot take all remaining sticks
    if total_sticks() - num_sticks <= 0:
        return False, "You cannot take all the remaining sticks"
    return True, ""

def apply_move(section: int, num_sticks: int):
    board[section - 1] -= num_sticks

def check_win_and_message():
    # Mirror your original logic
    ts = total_sticks()
    if ts == 1:
        # current player just moved and left 1 → current player wins
        return True, f"Player {player} wins!"
    if ts == 0:
        # shouldn't happen due to rule, but keep for parity
        other = 2 if player == 1 else 1
        return True, f"Player {other} wins!"
    return False, ""

def handle_player(conn_me, conn_other, my_num):
    # This thread only listens to disconnections; moves are prompted by the main loop.
    try:
        while True:
            data = conn_me.recv(1)
            if not data:
                # If a player disconnects, end the game.
                raise ConnectionError("Disconnected")
    except Exception:
        pass

def main():
    global board, player, game_continue

    # ----- set up the initial board on the server console -----
    print("Welcome to Nim (server).")
    while True:
        try:
            init_rows = int(input("Enter number of rows (>0): "))
        except Exception:
            print("Please enter an integer.")
            continue
        if init_rows < 1:
            print("Please enter a value greater than 0")
            continue
        break

    board = []
    for i in range(init_rows):
        while True:
            try:
                sticks = int(input(f"Enter number of sticks in row {i+1} (>0): "))
            except Exception:
                print("Please enter an integer.")
                continue
            if sticks < 1:
                print("Please enter a value greater than 0")
                continue
            board.append(sticks)
            break

    # ----- network setup -----
    HOST = "0.0.0.0"
    PORT = 5000
    print(f"\n[server] Listening on {HOST}:{PORT} ...")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(2)

    conn1, addr1 = srv.accept()
    print(f"[server] Player 1 connected from {addr1}")
    send_line(conn1, "ASSIGN 1")

    conn2, addr2 = srv.accept()
    print(f"[server] Player 2 connected from {addr2}")
    send_line(conn2, "ASSIGN 2")

    # background watchers (optional)
    threading.Thread(target=handle_player, args=(conn1, conn2, 1), daemon=True).start()
    threading.Thread(target=handle_player, args=(conn2, conn1, 2), daemon=True).start()

    # ----- game loop -----
    while game_continue:
        # send board state to both
        send_line(conn1, "BOARD " + board_to_str())
        send_line(conn2, "BOARD " + board_to_str())

        print_board_console()
        print(f"[server] Player {player}'s turn.")

        if player == 1:
            active, waiting = conn1, conn2
        else:
            active, waiting = conn2, conn1

        # prompt active player
        send_line(active, f"MSG Your turn, Player {player}. Enter: <row> <count>")
        send_line(active, "YOUR_TURN")
        send_line(waiting, f"MSG Waiting for Player {player}...")

        # read one line: "row count"
        line = recv_line(active)
        if not line:
            print("[server] A player disconnected. Ending game.")
            break
        parts = line.strip().split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            send_line(active, "ERROR Please send two integers: <row> <count>")
            continue

        section = int(parts[0])
        num = int(parts[1])

        ok, err = valid_move(section, num)
        if not ok:
            send_line(active, "ERROR " + err)
            continue

        apply_move(section, num)

        # check win
        won, msg = check_win_and_message()
        if won:
            # final board to both
            send_line(conn1, "BOARD " + board_to_str())
            send_line(conn2, "BOARD " + board_to_str())
            send_line(conn1, "MSG " + msg)
            send_line(conn2, "MSG " + msg)
            send_line(conn1, "WIN " + msg)
            send_line(conn2, "WIN " + msg)
            break

        # switch player
        player = 2 if player == 1 else 1

    try:
        conn1.close()
    except:
        pass
    try:
        conn2.close()
    except:
        pass
    srv.close()
    print("[server] Game over.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[server] Shutting down.")
        sys.exit(0)
