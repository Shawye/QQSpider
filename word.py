from os import path
from scipy.misc import imread
import matplotlib.pyplot as plt
import codecs
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

__basePath = './word'
__fileNamePath = u'./analyze/'
__stopWordPath = u'./word/stopwords.txt'
__imagePath = u'./word/bg.jpg'
__ttfPath = u'./word/SourceHanSans-Regular.otf'


def ReadFile(filePath, encoding="utf-8"):
    with codecs.open(filePath, "r", encoding) as f:
        return f.read()


def WriteFile(filePath, u, encoding="gbk"):
    with codecs.open(filePath, "w", encoding) as f:
        f.write(u)


def UTF8_2_GBK(src, dst):
    content = ReadFile(src, encoding="utf-8")
    WriteFile(dst, content, encoding="gbk")



if __name__ == '__main__':
    d = path.dirname(__file__)
    # UTF8_2_GBK(__fileNamePathO, __fileNamePathN)
    # Read the whole text.
    text = open(path.join(d, __fileNamePath), encoding='utf-8').read()

    # read the mask / color image
    # taken from http://jirkavinse.deviantart.com/art/quot-Real-Life-quot-Alice-282261010
    alice_coloring = imread(path.join(d, __imagePath))

    wc = WordCloud(background_color="black", max_words=2000, mask=alice_coloring,
               stopwords=STOPWORDS.add("said"),
               max_font_size=40, random_state=42, font_path=__ttfPath)
    # generate word cloud
    wc.generate(text)

    # create coloring from image
    image_colors = ImageColorGenerator(alice_coloring)

    # show
    # plt.imshow(wc)
    # plt.axis("off")
    # plt.show()
    # recolor wordcloud and show
    # we could also give color_func=image_colors directly in the constructor
    plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis("off")
    plt.show()
    # plt.imshow(alice_coloring, cmap=plt.cm.gray)
    # plt.axis("off")
    # plt.show()