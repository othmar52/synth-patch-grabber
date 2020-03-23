#!/bin/env python3
# -*- coding:utf-8 -*-

import cv2
import numpy as np
import argparse
import datetime

'''
    ------------------------------------------------------------------------------------------------------------
    This script inspects a MicroKORG's LCD display of a video and prints
    the currently displayed digits/letters with start second of video
    ------------------------------------------------------------------------------------------------------------

    Video : https://www.youtube.com/watch?v=UeiKJdvcync ("128 NEW microKorg patches" by Cuckoo [Nov 3, 2018])
    startsecond of interest: 394
    region of interest: frame[765:884, 1424:1697] pixels

    Many thanks to
        https://github.com/jiweibo/SSOCR
            as its the basis for this hacky script which is much faster than tesseract

        https://www.pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/
        https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/
        https://www.pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/
        https://medium.com/@basit.javed.awan/splitting-and-merging-image-channels-using-opencv-and-python-f3ba3d9ea0ae
        https://stackoverflow.com/questions/49048111/how-to-get-the-duration-of-video-using-cv2
        https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-set
        http://manpages.ubuntu.com/manpages/bionic/man1/tesseract.1.html
        https://www.unix-ag.uni-kl.de/~auerswal/ssocr/



    The purpose is to extract audio samples of each preset in as next step in another hacky script
    due to some invalid digit recognitions the result of this script has to be checked/corrected manually
    especially in the last part of the video where the LCD-display is partially hidden

'''

videoFilePath = "128 NEW microKorg patches-UeiKJdvcync.webm"

startSecond = 394

# region of interest [pixels]
roi_x1 = 1424
roi_y1 = 765
roi_x2 = 1697
roi_y2 = 884





# @see https://www.pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/
DIGITS_LOOKUP = {
    (1, 1, 1, 1, 1, 1, 0): 0,
    (1, 1, 0, 0, 0, 0, 0): 1,
    (1, 0, 1, 1, 0, 1, 1): 2,
    (1, 1, 1, 0, 0, 1, 1): 3,
    (1, 1, 0, 0, 1, 0, 1): 4,
    (1, 1, 0, 0, 0, 1, 1): 4,

    (0, 1, 1, 0, 1, 1, 1): 5,
    (0, 1, 1, 1, 1, 1, 1): 6,
    (1, 1, 0, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 8,

    (1, 1, 1, 0, 1, 1, 1): 9,
    (0, 0, 0, 0, 0, 1, 1): '-',
    (1, 1, 1, 1, 1, 0, 0): "P",
    (1, 1, 0, 1, 1, 1, 1): "A",
    (0, 1, 1, 1, 1, 0, 1): "B" # b
}
H_W_Ratio = 1.9
THRESHOLD = 35
arc_tan_theta = 6.0  # 数码管倾斜角度



parser = argparse.ArgumentParser()
#parser.add_argument('image_path', help='path to image')
parser.add_argument('-s', '--show_image', action='store_const', const=True, help='whether to show image')
parser.add_argument('-d', '--is_debug', action='store_const', const=True, help='True or False')


def preprocess(img, threshold, show=False, kernel_size=(5, 5)):
    # 直方图局部均衡化
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(6, 6))
    img = clahe.apply(img)
    # 自适应阈值二值化
    dst = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 127, threshold)
    # 闭运算开运算
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, kernel_size)
    dst = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, kernel)
    dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel)

    if show:
        cv2.imshow('equlizeHist', img)
        cv2.imshow('threshold', dst)
    return dst


def helper_extract(one_d_array, threshold=20):
    res = []
    flag = 0
    temp = 0
    for i in range(len(one_d_array)):
        if one_d_array[i] < 12 * 255:
            if flag > threshold:
                start = i - flag
                end = i
                temp = end
                if end - start > 20:
                    res.append((start, end))
            flag = 0
        else:
            flag += 1

    else:
        if flag > threshold:
            start = temp
            end = len(one_d_array)
            if end - start > 50:
                res.append((start, end))
    return res


