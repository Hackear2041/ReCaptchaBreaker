label_texts =  sorted(["vehicle", "traffic light", "tractor", "stairs", "motorcycle", "fire hydrant", "crosswalks", "chimney", "bus", "bicycle", "car", "bridge", "boat", "palm", "mountain", "taxi", "parking meter"])
NUM_LABELS = len(label_texts)
# TODO: We may want to change this
flex_thresh = {l:0 for l in label_texts}
