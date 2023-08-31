
import numpy as np
import tkinter as tk



# Konstantes dēļa izmēram
ROWS = 6
COLUMNS = 7


# Konstantes spēlētājiem
PLAYER = 1
COMPUTER = 2



def create_board():
    return np.zeros((ROWS, COLUMNS), dtype=int)


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROWS - 1][col] == 0


def get_row(board, col):
    for r in range(ROWS):
        if board[r][col] == 0:
            return r


def winning_move(board, piece):
    # Pārbaudu horizontālās uzvaras
    for r in range(ROWS):
        for c in range(COLUMNS - 3):
            if np.all(board[r, c:c + 4] == piece):
                return True

    # Pārbaudu vertikālās uzvaras
    for r in range(ROWS - 3):
        for c in range(COLUMNS):
            if np.all(board[r:r + 4, c] == piece):
                return True

    # Pārbaude, vai uzvar diagonāle (pozitīvs slīpums).
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            if np.all([board[r + i][c + i] == piece for i in range(4)]):
                return True

    # Pārbaude, vai uzvar diagonāle (negatīvs slīpums).
    for r in range(3, ROWS):
        for c in range(COLUMNS - 3):
            if np.all([board[r - i][c + i] == piece for i in range(4)]):
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER if piece == COMPUTER else COMPUTER

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score


def evaluate_board(board, piece):
    score = 0

    # Novērtējums horizontāli
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMNS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Novērtējums vertikāli
    for c in range(COLUMNS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Novērtē pozitīvās slīpuma diagonāles
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Novērtē negatīvās slīpuma diagonāles
    for r in range(3, ROWS):
        for c in range(COLUMNS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

# Funkcija, kas pārbauda, vai tāfeles stāvoklis ir (galīgs)
def is_terminal_node(board):
    return winning_move(board, PLAYER) or winning_move(board, COMPUTER) or len(get_valid_locations(board)) == 0  # Parbauda, vai uz galda ir uzvarošs gājiens , atgriez True

# Funkcija iegūst visas pieejamās kolonnas, kurās var pārvietoties
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# minimax algoritma realizacija
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)     # Iegūstam visu derīgo kolonnu sarakstu
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:   # Ja mezgls ir termināls vai dziļums ir nulle
        if is_terminal:
            if winning_move(board, COMPUTER):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER):
                return (None, -10000000000000)
            else:  # Spēles beigas, nav gājienu
                return (None, 0)
        else:  # Dziļums ir 0
            return (None, evaluate_board(board, COMPUTER))

    if maximizing_player:    # Ja pašreizējais mezgls ir maksimizēšanas mezgls
        value = -np.inf
        column = np.random.choice(valid_locations)

        for col in valid_locations:
            row = get_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, COMPUTER) #Datora gājiens
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Pārtraucam ciklu — alfa-beta izgriešana
        return column, value
    
    else:  # Minimizācijas mezgls
        value = np.inf
        column = np.random.choice(valid_locations)

        for col in valid_locations:
            row = get_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER)   # Cilvēka gājiens
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break        # Pārtraucam ciklu — alfa-beta izgriešana
        return column, value



class ConnectFourGUI:
    def restart_game(self, window_close):  # Aiztaisa logu un restarte speli
        self.board = create_board()
        self.update_board()
        self.game_over = False
        self.turn = PLAYER
        window_close.destroy()

    def __init__(self, root):      # Inicialize grafisko lietotāja interfeisu
        self.root = root
        self.root.title("Connect Four")
        
        self.board = create_board()
        self.buttons = np.array([[None] * COLUMNS for _ in range(ROWS)])
        for r in range(ROWS):
            for c in range(COLUMNS):
                self.buttons[r][c] = tk.Button(root, text=" ", width=10, height=2,
                command=lambda col=c: self.drop_piece(col))
                self.buttons[r][c].grid(row=r, column=c)
        self.turn = PLAYER
        self.game_over = False

    # Apstrādā pogu nospiešanu
    def drop_piece(self, col):  
        if self.game_over:
            return
        if is_valid_location(self.board, col):
            row = get_row(self.board, col)
            drop_piece(self.board, row, col, self.turn)
            self.update_board()
            if winning_move(self.board, self.turn):  #Noskaidrojam kas uzvara un uztaisa logu
                self.game_over = True
                end = tk.Toplevel()
                end.title("Game Over")
                winner = player_name if self.turn == PLAYER else "Computer"
                msg = tk.Message(end, text=f"{winner} wins!")
                msg.pack()
                button = tk.Button(end, text="Restart", command=lambda: self.restart_game(end))
                button.pack()
            else:
                self.turn = COMPUTER if self.turn == PLAYER else PLAYER
                if self.turn == COMPUTER:
                    self.computer_move()

    # Datora gājiens
    def computer_move(self):
        col, _ = minimax(self.board, 1, -np.inf, np.inf, True)   #Datora stiprums
        self.drop_piece(col)

    # Atjauno grafisko interfeisu
    def update_board(self):
        for r in range(ROWS):
            for c in range(COLUMNS):
                if self.board[r][c] == PLAYER:
                    self.buttons[ROWS-1-r][c].config(bg='blue')
                elif self.board[r][c] == COMPUTER:
                    self.buttons[ROWS-1-r][c].config(bg='red')
                else:
                    self.buttons[ROWS-1-r][c].config(bg='white')



def get_player_name():
    def submit_name():
        global player_name
        player_name = entry_name.get()
        if player_name:  # Pārbauda vai ir uzrakstīts vārds
            Player_name.destroy()
    Player_name = tk.Tk()
    Player_name.title("Uzrakstiet jūsu vārdu")
    label_name = tk.Label(Player_name, text="Uzrakstiet jūsu vārdu:")
    label_name.pack()
    entry_name = tk.Entry(Player_name)
    entry_name.pack()
    sub_button = tk.Button(Player_name, text="Ok", command=submit_name)
    sub_button.pack()
    Player_name.mainloop()

# Iegūstam vārdu
get_player_name()

# Šis nosacījums parāda, kāds kods ir jāizpilda, palaižot failu
if __name__ == "__main__":
    if player_name:
        root = tk.Tk()
        game = ConnectFourGUI(root)
        root.mainloop()

