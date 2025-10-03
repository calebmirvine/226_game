from Board import Board
from Player import Player


#Initialize Board and Player

b = Board(3, '3')
p1 = Player('One')

def runGame():
    game_active = True
    while game_active:
        print('---Treasure Hunt---')
        print(b)
        try:
            print("Select a Row & Column...")
            print("Row: ")
            row = int(input())

            print("Column: ")
            col = int(input())

        except ValueError:
            print("\033[31mInvalid Input. Try again.\033[0m")
            #continue to the next turn
            continue

        p1.add_score(b.pick(row, col))
        print(p1.__str__())

runGame()