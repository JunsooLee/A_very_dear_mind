# 애지중지(愛䙙重䙙)
가천대학교 소프트웨어학과 졸업작품 2분반<br/>
양한진, 이준수, 황병훈

### Motivation
1. Most of us do not tend to pay attention to the care symbols on the label of clothes.
2. Also, the laundry method varies according to type of clothes.
3. So we have experienced unwanted results like shrunken, being discolored or being damaged clothes by wrong laundry method.
4. This unwanted result can not be compensation by company

### Purpose
* **Provide service that people can know laundry method easily**

### System overview
**In Sequence**<br/>
<img src="./WIKI/proposal4.png" width="400"></img>
<br/>**Structure**<br/>
<img src="./WIKI/proposal6.png" width="400"></img> 

### Description
This program recognize care symbols in tag by image processing and Yolo v2.<br/>
Users can know laundry method of user's clothes easily by just taking a picture of care tag<br/>
<br/>
The following information can be displayed.
<br/>

* Recognized symbols
* Standard of symbols
* informaion about symbol

<img src="./WIKI/proposal5.png" width="50%"></img>
<br/><br/>

### Using Technology
1. Image processing<br/>
<img src="./WIKI/proposal7.png" width="50%"></img><br/>
* System processes image to recognize care tag which is bad quality or wrinkled
2. Image Detecting<br/>
<img src="./WIKI/proposal4.png" width="50%"></img><br/>
* System recognizes symbols in processed image of care tag
