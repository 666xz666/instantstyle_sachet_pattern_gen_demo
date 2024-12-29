import cv2
import numpy as np
from config import *
import random
from PIL import Image

def img_to_cv2_img(pil_image):
    """
    将Pillow的Image对象转换为OpenCV的图像格式。

    参数:
    pil_image (PIL.Image): Pillow的Image对象。

    返回:
    numpy.ndarray: OpenCV格式的图像。
    """
    # 将Pillow Image对象转换为NumPy数组
    numpy_image = np.array(pil_image)

    # 如果图像是RGBA，去掉alpha通道
    if numpy_image.shape[2] == 4:
        numpy_image = numpy_image[:, :, :3]

    # 将RGB转换为BGR，因为OpenCV期待的是BGR格式
    cv2_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

    return cv2_image

def cv2_img_to_pil_image(cv2_image):
    """
    将OpenCV的图像格式转换为Pillow的Image对象。

    参数:
    cv2_image (numpy.ndarray): OpenCV格式的图像。
    """
    cv2_image = cv2_image.astype(np.uint8)

    return Image.fromarray(cv2_image)



def save_img(pil_image):
    sd2 = random.randint(1, 114514)
    pil_image.save(OUTPUT_PATH + "result_" + str(sd2) + ".png")
    print("result saved to", OUTPUT_PATH + "result_" + str(sd2) + ".png")