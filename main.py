#!/usr/bin/env python3

### Imports
import os
import shutil
from datetime import datetime

### Settings
MAX_SAVES = 5
SAVES_FOLDER_NAME = ".saves"
SAVEFILE_PREFIX = "save_"
LOAD_BACKUP_NAME = "load_backup"
GAME_CONFIRMATION_FILE = "thumb.png"

### Constants
HOME_PATH = os.environ.get('HOME')
ZOMBOID_PATH = HOME_PATH + "/Zomboid"
GAMES_PATH = ZOMBOID_PATH + "/Saves"
SAVES_PATH = ZOMBOID_PATH + "/" + SAVES_FOLDER_NAME

### Functions
def get_games_and_saves():
    games_and_saves_list = {}

    # find all games
    gametypes_list = []
    if os.path.exists(GAMES_PATH) :
        gametypes_list = os.listdir(GAMES_PATH)
    for gametype in gametypes_list :
        gametype_path = GAMES_PATH + "/" + gametype

        games_list = []
        if os.path.exists(gametype_path) :
            games_list = os.listdir(gametype_path)
        for game in games_list :
            game_path = gametype_path + "/" + game
            
            game_confirmation_file_path = game_path + "/" + GAME_CONFIRMATION_FILE
            if os.path.exists(game_confirmation_file_path) :
                games_and_saves_list[game] = {
                    "game_exist"    : True,
                    "gametype"      : gametype,
                    "creation_time" : os.path.getmtime(game_confirmation_file_path),
                }
    
    # find all saves
    gametypes_list = []
    if os.path.exists(SAVES_PATH) :
        gametypes_list = os.listdir(SAVES_PATH)
    for gametype in gametypes_list :
        gametype_path = SAVES_PATH + "/" + gametype

        saves_list = []
        if os.path.exists(gametype_path) :
            saves_list = os.listdir(gametype_path)
        for save in saves_list :
            save_path = gametype_path + "/" + save

            savefiles_list = []

            files_list = []
            if os.path.exists(save_path) :
                files_list = os.listdir(save_path)
            for f in files_list :
                if SAVEFILE_PREFIX in f :
                    savefiles_list.append({
                        "name"          : f,
                        "creation_time" : os.path.getmtime(save_path + "/" + f),
                    })
            
            savefiles_list = sorted(savefiles_list, key=lambda d: d['creation_time'], reverse=True)

            if save in games_and_saves_list :
                games_and_saves_list[save]["savefiles_list"] = savefiles_list
            else :
                games_and_saves_list[save] = {
                    "gametype"          : gametype,
                    "savefiles_list"    : savefiles_list,
                }
    
    return games_and_saves_list


def save_game(games_and_saves_list, game):
    savefiles_list = []
    if games_and_saves_list[game].get("savefiles_list") :
        savefiles_list = games_and_saves_list[game]["savefiles_list"]
    
    savefile_name = ""
    if len(savefiles_list) == 0 :
        savefile_name = SAVEFILE_PREFIX + "00"
    elif len(savefiles_list) < MAX_SAVES :
        for savefile in savefiles_list :
            savefile["save_number"] = int(savefile["name"].replace(SAVEFILE_PREFIX, "").replace(".zip", ""))
        
        save_number = 0
        for save_number in range(MAX_SAVES) :
            for savefile in savefiles_list :
                number_found = False
                if savefile["save_number"] == save_number :
                    number_found = True
                    break
            if not number_found :
                break
        
        savefile_name = SAVEFILE_PREFIX + f"{save_number:02d}"
    else :
        savefile_name = savefiles_list[MAX_SAVES-1]["name"].replace(".zip", "")
    
    save_gametype_path = SAVES_PATH + "/" + games_and_saves_list[game]["gametype"]
    save_game_path = save_gametype_path + "/" + game
    save_path = save_game_path + "/" + savefile_name
    game_path = GAMES_PATH  + "/" + games_and_saves_list[game]["gametype"]  + "/" + game

    if not os.path.exists(SAVES_PATH) :
        os.mkdir(SAVES_PATH)
    if not os.path.exists(save_gametype_path) :
        os.mkdir(save_gametype_path)
    if not os.path.exists(save_game_path) :
        os.mkdir(save_game_path)

    shutil.make_archive(save_path, 'zip', game_path)

    savefile_local_path = SAVES_FOLDER_NAME + "/" + games_and_saves_list[game]["gametype"] + "/" + game + "/" + savefile_name + ".zip"
    print(f"\nGame saved into '{savefile_local_path}'\n")

