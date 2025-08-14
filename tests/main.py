import logging

from ..tic_tac_toe.user_config.user_credentials_gui import UserCredentialsGUI

def my_callback(credentials):
    print("Credenciales válidas:", credentials)
    # Aquí puedes continuar con la lógica para lanzar el juego

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    # Asumiendo que tienes estos datos ya cargados:
    animals = {'Dragon': '🐉', 'Dolphin': '🐬', 'Tiger': '🐯'}
    colors = {'Gold': (255, 215, 0), 'Blue': (0, 0, 255)}

    gui = UserCredentialsGUI()
    gui.mainloop()
