from MainGen import app
from flask import render_template, request
import requests
import keyring

def get_user_pass():
    return (
        keyring.get_password("imgflip", "username"),
        keyring.get_password("imgflip", "password")
    )

def meme_templates():
    try:
        response = requests.get('https://api.imgflip.com/get_memes')
        response.raise_for_status()
        return response.json()['data']['memes']
    except requests.RequestException as e:
        print(f"Error fetching meme templates: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    username, password = get_user_pass()
    meme_url = None
    templates = meme_templates()

    if request.method == 'POST':
        template_id = request.form['template_id']
        selected_template = next((meme for meme in templates if meme['id'] == template_id), None)

        if selected_template:
            box_count = selected_template['box_count']
            texts = [request.form.get(f'text{i}', '') for i in range(box_count)]

            meme_data = {
                'template_id': template_id,
                'username': username,
                'password': password
            }
            meme_data.update({f'boxes[{x}][text]': texts[x] for x in range(box_count)})

            try:
                response = requests.post('https://api.imgflip.com/caption_image', data=meme_data)
                response.raise_for_status()
                data = response.json()
                if data.get('success'):
                    meme_url = data['data']['url']
                else:
                    return f"Error: {data.get('error_message')}"
            except requests.RequestException as error:
                return f"Meme Gen Error,  {error}"
        else:
            return "Template Error"

    return render_template('index.html', templates=templates, meme_url=meme_url)
