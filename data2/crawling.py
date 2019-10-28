from google_images_download import google_images_download

import ssl
import os


ssl._create_default_https_context=ssl._create_unverified_context

def imageCrawling(keyword, dir):

    response = google_images_download.googleimagesdownload()

    arguments={ "keywords":keyword,
                "limit":100,
                "print_urls":True,
                "no_directory":True,
                'output_directory':dir}
    paths=response.download(arguments)
    print(paths)


    

imageCrawling('wash label',"C:\\Users\\ysurk\\Documents\\data")
