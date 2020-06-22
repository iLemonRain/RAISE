import steganography as steg
from PIL import Image

plain_data = ""
with open('原.txt', 'r', encoding='utf-8') as f:
    plain_data = f.read()

steg.encodeDataInImage(Image.open("coffee.png").convert('RGBA'), plain_data).save('encodeImage.png')
print(steg.decodeImage(Image.open("encodeImage.png")))
