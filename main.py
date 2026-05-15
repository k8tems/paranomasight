import time
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

def get_mime_type(filename):
    """Get MIME type based on file extension."""
    ext = Path(filename).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
        '.gif': 'image/gif'
    }
    return mime_types.get(ext, 'image/jpeg')


def query_llm(prompt: str, image_bytes: bytes, mime_type: str) -> str:
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents= [
        types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        ),
        prompt
    ])
    return response.text

def crop_left_screen(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.crop((0, 0, w // 2, h))

def transcribe_image(image_path: Path, dst_path: Path):
    # デュアルディスプレイのスクショが取られるので、左半分を切り抜く
    image = crop_left_screen(Image.open(image_path))

    # 1920x1080は少し大きすぎるし、テキストが十分に大きいので半分にする
    w, h = image.size
    new_size = (max(1, w // 2), max(1, h // 2))
    image = image.resize(new_size, Image.LANCZOS)

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    image_bytes = buf.getvalue()
    
    # mime type based on original file extension
    mime_type = get_mime_type(image_path)
    
    prompt = """
画像に書かれてるテキストを書き起こして下さい。。
- 画像のテキストは日本語で書かれています。
- 画像はゲーム内の資料を表す画面で、考察と情報を検索可能にする為にテキストに書き起こして欲しいです。
- 左側のセレクトボックスの中で青くなってるのが現在表示されてる資料のタイトルで、
画面の3/4を占めてる右側のテキスト(以降資料部分)が内容です。
- 資料に画像がある場合はスキップして下さい。
- <重要> 書き起こしは資料部分のみでお願いします。
- 判明してる場合は、資料のタイトルを1行めに<タイトル>の形式で書き起こして下さい。"""
    transcription = query_llm(prompt, image_bytes, mime_type)
    print(transcription)
    dst_path.write_text(transcription, encoding='utf-8')


def main():
    image_root = Path('E:\\Projects\\paranomasight\\screenshots')
    for image_path in sorted(image_root.glob('*.png')):
        dst_root = Path('transcriptions')
        dst_root.mkdir(exist_ok=True)
        dst_path = dst_root / image_path.with_suffix('.txt').name
        
        if not dst_path.exists():
            transcribe_image(image_path, dst_path)
            time.sleep(3)  # politeness
        else:
            print(f"{dst_path} already exists. Skipping.")



if __name__ == "__main__":
    main()
