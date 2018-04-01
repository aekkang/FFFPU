"""
Given an image with a 3"x5" index card in (upper left) corner oriented
vertically, identifies the index card and warps the image so that the index
card is exactly rectangular.
"""
import cv2
import numpy as np

def process_image(fname):
    """
    Returns:
        :out_name str: filename of the processed image
        :invden float: inverse pixel density (inches per pixel width)
    """
    # load image and convert to grayscale
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # smooth
    smooth = cv2.medianBlur(gray, 33)

    # threshold
    ret, thresh = cv2.threshold(smooth, 185, 255, cv2.THRESH_BINARY)

    # erode-blur-blur-erode (some hacky magic shit)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.erode(thresh, kernel)
    thresh = cv2.blur(thresh, (32, 32))
    thresh = cv2.blur(thresh, (32, 32))
    kernel = np.ones((13, 13), np.uint8)
    thresh = cv2.erode(thresh, kernel)

    # identify contours and pick out the largest contour
    thresh = np.uint8(thresh)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contour_lens = [len(x) for x in contours]
    ix = np.argmax(contour_lens)
    contour = contours[ix]

    # approximate contour with polygon
    epsilon = 0.1 * cv2.arcLength(contour, True)  # max allowed dist from approximation to true
    approx = cv2.approxPolyDP(contour, epsilon, True)
    approx = approx[:, 0, :]
    print(approx.shape)

    # transform image
    height, width, _ = img.shape
    width /= 4
    width = int(width)
    height = 5 * width / 3  # aspect ratio of index card

    # arbitrarily select upper left corner for index card
    init_x, init_y = (200, 200)
    before = np.float32(approx)
    after = np.float32([[init_x, init_y], 
                        [init_x, init_y + height],
                        [init_x + width, init_y + height], 
                        [init_x + width, init_y]])
    print(after.shape)

    # perform transform
    # print('please give me my M')
    # M = cv2.getPerspectiveTransform(before, after)
    # print('*richard voice* YEyEYSYESSSSS')
    # img_copy = img.copy()
    # dst = cv2.warpPerspective(img_copy, M, tuple(list(img_copy.shape)[:2][::-1]), cv2.WARP_INVERSE_MAP)

    # # export results to file (appending '-transform' to fname)
    # out_name = ''.join(fname.split('.')[:-1]) + '-processed.jpg'
    # cv2.imwrite(out_name, dst)

    # calculate inches per pixel
    invden = 5. / height  # inches per pixel

    # return
    return (None, invden)

