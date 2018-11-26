# coding: utf-8

import os
import sys
import requests
import tempfile

from PIL import Image


def make_image(content, convert=True):
    '''由图片二进制内容生成Image对像'''
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.write(content)
    tmpfile.close()
    im = None
    try:
        im = Image.open(tmpfile.name)
        if convert:
            im = im.convert('RGB')
    except IOError:
        os.remove(tmpfile.name)
        return
    os.remove(tmpfile.name)
    return im


# 将图片调整为方图
def image_adjust_size(img, size):
    rw, rh = size
    width, height = img.size

    if width == height:
        background = img.resize(size, Image.ANTIALIAS)
    else:
        if height > width:
            scale = 1.0 * height / rh
            resize_width = int(width / scale)
            resize = (resize_width, img.height)
            x = max(0, int((rw - resize_width) / 2))
            pos = (x, 0)
        else:
            scale = 1.0 * width / rw
            resize_height = int(height / scale)
            resize = (rh, resize_height)
            pos = (0, 0)

        img = img.resize(resize, Image.ANTIALIAS)

        background = Image.new('RGBA', size, (255, 255, 255, 0))
        background.paste(img, pos)

    return background


# 汉明路径小于5就认为是相似的图片
def haming_distance(h1, h2):
    count, h = 0, h1 ^ h2
    while h:
        count += 1
        h &= h - 1
    return count


def avhash(im):
    im = image_adjust_size(im, (8, 8)).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 64
    binarization_array = map(lambda x : 0 if x < avg else 1, im.getdata())
    return reduce(lambda x, (y, z): x | (z << y), enumerate(binarization_array), 0)


def get_image(url):
    r = requests.get(url)
    im = make_image(r.content)
    return im


def is_similar(h1, h2):
    return haming_distance(h1, h2) <= 5


def main():
    urls = [
        # 'https://img.alicdn.com/i3/2958736721/TB2ASr6X.sIL1JjSZPiXXXKmpXa_!!2958736721.jpg',
        # 'https://img.alicdn.com/i2/694648303/TB2mE8OgbsTMeJjy1zbXXchlVXa_!!694648303.jpg',
        # 'https://img.alicdn.com/i4/694648303/TB2d6T.XQ.HL1JjSZFuXXX8dXXa_!!694648303.jpg',
        # 'http://gd2.alicdn.com/imgextra/i2/2578199548/TB2GY_4g7OWBuNjSsppXXXPgpXa_!!2578199548.png',
        # 'https://img.alicdn.com/i4/2578199548/TB2gD2GdVmWBuNjSspdXXbugXXa_!!2578199548.jpg'
        'https://img.alicdn.com/i1/2453138172/O1CN012AEp768qkDehrRr_!!2453138172.jpg',
        'https://img.alicdn.com/i2/2453138172/O1CN012AEp7AV27AIcvQz_!!2453138172.jpg'
    ]

    for url in urls:
        im = get_image(url)
        h = avhash(im)
        for u in urls:
            if url == u:
                continue
            im1 = get_image(u)
            h1 = avhash(im1)
            print 'h: %s, h1: %s, haming: %s, is is_similar: %s' % (h, h1, haming_distance(h, h1), is_similar(h, h1))


if __name__ == '__main__':
    main()