def load_game(games_and_saves_list, game, savefile):
    save_path = SAVES_PATH + "/" + games_and_saves_list[game]["gametype"] + "/" + game
    savefile_path = save_path + "/" + savefile
    game_path = GAMES_PATH + "/" + games_and_saves_list[game]["gametype"] + "/" + game

    shutil.make_archive(save_path + "/" + LOAD_BACKUP_NAME, 'zip', game_path)

    if os.path.exists(game_path) :
        shutil.rmtree(game_path)

    shutil.unpack_archive(savefile_path, game_path)

    savefile_local_path = SAVES_FOLDER_NAME + "/" + games_and_saves_list[game]["gametype"] + "/" + game + "/" + savefile
    print(f"\nGame loaded from '{savefile_local_path}'\n")
    

### Program
print("\n[ Project Zomboid Saving Utility ]")

games_and_saves_list = get_games_and_saves()

print(
"""
Available options:
1 - quick-save game
2 - save game
3 - quick-load game
4 - load game
0 - exit
"""
)

user_choice = input("Choose what you want to do: ")
match user_choice:
    case "1": # quick-save game
        print("\nAvailable games:")
        sorter = []
        for game in games_and_saves_list :
            if games_and_saves_list[game].get("game_exist") :
                sorter.append({"game" : game, "creation_time" : games_and_saves_list[game]["creation_time"]})

        sorter = sorted(sorter, key=lambda d: d["creation_time"], reverse=True)

        iterator = 0
        for item in sorter :
            iterator += 1
            game = item["game"]
            gametype = games_and_saves_list[game]["gametype"]
            creation_time = datetime.utcfromtimestamp(item["creation_time"]).strftime('%Y-%m-%d %H:%M:%S')
            print(str(iterator) + " - " + game + " | " + gametype + " | " + creation_time)
        
        game_to_save = input("\nChoose what game to save: ")

        try :
            game_to_save = int(game_to_save)
        except ValueError :
            print("\nInvalid input!\n")
            quit()
        
        if game_to_save >= 1 and game_to_save <= len(sorter) :
            save_game(games_and_saves_list, sorter[int(game_to_save) - 1]["game"])
        else :
            print("\nInvalid input!\n")

    case "2": # save game
        print("\nNot implemented yet!\n")

    case "3": # quick-load game
        print("\nAvailable saves:")
        sorter = []
        for save in games_and_saves_list :
            if len(games_and_saves_list[save]["savefiles_list"]) > 0 :
                sorter.append({"save" : save, "creation_time" : games_and_saves_list[save]["savefiles_list"][0]["creation_time"]})

        sorter = sorted(sorter, key=lambda d: d["creation_time"], reverse=True)

        iterator = 0
        for item in sorter :
            iterator += 1
            save = item["save"]
            gametype = games_and_saves_list[save]["gametype"]
            savefile = games_and_saves_list[save]["savefiles_list"][0]["name"]
            creation_time = datetime.utcfromtimestamp(item["creation_time"]).strftime('%Y-%m-%d %H:%M:%S')
            print(str(iterator) + " - " + save + " | " + gametype + " | " + savefile + " | " + creation_time)
        
        game_to_load = input("\nChoose what game to load: ")

        try :
            game_to_load = int(game_to_load)
        except ValueError :
            print("\nInvalid input!\n")
            quit()
        
        if game_to_load >= 1 and game_to_load <= len(sorter) :
            savefile_to_load = games_and_saves_list[sorter[int(game_to_load) - 1]["save"]]["savefiles_list"][0]["name"]
            if savefile_to_load == "load_backup.zip":
                savefile_to_load = games_and_saves_list[sorter[int(game_to_load) - 1]["save"]]["savefiles_list"][1]["name"]

            load_game(
                games_and_saves_list,
                sorter[int(game_to_load) - 1]["save"],
                savefile_to_load
            )
        else :
            print("\nInvalid input!\n")

    case "4": # load game
        print("\nNot implemented yet!\n")

    case "0": # exit
        print("\nGoodbye!\n")

    case _ :
        print("\nInvalid input!\n")
