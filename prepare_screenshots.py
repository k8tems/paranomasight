from main import *

if __name__ == '__main__':
    src_dir = Path('screenshots')
    dst_dir = Path('prepared_screenshots')
    dst_dir.mkdir(exist_ok=True)
    for src_path in src_dir.glob('*.png'):
        # デュアルディスプレイのスクショが取られるので、左半分を切り抜く
        image = crop_left_screen(Image.open(src_path))

        # 1920x1080は少し大きすぎるし、テキストが十分に大きいので半分にする
        w, h = image.size
        new_size = (max(1, w // 2), max(1, h // 2))
        image = image.resize(new_size, Image.LANCZOS)
        image.save(dst_dir / src_path.name)
    