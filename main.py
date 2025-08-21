import logging
from tic_tac_toe.core.logic_game import TicTacToeLogic
from tic_tac_toe.gui.tic_tac_toe_game import TicTacToeGame
from tic_tac_toe.user_config.user_credentials_gui import UserCredentialsGUI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    user_credentials = UserCredentialsGUI() 
    user_credentials.mainloop()

    logic = TicTacToeLogic(size_board=3)
    app = TicTacToeGame(logic)
    app.mainloop()
    app._log.print_logs()

