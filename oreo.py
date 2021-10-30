import cv2
import base64
import requests
from flask import Flask, request, Response, jsonify
app = Flask(__name__)
def init():
    imge1 = cv2.cv2.imread('O.png', cv2.IMREAD_UNCHANGED)  # 上半饼
    imge2_temp = cv2.imread('R.png', cv2.IMREAD_UNCHANGED)  # 馅要比饼小一点
    imge3 = cv2.imread('Ob.png', cv2.IMREAD_UNCHANGED)  # 下半饼
    imge_empty = cv2.imread('empty.png', cv2.IMREAD_UNCHANGED)  # 空白画布

    # 对馅进行处理，缩小到90%
    scale_percent = 90
    width = int(imge2_temp.shape[1] * scale_percent / 100)
    height = int(imge2_temp.shape[0] * scale_percent / 100)
    imge2 = cv2.resize(imge2_temp, (width, height), interpolation=cv2.INTER_AREA)
    return imge1, imge2, imge3, imge_empty


#  画布增加
def png_extend(img, px):
    imgb = cv2.copyMakeBorder(img, px, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])  # 增加有颜色的像素，这里为白色
    b_channel, g_channel, r_channel, alpha_channel = cv2.split(imgb)  # 分离4个通道（RGB和Alpha）
    alpha_channel[:px, :] = 0  # 把有颜色的像素变透明
    return imgb


def add_t(imgb):
    img1, img2, img3, img_empty = init()
    roi = imgb[0:410, 0:600]
    img1gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img1gray, 253, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    img4_bg = cv2.bitwise_and(roi, roi, mask=mask)
    img1_fg = cv2.bitwise_and(img1, img1, mask=mask_inv)
    dst = cv2.add(img4_bg, img1_fg)
    imgb[0:410, 0:600] = dst
    return imgb


def add_re(imgb):
    img1, img2, img3, img_empty = init()
    roi = imgb[0:369, 30:570]
    regray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(regray, 253, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    imgb_bg = cv2.bitwise_and(roi, roi, mask=mask)
    re_fg = cv2.bitwise_and(img2, img2, mask=mask_inv)
    dst = cv2.add(imgb_bg, re_fg)
    imgb[0:369, 30:570] = dst
    return imgb


def add_b(imgb):
    img1, img2, img3, img_empty = init()
    roi = imgb[0:410, 0:600]
    img1gray = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img1gray, 253, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    img4_bg = cv2.bitwise_and(roi, roi, mask=mask)
    img1_fg = cv2.bitwise_and(img3, img3, mask=mask_inv)
    dst = cv2.add(img4_bg, img1_fg)
    imgb[0:410, 0:600] = dst
    return imgb


def draw(name):
    img1, img2, img3, img_empty = init()
    if name[-1] == '奥':
        cv2.imwrite('img4.png', img3)
    else:
        img4 = add_re(img_empty)
        cv2.imwrite('img4.png', img4)
    img4 = cv2.imread('img4.png', cv2.IMREAD_UNCHANGED)
    for i in range(0, len(name) - 2):
        if (name[len(name) - i - 1] == '奥') & (name[len(name) - i - 2] == '利'):
            """底+馅要拓展40像素"""
            imgt = png_extend(img4, 40)
            img4 = add_re(imgt)
        elif (name[len(name) - i - 1] == '利') & (name[len(name) - i - 2] == '利'):
            """馅+馅要拓展60像素"""
            img4 = png_extend(img4, 60)
            img4 = add_re(img4)
        elif (name[len(name) - i - 1] == '利') & (name[len(name) - i - 2] == '奥'):
            """馅+底/顶要拓展84像素"""
            img4 = png_extend(img4, 84)
            img4 = add_b(img4)
        elif (name[len(name) - i - 1] == '奥') & (name[len(name) - i - 2] == '奥'):
            """底+底/顶要拓展84像素"""
            img4 = png_extend(img4, 64)
            img4 = add_b(img4)
    if (name[0] == '奥') & (name[1] == '利'):
        img4 = png_extend(img4, 84)
        img4 = add_t(img4)
    elif (name[0] == '奥') & (name[1] == '奥'):
        img4 = png_extend(img4, 64)
        img4 = add_t(img4)
    elif (name[0] == '利') & (name[1] == '奥'):
        imgt = png_extend(img4, 40)
        img4 = add_re(imgt)
    elif (name[0] == '利') & (name[1] == '利'):
        img4 = png_extend(img4, 60)
        img4 = add_re(img4)
    cv2.imwrite('oreo.png', img4)
    # cv2.imshow('image', img4)
    # cv2.waitKey(0)  # 几秒内检测到键盘输入会继续，0为一直检测
    # cv2.destroyAllWindows()


@app.route('/oreo', methods=["GET"])
def post_data():
    name = request.args.get('name')
    draw(name)
    pic = open("oreo.png", "rb")
    pic_base64 = base64.b64encode(pic.read())
    pic.close()
    return pic_base64


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, host='127.0.0.1', port=9100)  # 此处的 host和 port对应上面 yml文件的设置

