import argparse
from PIL import Image
from src.board_predictor import BoardPredictor

def main(args):
    # load model
    predictor = BoardPredictor(args.model)
    img = Image.open(args.image)
    prediction = predictor.predict(img)
    print(prediction)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inference')
    parser.add_argument('--model', help='model file path', type=str)
    parser.add_argument('--image',help='image file path', type=str)
    args = parser.parse_args()
    main(args)