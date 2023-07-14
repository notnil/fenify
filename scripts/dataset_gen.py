import os
import random
import argparse
from PIL import Image
from src.dataset_gen import random_board, generate_board_image_with_background, generate_board_image_with_squares, piece_set_from_dir, squares_from_dir

# use this if you get OSError: no library called "cairo-2" was found on mac
# export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib

def list_directories(directory):
    # Get a list of all files and directories within the specified directory
    entries = os.listdir(directory)
    # Iterate over the entries and filter out directories
    directories = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]
    return directories

def list_directories_with_target(directory, target_file):
    # Get a list of all files and directories within the specified directory
    entries = os.listdir(directory)

    # Iterate over the entries and filter out directories that contain the target file
    directories = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry)) 
                   and os.path.isfile(os.path.join(directory, entry, target_file))]

    return directories

def list_image_files(directory):
    # Get a list of all files in the specified directory
    files = os.listdir(directory)
    # Filter the files based on the extensions
    image_files = [file for file in files if file.lower().endswith(('.png', '.jpg'))]
    return image_files

def main(args):
    # reset output directory
    if os.path.exists(args.output):
        # delete output directory
        for file in os.listdir(args.output):
            os.remove(os.path.join(args.output, file))
        os.rmdir(args.output)
    os.makedirs(args.output)
        
    # generate internet boards
    piece_sets = list_directories(args.int_piece_sets)
    board_imgs = list_image_files(args.int_boards)
    for _ in range(args.int_count):
        piece_set_dir = os.path.join(args.int_piece_sets,random.choice(piece_sets))
        piece_set = piece_set_from_dir(dir=piece_set_dir, piece_size=64, suffix=".svg")
        random_board_img = os.path.join(args.int_boards,random.choice(board_imgs))
        board_img = Image.open(random_board_img)
        board = random_board()
        file_name = os.path.join(args.output, board.fen().split(" ")[0].replace("/", "-") + ".png")
        generate_board_image_with_background(board=board, 
                                             piece_set=piece_set, 
                                             background_img=board_img,
                                                size=512).save(file_name)

    # generate book boards
    piece_sets = list_directories_with_target(args.book_piece_sets, "wK.png")
    board_sets = list_directories_with_target(args.book_piece_sets, "sqLight.png")
    for _ in range(args.book_count):
        piece_set_dir = os.path.join(args.book_piece_sets,random.choice(piece_sets))
        piece_set = piece_set_from_dir(dir=piece_set_dir, piece_size=64)
        board_dir = os.path.join(args.book_piece_sets,random.choice(board_sets))
        light_sq, dark_sq = squares_from_dir(board_dir)
        board = random_board()
        file_name = os.path.join(args.output, board.fen().split(" ")[0].replace("/", "-") + ".png")
        generate_board_image_with_squares(board=board, 
                                            piece_set=piece_set, 
                                            light_sq_img=light_sq,
                                            dark_sq_img=dark_sq,
                                            square_size=64).save(file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--int_piece_sets', help='piece sets for internet directory', default="assets/internet-artifacts/piece", type=str)
    parser.add_argument('--int_boards',help='boards for internet directory', default="assets/internet-artifacts/board", type=str)
    parser.add_argument('--int_count',help='number of internet boards to generate', default=10, type=int)
    parser.add_argument('--book_piece_sets', help='piece sets for book directory', default="assets/book-artifacts", type=str)
    parser.add_argument('--book_count',help='number of book boards to generate', default=10, type=int)
    parser.add_argument('--output', help='output directory', type=str, default="output")
    args = parser.parse_args()

    main(args)