import torchvision.transforms.functional as F
from PIL import Image


class ConvertToBGR(object):
    """
    Converts a PIL image from RGB to BGR
    """

    def __init__(self):
        pass

    def __call__(self, img):
        r, g, b = img.split()
        img = Image.merge("RGB", (b, g, r))
        return img

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class Multiplier(object):
    def __init__(self, multiple):
        self.multiple = multiple

    def __call__(self, img):
        return img*self.multiple

    def __repr__(self):
        return "{}(multiple={})".format(self.__class__.__name__, self.multiple)