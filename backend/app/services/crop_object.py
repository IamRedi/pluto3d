def crop_object(image, box):

    x1, y1, x2, y2 = box

    return image[y1:y2, x1:x2]