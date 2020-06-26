# 👕👚 A very dear mind
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

- **Gachon Univ. Software department Graduation project**   
- **양한진, 이준수, 황병훈**

<img src = "https://user-images.githubusercontent.com/52238766/85866361-3cef9100-b802-11ea-9e1a-c80f5a43c97c.PNG"></img>


## 📄 General Outline for projects   


<img src="https://github.com/JunsooLee/A_very_dear_mind/blob/master/WIKI/outline.png" width="50%"></img>




## :point_right: Requirements

**1. Set up the python environment:**

  - Python = 3.6
  - torch = 1.2.0
  - torchVison = 0.4.0
  - OpenCV-python = 4.1.1.26
  - pillow = 6.2.1
  - vispy = 0.6.3
  - scipy = 1.1.0
  - minSdkVersion: 23
  - targetSdkVersion: 29
  - JAVA jdk: 1.8.0_241

  ```
  $ git clone https://github.com/JunsooLee/A_very_dear_mind.git
  $ conda create -n AVDM python=3.6
  $ conda activate AVDM
  $ pip install -r requirements.txt
  ```

## 💾 Download pretrain models

**1. We provide the pretrained models, which can be found at [here](https://drive.google.com/file/d/1qzQ0Uaw_r2T1iTZK2f7Icz7WhC9lObWl/view?usp=sharing).**
  - Make "checkpoints" folder in `$ROOT/training code/`.
  - Download the pretrained model and put it to `$ROOT/training code/checkpoints/fasterrcnn_11080821_94%.pth`.


## Testing

1. Test:
  - In `$ROOT/training code/`
    ```
    $ python demo.py --path ./test_image/test1.jpg
    ```
    
2. Result image
  - You can check the result image.
  <img src = "https://user-images.githubusercontent.com/52238766/85869073-26e3cf80-b806-11ea-9288-830b32acee8a.PNG"></img>

## YouTube Link
  - Only Korean Language Support 
  - We're planning to add English subtitles in the future.
  - https://youtu.be/jLvpi1dP_Mk


## ©️ License
```
 Copyright 2020 Team A very dear mind

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
```