def find_digits_positions(img, reserved_threshold=20):

    digits_positions = []
    img_array = np.sum(img, axis=0)
    horizon_position = helper_extract(img_array, threshold=reserved_threshold)
    img_array = np.sum(img, axis=1)
    vertical_position = helper_extract(img_array, threshold=reserved_threshold * 4)
    # make vertical_position has only one element
    if len(vertical_position) > 1:
        vertical_position = [(vertical_position[0][0], vertical_position[len(vertical_position) - 1][1])]
    for h in horizon_position:
        for v in vertical_position:
            digits_positions.append(list(zip(h, v)))
    assert len(digits_positions) > 0, "Failed to find digits's positions"

    return digits_positions


def recognize_digits_area_method(digits_positions, output_img, input_img):
    digits = []
    for c in digits_positions:
        x0, y0 = c[0]
        x1, y1 = c[1]
        roi = input_img[y0:y1, x0:x1]
        h, w = roi.shape
        suppose_W = max(1, int(h / H_W_Ratio))
        # 对1的情况单独识别
        if w < suppose_W / 2:
            x0 = x0 + w - suppose_W
            w = suppose_W
            roi = input_img[y0:y1, x0:x1]
        width = (max(int(w * 0.15), 1) + max(int(h * 0.15), 1)) // 2
        dhc = int(width * 0.8)
        # print('width :', width)
        # print('dhc :', dhc)

        small_delta = int(h / arc_tan_theta) // 4
        # print('small_delta : ', small_delta)
        segments = [
            ((w - width - small_delta, width // 2), (w, (h - dhc) // 2)),
            ((w - width - 2 * small_delta, (h + dhc) // 2), (w - small_delta, h - width // 2)),
            ((width - small_delta, h - width), (w - width - small_delta, h)),
            ((0, (h + dhc) // 2), (width, h - width // 2)),
            ((small_delta, width // 2), (small_delta + width, (h - dhc) // 2)),
            ((small_delta, 0), (w + small_delta, width)),
            ((width - small_delta, (h - dhc) // 2), (w - width - small_delta, (h + dhc) // 2))
        ]
        on = [0] * len(segments)

        for (i, ((xa, ya), (xb, yb))) in enumerate(segments):
            seg_roi = roi[ya:yb, xa:xb]
            # plt.imshow(seg_roi)
            # plt.show()
            total = cv2.countNonZero(seg_roi)
            area = (xb - xa) * (yb - ya) * 0.9
            print(total / float(area))
            if total / float(area) > 0.45:
                on[i] = 1

        # print(on)

        if tuple(on) in DIGITS_LOOKUP.keys():
            digit = DIGITS_LOOKUP[tuple(on)]
        else:
            digit = '*'
        digits.append(digit)
        cv2.rectangle(output_img, (x0, y0), (x1, y1), (0, 128, 0), 2)
        cv2.putText(output_img, str(digit), (x0 - 10, y0 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 128, 0), 2)

    return digits


def recognize_digits_line_method(digits_positions, output_img, input_img):
    digits = []
    for c in digits_positions:
        x0, y0 = c[0]
        x1, y1 = c[1]
        roi = input_img[y0:y1, x0:x1]
        h, w = roi.shape
        suppose_W = max(1, int(h / H_W_Ratio))

        # 消除无关符号干扰
        if x1 - x0 < 25 and cv2.countNonZero(roi) / ((y1 - y0) * (x1 - x0)) < 0.2:
            continue

        # 对1的情况单独识别
        if w < suppose_W / 2:
            x0 = max(x0 + w - suppose_W, 0)
            roi = input_img[y0:y1, x0:x1]
            w = roi.shape[1]

        center_y = h // 2
        quater_y_1 = h // 4
        quater_y_3 = quater_y_1 * 3
        center_x = w // 2
        line_width = 5  # line's width
        width = (max(int(w * 0.15), 1) + max(int(h * 0.15), 1)) // 2
        small_delta = int(h / arc_tan_theta) // 4
        segments = [
            ((w - 2 * width, quater_y_1 - line_width), (w, quater_y_1 + line_width)),
            ((w - 2 * width, quater_y_3 - line_width), (w, quater_y_3 + line_width)),
            ((center_x - line_width - small_delta, h - 2 * width), (center_x - small_delta + line_width, h)),
            ((0, quater_y_3 - line_width), (2 * width, quater_y_3 + line_width)),
            ((0, quater_y_1 - line_width), (2 * width, quater_y_1 + line_width)),
            ((center_x - line_width, 0), (center_x + line_width, 2 * width)),
            ((center_x - line_width, center_y - line_width), (center_x + line_width, center_y + line_width)),
        ]
        on = [0] * len(segments)

        for (i, ((xa, ya), (xb, yb))) in enumerate(segments):
            seg_roi = roi[ya:yb, xa:xb]
            # plt.imshow(seg_roi, 'gray')
            # plt.show()
            total = cv2.countNonZero(seg_roi)
            area = (xb - xa) * (yb - ya) * 0.9
            # print('prob: ', total / float(area))
            if total / float(area) > 0.25:
                on[i] = 1
        # print('encode: ', on)
        #print(tuple(on))
        if tuple(on) in DIGITS_LOOKUP.keys():
            digit = DIGITS_LOOKUP[tuple(on)]
        else:
            digit = '*'

        digits.append(digit)

        # 小数点的识别
        # print('dot signal: ',cv2.countNonZero(roi[h - int(3 * width / 4):h, w - int(3 * width / 4):w]) / (9 / 16 * width * width))
        if cv2.countNonZero(roi[h - int(3 * width / 4):h, w - int(3 * width / 4):w]) / (9. / 16 * width * width) > 0.65:
            digits.append('.')
            cv2.rectangle(output_img,
                          (x0 + w - int(3 * width / 4), y0 + h - int(3 * width / 4)),
                          (x1, y1), (0, 128, 0), 2)
            cv2.putText(output_img, 'dot',
                        (x0 + w - int(3 * width / 4), y0 + h - int(3 * width / 4) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 128, 0), 2)

        cv2.rectangle(output_img, (x0, y0), (x1, y1), (0, 128, 0), 2)
        cv2.putText(output_img, str(digit), (x0 + 3, y0 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 128, 0), 2)
    return digits


def main():
    args = parser.parse_args()
    cap = cv2.VideoCapture(videoFilePath)
    startRecognizingMilisecond = startSecond * 1000
    lastPersistedPatchName = ""
    while True:
        # This drives the program into an infinite loop.
        # Captures the video file frame-by-frame

        frame = cap.read()
        frame = frame[1]

        # check to see if we have reached the end of the stream
        if frame is None:
            print("no more frame")
            break

        if cap.get(cv2.CAP_PROP_POS_MSEC) < startRecognizingMilisecond:
            print("skip beginning of %s seconds" % startSecond)
            cap.set(cv2.CAP_PROP_POS_MSEC, startRecognizingMilisecond + 1)
            continue


        frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]
        blue, green, red = cv2.split(frame)
        lower_white = np.array([230,230,230])
        upper_white = np.array([255,255,255])
        fullred = cv2.merge((red,red,red))
        mask = cv2.inRange(fullred, lower_white, upper_white)
        mask = cv2.bitwise_not(mask)

        gray_img = mask
        h, w = gray_img.shape
        blurred = cv2.GaussianBlur(gray_img, (7, 7), 0)

        output = blurred
        dst = preprocess(blurred, THRESHOLD, show=args.show_image)
        try:
            digits_positions = find_digits_positions(dst)
        except AssertionError:
            continue
        digits = recognize_digits_line_method(digits_positions, output, dst)
        if args.show_image:
            cv2.imshow('output', output)
            cv2.waitKey()
            cv2.destroyAllWindows()
        patchName = ''.join(str(x) for x in digits).replace('.', '').strip('*')
        if lastPersistedPatchName != patchName:
            second = '{:06.2f}'.format(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            print(','.join([patchName, second, str(datetime.timedelta(seconds=float(second)))]))
            lastPersistedPatchName = patchName
        
        # bigger step (30 seconds) to next frame recognition for testing
        #cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) + 30000)


if __name__ == '__main__':
    main()
