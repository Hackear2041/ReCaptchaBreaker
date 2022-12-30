from transformers import AutoModel, AutoProcessor, AutoConfig
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
import os

from .utils import download_image, get_borders
from .constants import label_texts, flex_thresh, NUM_LABELS

from typing import Tuple, List



class CustomModel(torch.nn.Module):

    def __init__(self, model):
        super().__init__()

        self.image_model = model.vision_model
        self.proj1 = model.visual_projection
        self.fc = nn.Linear(512, NUM_LABELS, bias = False)
        self.criterion = torch.nn.CrossEntropyLoss()
    
    def forward(self, images, labels = None):
        logits = self.proj1(self.image_model(images).pooler_output)
        logits = self.fc(logits)

        if labels is not None:
            loss = self.criterion(logits, labels)
        else:
            loss = None
        output = (logits,)
        return ((loss,) + output) if loss is not None else output

def get_model() -> Tuple[AutoModel, AutoProcessor]:
    # TODO: Load directly from checkpoint
    config = AutoConfig.from_pretrained("openai/clip-vit-base-patch32")
    model = AutoModel.from_config(config)
    feature_extractor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

    model = CustomModel(model)
    model.load_state_dict(torch.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model.bin'), map_location = 'cpu'))
    return model, feature_extractor

def predict_images(images : List[Image.Image], model, feature_extractor, returnDict = False
) -> torch.tensor:
    images = torch.tensor(np.array(feature_extractor(images = images).pixel_values))
    outs =  model(images = images)[0]

    if returnDict:
        # Returns a list of dictionary based on lbael_texts
        outs = outs.detach().numpy()
        outs = [dict(zip(label_texts, out)) for out in outs]
        return outs
    else:
        return outs


def predict_squares(model, feature_extractor, url, grid_size, label, min_preds = 3, border = 0.1, returnImages = False):
    l = int(grid_size**0.5)
    
    img = download_image(url)
    img = np.array(img)
    boxes = set()
    h = img.shape[0]
    w = img.shape[1]
    ims_pil = []
    for i in range(l ** 2):
        x1, x2, y1, y2 = get_borders(i // l, i % l, h, w, l, border = border)
        ims_pil.append(Image.fromarray(img[y1:y2, x1:x2]))
    outs = predict_images(ims_pil, model, feature_extractor)
    l_idx = label_texts.index(label)
    scores = outs[:, l_idx]
    print(scores)
    for i,s in enumerate(scores):
        if s > flex_thresh[label]:
            boxes.add(i)
    if len(boxes) < min_preds:
        for x in torch.topk(scores, k = min_preds).indices:
            boxes.add(x.item()) 
    if returnImages:
        return list(boxes), ims_pil
    else:
        return list(boxes)

