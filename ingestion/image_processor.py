
'''
This will read the image file and then send it to the vision model
the model will give us the text description 
then we will save that text description and will search for it later on
'''
import os
import base64
from PIL import Image  #Python Image Library for opening,loading,editing,resizing the image 
import io #for getiing the bytes of the image
from groq import Groq
import config


def read_image(image_path):
    #converting the image to the base64 txt because the groq api don't accpet the raw api, it has to be converted to the plain text
    
    img = Image.open(image_path)
    
    #groq needs the RGB image, and we have to convert it to the RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    #resize the image if it is large
    #this resize will save our api call and increase the speed
    max_size = 1024
    width, height = img.size
    if width > max_size or height > max_size:
        ratio = max_size / max(width / height)
        new_w = int(width * ratio)
        new_h = int(height * ratio)
        img = img.resize((new_w, new_h))
        
    #save image to the memory as BYTES
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)  #after saving, the cursor moves to the end
    buffer.seek(0)  #this will move the cursor to the starting
    
    image_bytes = buffer.read()
    b64 = base64.b64encode(image_bytes).decode("utf-8")  #converts the base64 to the normal text
    return b64

def describe_image (image_path):
    #give image to the groq api and get the metadata back
    # "text"= the AI description
    # "metadata" = the info about the image
    print(f"reading image:{image_path}")
    b64_image = read_image(image_path)
    
    file_name = os.path.basename(image_path)
    
    prompt = (
        "describe this image in detail"
        "if it is chart or graph, mention: the chart type, axis label"
        "data values, and main trend or insight"
        "if it is a photo, then describe what you see clearly"
    )
    
    client = Groq(api_key = config.GROQ_API_KEY)
    
    response = client.chat.completions.create(
        model = config.GROQ_VISION_MODEL,
        messages = [
            {
                "role" : "user",
                "content" : [
                    {
                        "type" : "image_url",
                        "image_url" : {
                            # Standard way to embed an image in the API call
                            # Format: "data:<mime_type>;base64,<data>"
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    },
                    {
                        "type" : "text",
                        "text" : prompt
                    }
                ]
            }
        ],
        max_tokens = 800,
    )
    
    description = response.choices[0].message.content
    print(f"Got description ({len(description)} chars)")
    
    return {
        "text" : description,
        "metadata" : {
            "source_type" : "image",
            "file_name" : file_name,
            "file_path" : image_path
        }
    }
    