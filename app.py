import gradio as gr
import requests
import json

# --- Core Function: Fetch Tags & Image Preview ---
def fetch_info(image_id):
    if image_id.strip() == '':
        return (
            gr.Textbox.update(value="[ABORTED]: The Image ID cannot be empty!", lines=6),
            gr.Textbox.update(value=""),
            gr.HTML.update(value="Preview image"),
            gr.HTML.update(visible=False)
        )

    base_url = 'https://danbooru.donmai.us/posts'
    url = f'{base_url}/{image_id}.json'

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return (
                gr.Textbox.update(value=f"[ERROR]: Failed to fetch data for ID {image_id}", lines=6),
                gr.Textbox.update(value=""),
                gr.HTML.update(value="Preview image"),
                gr.HTML.update(visible=False)
            )

        data = response.json()
        character = data.get('tag_string_character', '')
        origin = data.get('tag_string_copyright', '')
        tags = data.get('tag_string_general', '')
        additional = data.get('tag_string_meta', '').replace(' ', ', ')
        source = data.get('source', '')

        # Prompt Construction
        prompt = f'{character} {origin} {tags}'
        formatted_tags = tags.replace(' ', ', ')
        output_info = f"Character: {character}\nOrigin: {origin}\nTags: {formatted_tags} \nAdditional: {additional} \nSource: {source}"

        # Image Links
        preview_url = data.get('preview_file_url')
        full_image_url = data.get('file_url') or data.get('large_file_url') or preview_url

        # HTML Components
        preview_html = f'<img src="{preview_url}" alt="Preview" style="max-width:100%; max-height:300px; border-radius: 8px;" />' if preview_url else "Preview image"
        download_html = f'''
            <a href="{full_image_url}" download="{character or 'image'}" target="_blank" id="download_link">
                ⬇️ Download !
            </a>
        '''

        return (
            gr.Textbox.update(value=output_info, lines=10),
            gr.Textbox.update(value=prompt.replace(' ', ', '), lines=10),
            gr.HTML.update(value=preview_html),
            gr.HTML.update(value=download_html, visible=True)
        )

    except Exception as e:
        return (
            gr.Textbox.update(value=f"[ERROR]: Exception occurred: {str(e)}", lines=6),
            gr.Textbox.update(value=""),
            gr.HTML.update(value="Preview image"),
            gr.HTML.update(visible=False)
        )

# --- Interface Layout ---
with gr.Blocks(css="""
body { background-color: #222; color: white; font-family: sans-serif; }
h1 { color: #40E0D0; text-align: center; font-size: 2.5em; margin-bottom: 10px; }
button { border-radius: 8px !important; }

#download_full_image_link_container {
    display: flex;
    justify-content: center;
}
#download_full_image_link_container a#download_link {
    background-color: #4a90e2;
    color: white;
    padding: 10px 20px;
    font-size: 16px;
    font-weight: 500;
    text-decoration: none;
    transition: background-color 0.3s ease;
}
#download_full_image_link_container a#download_link:hover {
    background-color: #3b7cd6;
}

.preview-container {
    border: 1px solid #555;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    margin-top: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.output-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.gradio-container textarea {
    width: 100%;
    resize: none;
    overflow-y: auto;
    white-space: pre-wrap;
    box-sizing: border-box;
}
""") as demo:

    gr.HTML("<h1>Get Danbooru Tags</h1>")

    with gr.Row(equal_height=True):
        image_id_input = gr.Textbox(
            placeholder="Enter Danbooru image ID...",
            scale=6,
            container=False,
            show_label=False
        )
        search_btn = gr.Button("Query Danbooru", scale=4)

    preview_html = gr.HTML("Preview image", elem_id="preview_area", elem_classes=["preview-container"])
    download_html = gr.HTML("", visible=False, elem_id="download_full_image_link_container")

    output_info = gr.Textbox(label="Full data:", lines=6, max_lines=10, interactive=True, elem_classes=["output-container"])
    output_prompt = gr.Textbox(label="Prompt:", lines=4, max_lines=10, interactive=True, elem_classes=["output-container"])

    search_btn.click(
        fn=fetch_info,
        inputs=[image_id_input],
        outputs=[output_info, output_prompt, preview_html, download_html]
    )

    demo.launch()
