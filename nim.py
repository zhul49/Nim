import sys

player = 1
human_player_num = 1
game_continue = True
board = []
vs_computer = False
vs_computer_player_num = 2

def initialize_board():
    global vs_computer
    global player
    print("Welcome to Nim!")
    init_rows = int(input("Enter number of rows: "))
    if init_rows < 1:
        print("Please enter a value greater than 0")
    else:
        global board
        board = []
        for i in range(init_rows):
            sticks = int(input(f"Enter number of sticks in row {i + 1}: "))
            if sticks < 1:
                print("Please enter a value greater than 0")
                return initialize_board()
            else:
                board.append(sticks)
        mode = str(input("Play against computer? (y/n): "))
        if mode == 'y':
            vs_computer = True
            global vs_computer_player_num
            global human_player_num
            vs_computer_player_num = int(input("Do want the computer to be player 1 or 2: "))
            if vs_computer_player_num == 1:
                human_player_num = 2
            elif vs_computer_player_num == 2:
                human_player_num = 1
        else:
            vs_computer = False

############################### Begin_Citation [1] ############################
def computer_move():

    nim_sum = 0
    for sticks in board:
        nim_sum ^= sticks
    for i in range(len(board)):
        sticks = board[i]
        target = sticks ^ nim_sum
        if target < sticks:
            num_sticks = sticks - target
            print(f"Computer removes {num_sticks} stick(s) from row {i+1}")
            board[i] -= num_sticks
            return
    for i in range(len(board)):
        if board[i] > 0:
            print(f"Computer removes 1 stick from row {i+1}")
            board[i] -= 1
            return
############################### End_Citation [1] #############################


def print_board(board):
    i = 1
    for row in board:
        print(str(i) + ": " + "|" * row)
        i += 1

def main():
    global player
    global game_continue
    global vs_computer_player_num
    
    print_board(board)
    print(f"\n Player {player}'s turn")
    print("Enter which row and how many")
    if vs_computer and player == vs_computer_player_num:
        computer_move()
        if player == 1:
            player = 2
        elif player == 2:
            player = 1
    else:
        section = int(input("Enter which row: "))
        if section > len(board):
            print(f"Please enter a row that is equal or less than {len(board)}")
        else:
            section -= 1
            num_sticks = int(input("Enter how many sticks to remove: "))
            
            if num_sticks > board[section]:
                print("Please enter a value that is less than or equal to the number of remaining sticks in the row")
            if sum(board) - num_sticks <= 0:
                print("You cannot take all the remaining sticks")
            else:
                board[section] = board[section] - num_sticks

                total_sticks = sum(board)

                if total_sticks == 1:
                    if player == 1:
                        print("\n Player 1 wins!")
                        game_continue = False
                        sys.exit(0)
                    elif player == 2:
                        print("\n Player 2 wins!")
                        game_continue = False
                        sys.exit(0)
                elif total_sticks == 0:
                    if player == 1:
                        print("\n Player 2 wins!")
                        game_continue = False
                        sys.exit(0)
                    elif player == 2:
                        print("\n Player 1 wins!")
                        game_continue = False
                        sys.exit(0)
                
                if player == 1:
                    player = 2
                elif player == 2:
                    player = 1


if __name__ == "__main__":
    initialize_board()
    while game_continue:
        main()
