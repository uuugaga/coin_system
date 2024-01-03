from PIL import Image
import numpy as np
from cnocr import CnOcr

ocr_model = CnOcr(rec_model_name='en_number_mobile_v2.0')

def detect_number(img, average):

    (w, h) = img.size

    img = img.resize((w * 3, h * 3), Image.BICUBIC)

    img = np.array(img)

    text = ocr_model.ocr_for_single_line(img)['text']

    dictionary = {' ':'', ',':'', 'k':'000', 'm':'000000'} 
    for key in dictionary.keys():
        text = text.lower().replace(key, dictionary[key])

    # print(text)

    try:
        number = int(''.join(i for i in text if i.isdigit()))

        if average != 0 and abs(average - number) > 70:
            raise ValueError
        
        return number

    except ValueError:
        return 0
    
    

