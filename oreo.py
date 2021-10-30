import cv2


def init():  # 将加载本地图片作为函数封装起来，以便后续作为模块使用
    imge1 = cv2.cv2.imread('O.png', cv2.IMREAD_UNCHANGED)  # 上半饼
    imge2_temp = cv2.imread('R.png', cv2.IMREAD_UNCHANGED)  # 暂时的馅，后续要做缩小处理
    imge3 = cv2.imread('Ob.png', cv2.IMREAD_UNCHANGED)  # 下半饼

    # 空白画布，在最底层为馅的时候要用
    imge_empty = cv2.imread('empty.png', cv2.IMREAD_UNCHANGED)

    # 对馅进行处理，缩小到90%，毕竟总不能馅和饼一样大
    scale_percent = 90
    width = int(imge2_temp.shape[1] * scale_percent / 100)
    height = int(imge2_temp.shape[0] * scale_percent / 100)
    imge2 = cv2.resize(imge2_temp, (width, height), interpolation=cv2.INTER_AREA)
    return imge1, imge2, imge3, imge_empty  # 将上半饼，缩小的馅，下半饼以及空白画布作为对象返回


#  画布增加（为了让图片能叠加，和ps一个道理）
def png_extend(img, px):
    # 增加有颜色的像素，value的3个值代表RGB，随便啥都行（反正后续要变成透明），这里为白色
    imgb = cv2.copyMakeBorder(img, px, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    # 分离4个通道（R，G，B和Alpha（透明度））（虽然平时念RGB比较习惯，不过在opencv里面顺序变成BGR了）
    b_channel, g_channel, r_channel, alpha_channel = cv2.split(imgb)
    alpha_channel[:px, :] = 0  # 把有颜色的像素变透明
    return imgb  # 处理完的画布作为整体返回


def add_t(imgb):  # 增加上半饼，只在要叠加最上面一层的时候使用
    img1, img2, img3, img_empty = init()  # 初始化本地图片
    roi = imgb[0:410, 0:600]  # 设置要叠加的区域

    # 下面的步骤为opencv中教科书般的“按位运算”操作，和百度能找到的教程几乎一样
    img1gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    # 这里的第二个参数253不是唯一可用的值，可在255以内随意尝试
    # 不过太低会导致图像识别差异过大，我试过的最低大概是248左右
    ret, mask = cv2.threshold(img1gray, 253, 255, cv2.THRESH_BINARY)

    mask_inv = cv2.bitwise_not(mask)
    img4_bg = cv2.bitwise_and(roi, roi, mask=mask)
    img1_fg = cv2.bitwise_and(img1, img1, mask=mask_inv)
    dst = cv2.add(img4_bg, img1_fg)
    imgb[0:410, 0:600] = dst
    return imgb  # 处理完的画布作为整体返回


def add_re(imgb):  # 注释同函数add_t
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


def add_b(imgb):  # 注释同函数add_t
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


def draw(name):  # 这里传进来的的name是你定义的奥利奥字段，如“奥利奥奥利利利奥”
    # 预处理
    img1, img2, img3, img_empty = init()
    if name[-1] == '奥':  # 如果最底层是“奥”，则直接用下半饼作为基础画布
        cv2.imwrite('img4.png', img3)
    else:  # 如果最底层是“利”，则要在空白画布上附加缩小后的馅，再作为基础画布，以便后续图片宽度不变
        img4 = add_re(img_empty)
        cv2.imwrite('img4.png', img4)
    img4 = cv2.imread('img4.png', cv2.IMREAD_UNCHANGED)  # img4就是我们的基础画布了

    # 对除去顶层以外的部分进行叠图（因为顶层有可能要叠上半饼，所以后续拉出来单独处理）
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
            """底+底/顶要拓展64像素"""
            img4 = png_extend(img4, 64)
            img4 = add_b(img4)

    # 对顶层单独处理
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
    cv2.imwrite('oreo.png', img4)  # 将最终图像保存为oreo.png
    # 以下被注释的代码用来临时调试使用，可将最终图片自动展示出来，不用手动点开图片查看
    # cv2.imshow('image', img4)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
