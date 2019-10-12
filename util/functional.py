from numpy import linalg
import numpy as np


def cos_distance(vector1: np.ndarray, vector2: np.ndarray):
    """
    cos距离，会归一化，输出未0~1，越大越相似
    :param vector1:
    :param vector2:
    :return:
    """
    value = np.dot(vector1.T, vector2)/ (linalg.norm(vector1) * linalg.norm(vector2))
    score = 0.5 + 0.5 * float(value)
    return score
