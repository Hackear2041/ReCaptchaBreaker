<div align="center">
    <h1> ReCaptaBreaker</h1>
    <p><i>Auto Solve Google's Recaptcha Image Challenge with near human performance!</i></p>
    <img src="https://img.shields.io/github/license/Hackear2041/ReCaptchaBreaker?style=for-the-badge">
    <a href="https://pypi.org/project/recaptchabreaker"><img src="https://img.shields.io/pypi/v/recaptchabreaker?style=for-the-badge"></a>
    <!-- <a href="https://github.com/QIN2DIM/recaptcha-challenger/"><img src="https://img.shields.io/github/stars/Hackear2041/ReCaptchaBreaker?style=for-the-badge"></a> -->
	<br>
	<br>
</div>

<!-- # ReCaptaBreaker - Auto Solve Google's Recaptcha Image Challenge with near human performance! -->

### This is one of the first library that breaks google recaptcha image challenge using autmoated system right in your device, with near human accuracy!


## Installing

You can use pypi distribution:
```shell
pip install recaptchabreaker
```
or install locally from source:
```shell
git clone https://github.com/Hackear2041/ReCaptchaBreaker.git
python setup.py install
```
Models will be downloaded on first use.

## Usage

1. You can use the solver in selenium based drivers 

```python
from recaptchabreaker import ReCaptchaBreaker
breaker = RecaptchBreaker() 

# Load the page, where recaptcha needs to be solved.
# The method will automatically find the captcha and solve it.
breaker.solve_captcha(driver)
```

2. You can directly classify on images as well

```python
from recaptchabreaker import ReCaptchaBreaker
breaker = RecaptchBreaker() 

# Load the list of images
image_list : List[PIL.Image] = ...

for pred in breaker.solve_images():
    print(pred) # Prints dictionary of label:score
```

## Hardware Requirements
Any device with python support and atleast 1GB RAM and 500MB free space should be supported. Expected classification time is ~1sec for 4*4 recaptcha Grid, and is dependent on number of CPU cores available. Faster Models Coming Soon!

## How it Works?

I train [Clip](https://huggingface.co/docs/transformers/model_doc/clip) model for classification and [Diffusion](https://huggingface.co/docs/diffusers/index) models for synthetic dataset generation. Further, using an iterative procedure, new annotated data points are collected by applying a week classifier to a real recaptcha system. The classifier model is further trained on the collected and augmented dataset resulting in a better classifier. The method is easily extendible to other forms of image captcha tasks such as hCaptcha. 

## Citing

If you find this repo useful, please consider citing the following paper:

```bibtex
@software{Anonymous_ReCaptchaBreaker_Breaking_Google_s_2022,
	author = {Anonymous},
	month = {12},
	title = {{ReCaptchaBreaker: Breaking Google's Recaptcha Image Challenge with near human performance}},
	url = {https://github.com/Hackear2041/ReCaptchaBreaker},
	version = {1.0.0},
	year = {2022}
}
``` 

## Disclaimer⚠️
 This repo is for educational and research purposes only. Any actions and/or activities related to the material contained on this repo is solely your responsibility. The misuse of the information in this repo can result in criminal charges brought against the persons in question. The author will not be held responsible in the event any criminal charges be brought against any individuals misusing the information in this repo to break the law. However, if you think this repo violates any of your terms of usage or policies, feel free to contact me.
