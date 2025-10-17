#%%
import glob
from PIL import Image
from tqdm import tqdm

png_files = glob.glob("img/*.png")
# %%
png_files
# %%

def convert_pngs_to_jpg_max_height_800():
    import os
    for png_path in tqdm(png_files, desc="Converting PNG to JPG (max height 800)"):
        try:
            img = Image.open(png_path)

            width, height = img.size
            if height > 800:
                new_height = 800
                new_width = int(width * (800 / height))
                img = img.resize((new_width, new_height), Image.LANCZOS)

            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                background = Image.new("RGB", img.size, (255, 255, 255))
                alpha = img.split()[-1] if img.mode in ("RGBA", "LA") else None
                background.paste(img, mask=alpha)
                output_img = background
            else:
                output_img = img.convert("RGB")

            base_name = os.path.splitext(os.path.basename(png_path))[0]
            output_path = os.path.join(os.path.dirname(png_path), f"{base_name}.jpg")

            output_img.save(output_path, "JPEG", quality=80, optimize=True)
        except Exception as e:
            print(f"Failed processing {png_path}: {e}")


if __name__ == "__main__":
    convert_pngs_to_jpg_max_height_800()
# %%
