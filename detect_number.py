from PIL import Image
import numpy as np
from cnocr import CnOcr

ocr_model = CnOcr(rec_model_name='en_number_mobile_v2.0')

# cnocr drops the end of a line that reaches close to the right edge: a held
# balance of '633,103 k' came back as '633,1', so the bot valued 633 m of
# silver at 6,331. Widening the crop is not enough, the model needs blank space
# around the text. Sideways only: padding above and below makes it worse.
HORIZONTAL_PAD = 20


def prepare(img):
    """Pad and enlarge a crop the way the recognizer wants to see it."""
    (w, h) = img.size

    background = int(np.median(np.array(img)))
    padded = Image.new('L', (w + 2 * HORIZONTAL_PAD, h), background)
    padded.paste(img.convert('L'), (HORIZONTAL_PAD, 0))

    return np.array(padded.resize((padded.width * 3, padded.height * 3), Image.BICUBIC))


def detect_number(img):

    text = ocr_model.ocr_for_single_line(prepare(img))['text']

    dictionary = {' ':'', ',':'', 'k':'000', 'm':'000000'} 
    for key in dictionary.keys():
        text = text.lower().replace(key, dictionary[key])

    # print(text)

    try:
        # A reading that differed from the last one by more than 70 used to be
        # thrown away as a misread. That deadlocked the bot whenever the market
        # moved further than that between two reads: the remembered price only
        # updates on a successful read, so nothing was ever accepted again.
        # get_info now requires two identical readings in a row instead.
        return int(''.join(i for i in text if i.isdigit()))

    except ValueError:
        return 0
    
    

