import urllib.request
from PIL import Image
from .constants import label_texts

def download_image(url, file = 'temp.png'):
    urllib.request.urlretrieve(url, file)
    return Image.open(file)

def get_borders(i, j, h, w, l, border = 0.1):
    y1 = int(i*h/l - border*h)
    y2 = int((i+1)*h/l + border*h)
    
    x1 = int(j*w/l - border * w) 
    x2 = int((j+1)*w/l + border * w)
    
    x1 = max(x1, 0)
    x2 = min(x2, w)
    
    y1 = max(y1, 0)
    y2 = min(y2, h)
    return x1, x2, y1, y2


def captcha_label_to_text(label):
    for l in label_texts:
        if label.find(l) != -1:
            return l