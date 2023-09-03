
from copy import deepcopy
import random
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout


# Konstantes dēļa izmēram
ROWS = 6
COLUMNS = 7


# Konstantes spēlētājiem
PLAYER = 1
COMPUTER = 2



def create_board():
    return [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]



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
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Pārbaudu vertikālās uzvaras
    for r in range(ROWS - 3):
        for c in range(COLUMNS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Pārbaude, vai uzvar diagonāle (pozitīvs slīpums).
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Pārbaude, vai uzvar diagonāle (negatīvs slīpums).
    for r in range(3, ROWS):
        for c in range(COLUMNS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
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
        row_array = [int(i) for i in list(board[r])]
        for c in range(COLUMNS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Novērtējums vertikāli
    for c in range(COLUMNS):
        col_array = [int(board[r][c]) for r in range(ROWS)]
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

    if maximizing_player:  # Ja pašreizējais mezgls ir maksimizēšanas mezgls
        value = float('-inf')
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_row(board, col)
            temp_board = deepcopy(board)
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
        value = float('inf')
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_row(board, col)
            temp_board = deepcopy(board)
            drop_piece(temp_board, row, col, PLAYER)   # Cilvēka gājiens
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break        # Pārtraucam ciklu — alfa-beta izgriešana
        return column, value



class ConnectFourBoard(GridLayout):

    def initialize_game_field(self):
        self.rows = 6
        self.board = create_board()
        self.buttons = [[None] * 7 for _ in range(6)]
        self.game_over = False
        self.turn = PLAYER
        for r in range(6):   # Izveido pogas spēles laukumam
            for c in range(7):
                self.buttons[r][c] = Button()
                self.buttons[r][c].bind(on_press=lambda btn, col=c: self.drop_piece(col))
                self.add_widget(self.buttons[r][c])


    # Sākuma logs vārda ievadīšanai
    def start_game(self):
        self.player_name = ""
        box = BoxLayout(orientation='vertical')
        text_input = TextInput(hint_text="Enter your name")
        submit_button = Button(text="Start Game")

        submit_button.bind(on_press=lambda instance: self.set_player_name(text_input.text))

        box.add_widget(text_input)
        box.add_widget(submit_button)

        self.popup = Popup(title="Welcome",
                    content=box,
                    size_hint=(None, None), size=(300, 300))
        self.popup.open()

    def set_player_name(self, name):   # Iestatiet spēlētāja vārdu un sāciet spēli
        self.player_name = name
        self.initialize_game_field()
        self.popup.dismiss()



    def __init__(self, **kwargs):
        super(ConnectFourBoard, self).__init__(**kwargs)
        self.start_game()



    def drop_piece(self, col):
        if self.game_over:  # Pārbaude vai spēle ir beigusies
            return

        if is_valid_location(self.board, col):
            row = get_row(self.board, col)
            drop_piece(self.board, row, col, self.turn)
            self.update_board()
            #Pārbaud uz uzvarētāju
            if winning_move(self.board, self.turn):
                self.game_over = True
                winner = self.player_name if self.turn == PLAYER else "Computer"
                box = BoxLayout(orientation='vertical')
                label = Label(text=f'{winner} wins!')
                restart_button = Button(text="Restart")
                
                restart_button.bind(on_press=lambda instance: self.restart_game(popup))

                box.add_widget(label)
                box.add_widget(restart_button)

                popup = Popup(title='Game Over',
                            content=box,
                            size_hint=(None, None), size=(300, 300))
                popup.open()
        self.turn = COMPUTER if self.turn == PLAYER else PLAYER
        if self.turn == COMPUTER and not self.game_over:
            self.computer_move()


    def restart_game(self, window_close=None):
        self.board = create_board() 
        self.update_board()  
        self.game_over = False  
        self.turn = PLAYER  
        
        if window_close:  
            window_close.dismiss()


    def computer_move(self):
        col, _ = minimax(self.board, 2, float('-inf'), float('inf'), True)
        self.drop_piece(col)


    def update_board(self):
        for r in range(6):
            for c in range(7):
                if self.board[r][c] == PLAYER:
                    self.buttons[5-r][c].background_color = (0, 0, 1, 1)
                elif self.board[r][c] == COMPUTER:
                    self.buttons[5-r][c].background_color = (1, 0, 0, 1)
                else:
                    self.buttons[5-r][c].background_color = (1, 1, 1, 1)


class ConnectFourApp(App):

    def build(self):
        return ConnectFourBoard()

if __name__ == '__main__':
    ConnectFourApp().run()



