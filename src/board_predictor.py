import chess
import torch
from torchvision import transforms
from dataclasses import dataclass
from PIL import Image

@dataclass
class BoardPrediction:
    board: chess.Board
    probabilities: torch.Tensor

class BoardPredictor:

    def __init__(self, model_path: str) -> None:
        self.model = torch.jit.load(model_path)    
        self.preprocessor = transforms.Compose([
            transforms.Grayscale(num_output_channels=3),
            transforms.Resize((300, 300)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, img: Image) -> BoardPrediction:
        img_tensor = self.preprocessor(img)
        img_batch = torch.unsqueeze(img_tensor, 0)
        y_hat = self.model(img_batch).data
        board = self._post_process(y_hat)
        return BoardPrediction(board, y_hat)

    def _post_process(self, y_hat: torch.Tensor) -> chess.Board:
        y_hat = torch.squeeze(y_hat)
        print(y_hat.shape)
        y_hat = torch.argmax(y_hat, dim=1)
        y_hat = torch.reshape(y_hat, (8, 8))
        a = y_hat.cpu().numpy()
        board = chess.Board()
        board.clear()
        for file in range(8):
            for rank in range(8):
                i = a[rank][file]
                if i == 0:
                    continue
                sq = (rank * 8) + file
                piece = self._piece_from_int(i)
                board.set_piece_at(sq, piece)
        return board

    def _piece_from_int(self, i):
        if i == 0:
            return None
        piece_type = ((i-1)%6)+1
        piece_color = chess.BLACK if i > 6 else chess.WHITE
        return chess.Piece(piece_type=piece_type, color=piece_color)