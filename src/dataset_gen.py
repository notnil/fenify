import chess
import random
import os
import io
from PIL import Image
import cairosvg

def piece_set_from_dir(dir: str, suffix: str = ".png", piece_size: int=64) -> dict[chess.Piece, Image.Image]:
    """Return a dictionary of piece images from the given directory.  Expects the file names to be in the format wK.png, wQ.png, etc.  Supported suffixes are .png and .svg."""
    piece_set = {}
    for piece_type in chess.PIECE_TYPES:
        for color in [chess.WHITE, chess.BLACK]:
            piece = chess.Piece(piece_type, color)

            color_char = "w" if color == chess.WHITE else "b"
            file_name = os.path.join(dir, color_char + chess.piece_symbol(piece_type=piece_type).upper() + suffix)
            if not os.path.exists(file_name):
                raise Exception(f"File {file_name} does not exist")
            img = None
            if suffix == ".svg":
                piece_bytes = cairosvg.svg2png(url=file_name, output_height=piece_size, output_width=piece_size, background_color=None)
                img = Image.open(io.BytesIO(piece_bytes)).convert("RGBA")
            elif suffix == ".png":
                img = Image.open(file_name).convert("RGBA").resize((piece_size, piece_size))
            piece_set[piece] = img
    return piece_set

def squares_from_dir(dir: str) -> tuple[Image.Image, Image.Image]:
    """Return a tuple of light and dark square images from the given directory. Expects the file names sqLight.png and sqDark.png."""
    light_sq = Image.open(os.path.join(dir, "sqLight.png"))
    dark_sq = Image.open(os.path.join(dir, "sqDark.png"))
    return light_sq, dark_sq

def random_board(rand: random.Random = random) -> chess.Board:
    """Create a board with a random piece (including no piece) of equal probability on each square.  A random seed can be provided."""
    board = chess.Board(None)
    options = [chess.Piece(piece_type=piece_type, color=color) 
                                for piece_type in chess.PIECE_TYPES 
                                for color in [chess.WHITE, chess.BLACK]]
    options.append(None)
    for sq in chess.SQUARES:
        piece = rand.choice(options)
        board.set_piece_at(sq, piece)
    return board

def generate_board_image_with_background(board: chess.Board, 
                                         piece_set: dict[chess.Piece,Image.Image], 
                                         background_img: Image.Image,
                                         size: int = 512) -> Image.Image:
    """Generate an image of a board with the given piece set.  The background image is resized to the given size and the pieces are placed on top."""
    board_img = background_img.resize((size, size)).convert("RGBA")
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        piece_img = piece_set[piece].convert("RGBA").resize((size//8, size//8))
        col = chess.square_file(sq)
        row = chess.square_rank(sq)
        board_img.alpha_composite(piece_img, dest=(col * size//8, (7-row) * size//8))
    return board_img

def generate_board_image_with_squares(board: chess.Board, 
                                    piece_set: dict[chess.Piece,Image.Image],
                                    square_size: int, 
                                    light_sq_img: Image.Image, 
                                    dark_sq_img: Image.Image) -> Image.Image:
    """Generate an image of a board with the given piece set.  The square size is the size of each square in pixels.  
    The light and dark square images are composed in a grid to form the squares."""

    # Create new image with correct size
    board_image = Image.new('RGB', (square_size * 8, square_size * 8))
    # Iterate over all squares
    for square in chess.SQUARES:
        rank = square // 8
        file = square % 8
        piece = board.piece_at(square)
        
        # Choose correct square color
        square_image = None
        if (rank + file) % 2 == 0:
            square_image = dark_sq_img
        else:
            square_image = light_sq_img
        square_image = square_image.resize((square_size, square_size))

        # If piece exists, draw it on square
        if piece is not None:
            piece_image = piece_set[piece]
            piece_image = piece_image.resize((square_size, square_size))
            square_image.paste(piece_image, (0, 0), piece_image)

        # Paste square into correct position
        board_image.paste(square_image, (file*square_size, (7-rank)*square_size))

    return board_image