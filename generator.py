import random

import torch
from diffusers import StableDiffusionPipeline, UniPCMultistepScheduler
from PIL import Image

from utils import *

from ip_adapter import IPAdapter
import cv2

from transformers import CLIPTextModelWithProjection, CLIPTokenizer

class Generator:
    tokenizer = None
    text_encoder = None
    ip_model = None
    pipe = None

    def load_models(self):
        print("Loading models...")
        base_model_path = r"D:\caches\huggingface\hub\models--runwayml--stable-diffusion-v1-5\snapshots\1d0c4ebf6ff58a5caecab40fa1406526bca4b5b9"
        image_encoder_path = "../models/image_encoder"
        ip_ckpt = "../models/ip-adapter_sd15.bin"
        device = "cuda"

        # load SDXL pipeline
        self.pipe = StableDiffusionPipeline.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16,
        )
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_vae_tiling()

        # load ip-adapter
        # target_blocks=["block"] for original IP-Adapter
        # target_blocks=["up_blocks.1"] for style blocks only (experimental, not obvious as SDXL)
        # target_blocks = ["down_blocks.2", "mid_block", "up_blocks.1"] # for style+layout blocks (experimental, not obvious as SDXL)
        self.ip_model = IPAdapter(self.pipe, image_encoder_path, ip_ckpt, device, target_blocks=["block"])

        self.text_encoder = CLIPTextModelWithProjection.from_pretrained("laion/CLIP-ViT-H-14-laion2B-s32B-b79K").to(
            self.pipe.device,
            dtype=self.pipe.dtype)
        self.tokenizer = CLIPTokenizer.from_pretrained("laion/CLIP-ViT-H-14-laion2B-s32B-b79K")
        print("Loaded models successfully")

    def __init__(self):
        self.load_models()

    def generate(self, content_img_obj, style_img_obj, keyword_list, neg_content_scale=0.8, steps=100, neg_list=None):
        # image = "assets/datasets/13.jpg"
        # image = Image.open(image)
        # image.resize((512, 512))

        #test
        # style_img_obj.show()
        # content_img_obj.show()

        image = content_img_obj

        # set negative content
        # neg_content = "a girl"
        # neg_content = None
        # neg_content_scale = 0.8

        if neg_list is not None:
            neg_content = ", ".join(neg_list)
        else:
            neg_content = None

        if neg_content is not None:

            tokens = self.tokenizer([neg_content], return_tensors='pt').to(self.pipe.device)
            neg_content_emb = self.text_encoder(**tokens).text_embeds
            neg_content_emb *= neg_content_scale
        else:
            neg_content_emb = None

        # 读取控制图像
        input_image = img_to_cv2_img(style_img_obj)

        detected_map = cv2.Canny(input_image, 50, 200)
        canny_map = Image.fromarray(cv2.cvtColor(detected_map, cv2.COLOR_BGR2RGB))

        # 生成风格化图像
        positive_prompt = "masterpiece, best quality, high quality, " + ", ".join(keyword_list)
        negative_prompt = "text, watermark, lowres, low quality, worst quality, deformed, glitch, low contrast, noisy, saturation, blurry"
        print("Positive prompt: "+positive_prompt)
        print("Negative prompt: "+negative_prompt)

        sd = random.randint(1, 10)
        print("Seed:" + str(sd))

        # generate image with content subtraction
        images = self.ip_model.generate(pil_image=image,
                                        prompt=positive_prompt,
                                        negative_prompt=negative_prompt,
                                        scale=1.0,
                                        guidance_scale=5,
                                        num_samples=1,
                                        num_inference_steps=steps,
                                        seed=sd,
                                        neg_content_emb=neg_content_emb,
                                        image=canny_map,
                                        )
        return images[0]


if __name__ == "__main__":
    from style_img_api import *

    g = Generator()
    keyword_list = ["flower", "nature"]
    url = get_style_img_url_list(keyword_list)[0]
    show_img(get_img(url))
    style_img_obj = get_img_obj(url)
    content_img_obj = Image.open("../assets/datasets/13.jpg")
    result_img = g.generate(content_img_obj, style_img_obj, keyword_list, neg_content_scale=0.8, neg_list=None, steps=100)
    save_img(result_img)





