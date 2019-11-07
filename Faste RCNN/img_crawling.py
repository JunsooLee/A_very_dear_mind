from google_images_download import google_images_download
from PIL import Image
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context

###
# @brief 구글 크롤링
# @param keyword 크롤링 할 단어
# @param dir 크롤링 데이터 저장 공간 경로
###
def imageCrawling(keyword, dir):
    response = google_images_download.googleimagesdownload()

    arguments = {"keywords": keyword,
                 "limit": 200,
                 "print_urls": True,
                 "no_directory": True,
                 'output_directory': dir,
                 "chromedriver": "C:/Users/user/Downloads/chromedriver_win32/chromedriver.exe"
                 }
    paths = response.download(arguments)
    print(paths)

###
# @brief 크롤링한 파일 open 여부 판단
###
def img_delete():
    img_dir = r"C:/Users/user/Desktop/dataset"
    for filename in os.listdir(img_dir):
        try:
            with Image.open(img_dir + '/' + filename) as im:
                print("ok")
        except:
            print(img_dir + "/" + filename)
            os.remove(img_dir + "/" + filename)

###
# @brief 파일 확장자 check jpg & png 만 남겨놓음
###
def img_check():

    img_dir = r"C:/Users/user/Desktop/dataset/"
    for filename in os.listdir(img_dir):
        fileExtension = os.path.splitext(img_dir+filename)[1]
        if fileExtension == '.jpg' or fileExtension == '.png':
            print("check")
        else:
            os.remove(img_dir + filename)


if __name__ == '__main__':
    imageCrawling('care tag jpg', "C:/Users/user/Pictures/pic/")
    img_delete()
    # img_check()