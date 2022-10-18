from telethon import TelegramClient, events, sync
import os
from dotenv import load_dotenv
from telethon.tl.types import InputMessagesFilterPhotos

from PIL import Image, ImageDraw, ImageFont
import textwrap
from string import ascii_letters

TINT_COLOR = (255, 255, 255)  # Black
TRANSPARENCY = .55  # Degree of transparency, 0-100%
OPACITY = int(255 * TRANSPARENCY)

def generate_img(id,folder, text):
    """ Generate image with overlay and text

    Args:
        id (int): Message ID
        folder (str): Path to text and src image
        text (str): Text of message

    Returns:
        _type_: _description_
    """
    img_path = folder+"img.jpg"
    img = Image.open(fp=img_path, mode='r')
    fsize = 72
    text_len_= len(text)
    if text_len_>150:
        fsize = 25+int(50*(1-(text_len_-150)/150/2))

    font = ImageFont.truetype(font='./font/georgia.ttf', size=fsize)
    # Create DrawText object
    draw = ImageDraw.Draw(img, 'RGBA')
    # Determine extent of the largest possible square centered on the image.
    # and the image's shorter dimension.
    if img.size[0] > img.size[1]:
        shorter = img.size[1]
        longer = img.size[0]
        llx, lly = shorter *.1 , shorter *.1
    else:
        shorter = img.size[0]
        longer = img.size[1]
        llx, lly = shorter *.1 , longer *.1
    # Calculate upper point + 1 because second point needs to be just outside the
    # drawn rectangle when drawing rectangles.
    urx, ury = longer-lly+1, shorter-lly+1
    # overlay = Image.new('RGBA', img.size, TINT_COLOR+(0,))
    # draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
    draw.rectangle(((llx, lly), (urx, ury)), fill=TINT_COLOR+(OPACITY,))
    # img = Image.alpha_composite(img, overlay)
    # Calculate the average length of a single character of our font.
    # Note: this takes into account the specific font and font size.
    avg_char_width = False
    try:
        avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
    except Exception as e:
        print(e)
    if avg_char_width is False:
        return False
    # Translate this average length into a character count
    max_char_count = int(img.size[0] * .88 / avg_char_width)
    # Create a wrapped text object using scaled character count
    text = textwrap.fill(text=text, width=max_char_count)
    # Add text to the image
    draw.text(xy=(img.size[0]/2, img.size[1] / 2), text=text, font=font, fill="#000000", anchor='mm')
    img.save("./results/%d.jpg" % id, quality=92)

load_dotenv()

# Remember to use your own values from my.telegram.org!
api_id           = os.getenv('API_ID')
api_hash         = os.getenv('API_HASH')
channel_username = os.getenv('API_CHANNEL')
client           = TelegramClient('anon', api_id, api_hash)
client.start()
print("Client Created")
os.makedirs("./results/", exist_ok=True)
os.makedirs("./data/", exist_ok=True)
for message in client.get_messages(channel_username, limit=600, filter=InputMessagesFilterPhotos):
    # if message.id != 3651:
    #     continue
    p_ = './data/' + str(message.id)+'/'
    os.makedirs(p_, exist_ok=True)
    # save text
    if not os.path.isfile(p_+'msg.txt'):
        with open( p_+'msg.txt', 'w') as f:
            f.write(message.message)
    if not os.path.isfile(p_+"img.jpg"):
        client.download_media(message.media,p_+"img.jpg")
    generate_img(message.id,p_, message.message)
    print("Finish #%d" % message.id)

