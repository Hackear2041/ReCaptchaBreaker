import time
from .model import get_model, predict_squares
from .utils import captcha_label_to_text, download_image
from .constants import label_texts, flex_thresh
import torch
import numpy as np
from typing import List
from PIL import Image
import requests
import os
from tqdm import tqdm
class ReCaptchaBreaker:

    def print(self, *args, **kwargs):
        if self.verbose: print(*args, **kwargs)


    def __init__(self, driver = None, verbose = False):
        self.driver = driver
        self.verbose = verbose
        self.package_path = os.path.dirname(os.path.abspath(__file__))
        self.load_model()

    def get_captcha_box(self, driver = None):
        if driver is None: driver = self.driver
        driver.switch_to.default_content()
        cand_captchas = driver.find_elements_by_tag_name('iframe')
        cand_captcha = None
        for captcha in cand_captchas:
            try:
                if captcha.get_attribute('title') == 'reCAPTCHA':
                    cand_captcha = captcha
                    break
            except: continue
        if cand_captcha is None:
            self.print('No recaptcha found :(')
            return None
        else:
            self.print('Captcha Found, Lets Go!!!')
        return cand_captcha
    
    def get_captcha_challenge_dialog(self, driver = None):
        if driver is None: driver = self.driver
        driver.switch_to.default_content()
        cand_captchas = driver.find_elements_by_tag_name('iframe')
        img_select_iframe = None
        for captcha in cand_captchas[::-1]:
            try:
                if captcha.get_attribute('title').find('recaptcha challenge') != -1:
                    img_select_iframe = captcha
                    break
            except: continue
        if img_select_iframe is None:
            self.print('Some unexpected error')
        else:
            self.print('Switching Frames!!!')
        return img_select_iframe
        
    def get_frame_metadata(driver):
        '''
            Returns the metadata of the image frame:
            1. Question Text
            2. All Tiles
            3. Image Link
            4. Verify Button
            Assume, we have switched to the image frame
        '''
        question_text = driver.find_element_by_tag_name('div').text.strip()
        all_tiles = driver.find_elements_by_tag_name('td')
        img_link = driver.find_element_by_tag_name('img').get_attribute('src')
        verify_btn = driver.find_elements_by_tag_name('button')[-1]
        return question_text, all_tiles, img_link, verify_btn

    def __captcha_box_click__(self, cand_captcha, timegap = 0.5):
        while True:
            try:
                cand_captcha.click()
                return
            except:
                self.print('Captcha clicked, but error occured. Trying again in {} seconds'.format(timegap))
                time.sleep(timegap)

    def __check_solve__(self, driver, verify_btn, ):
        if verify_btn.text.lower().find('verify') == -1:
            # We solved it once, but we need to continue
            verify_btn.click()
            time.sleep(3)
            return False
        else:
            verify_btn.click()
            time.sleep(3)
            # Check if our choice was correct
            cand_captcha = self.get_captcha_box(driver)
            try:
                driver.switch_to.frame(cand_captcha)
                if driver.find_element_by_id('recaptcha-anchor').get_attribute('aria-checked') != 'false':
                    self.print('Captcha Hit Successfully')
                    driver.switch_to.default_content()
                    return True
                else:
                    self.print('New challenge popped up, we probably failed last time.')
                    driver.switch_to.default_content()
                    return False
            except Exception as e:
                self.print(e)
                driver.switch_to.default_content()
                self.print('New challenge popped up')
                return False

    def attempt_multiple_select(self, boxes, label, all_tiles, verify_btn):
        while len(boxes) != 0:
            # TODO: Find a better way to identify when new images are loaded
            time.sleep(2)
            new_boxes = []
            # label = captcha_label_to_text(question_text.splitlines()[1])
            l_idx = label_texts.index(label)
            for box in boxes:
                while all_tiles[box].get_attribute('outerHTML').find('rc-imageselect-dynamic-selected')!=-1:
                    print('Still Loading')
                    time.sleep(0.2)
                time.sleep(0.2)
                src_link = all_tiles[box].find_element_by_tag_name('img').get_attribute('src')
                im = download_image(src_link)
                outs = self.model(images = torch.tensor(np.array(self.feature_extractor(images = [im]).pixel_values)))[0][0]
                if outs[l_idx] > flex_thresh[label]:
                    new_boxes.append(box)
                    all_tiles[box].click()
            boxes = new_boxes
        verify_btn.click()


    def solve_images(self, images : List[Image.Image]) -> torch.tensor:
        images = torch.tensor(np.array(self.feature_extractor(images = images).pixel_values))
        return self.model(images = images)[0]


    def solve_captcha(self, driver = None, MAX_RETRIES = 10):
        if driver is None: driver = self.driver
        self.print('Solving Captcha')
        
        captcha_box = self.get_captcha_box(driver)
        if captcha_box is None:
            return False
        
        self.__captcha_box_click__(captcha_box)



        for _ in range(MAX_RETRIES):
            img_select_iframe = self.get_captcha_challenge_dialog(driver)
            driver.switch_to.frame(img_select_iframe)
            question_text, all_tiles, img_link, verify_btn = self.get_frame_metadata(driver)
            self.print('Question Text: ', question_text)
            self.print('Image Link: ', img_link)
            self.print('Number of Tiles: ', len(all_tiles))
            self.print('Solving Captcha')

            first_line = question_text.splitlines()[0].strip()
            GRID_SIZE = len(all_tiles)
            
            click_next = False
            if question_text.find('Click verify')!=-1 and question_text.find('none left') != -1:
                self.print('Multiple select')
            elif first_line.find('Select all images with') != -1:
                click_next = True
            elif first_line == 'Select all squares with':
                # Model generalizes poorly for this case
                click_next = True

            try:
                boxes, images = predict_squares(img_link, GRID_SIZE, captcha_label_to_text(question_text.splitlines()[1]), border = 0.02 if GRID_SIZE==16 else 0., returnImages = True)
            except Exception as e:
                self.print(e)
                return False

            for i, x in enumerate(all_tiles):
                if i in boxes:
                    x.click()

            
            if not click_next:
                self.attempt_multiple_select(boxes, captcha_label_to_text(question_text.splitlines()[1]), all_tiles, verify_btn)
                
            
            if self.__check_solve__(driver, verify_btn): return True

        return False


    def download_model(self,):
        link = 'https://github.com/Hackear2041/ReCaptchaBreaker/raw/main/src/model.bin'
        self.print('Downloading Model')
        # Beautiful downloader with progress bar

        r = requests.get(link, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        t=tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(os.path.join(self.package_path, 'model.bin'), 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
        if total_size != 0 and t.n != total_size:
            self.print('ERROR, something went wrong')
        self.print('Model Downloaded')


    def load_model(self, ):
        print(os.path.join(self.package_path, 'model.bin'))
        if not os.path.exists(os.path.join(self.package_path, 'model.bin')):
            self.download_model()
        self.model, self.feature_extractor = get_model() 
