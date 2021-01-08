from PIL import Image
import numpy as np
import cv2
import os


def mask_3d_255(img_root):
    # up-cloth = 4 -> 255
    img = Image.open(img_root)
    # img = img.resize((192, 256)) # resize for training
    model_cut = np.asarray(img)
    b = (model_cut == 4)
    c = b.astype(int)
    c[c == 1] = 255
    path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_warped_mask/'
    name = path + "model_cut.png"
    cv2.imwrite(name, c)
    return name


def edge_255(img_root, output_path):
    print(img_root)
    image = cv2.imread(img_root)
    mask = np.zeros(image.shape[:2], dtype="uint8")
    rect = (1, 1, mask.shape[1], mask.shape[0])
    # 알고리즘 수행중 활용할 메모리
    fgModel = np.zeros((1, 65), dtype="float")
    bgModel = np.zeros((1, 65), dtype="float")
    # 입력 이미지, 채널의 모든 요소가 0인 마스크, 사각형 영역, 메모리, 메모리, 알고리즘 반복 횟수, 사각형 영역 지정을 통한
    # GrabCut일 경우 cv2.GC_INIT_WITH_RECT로 설정
    (mask, bgModel, fgModel) = cv2.grabCut(image, mask, rect, bgModel,
                                            fgModel, iterCount=10, mode=cv2.GC_INIT_WITH_RECT)
    outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1)
    outputMask = (outputMask * 255).astype("uint8")  # 검은색 배경
    cv2.imwrite(output_path, outputMask)
