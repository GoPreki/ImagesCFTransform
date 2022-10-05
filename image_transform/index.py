import os
import pillow_avif
from io import BytesIO
from uuid import uuid4
from pathlib import Path
from PIL import Image, ImageSequence
from typing import Generator, Iterable, Optional, Tuple, Union
from utils import optional_dict

# Just for linter to ignore unused
pillow_avif.__version__


class ImageTransformer:
    img: Image.Image
    source: Optional[Path] = None

    def __init__(self, source: Union[Path, bytes], /, *, destiny_with_modifiers=True) -> None:
        if isinstance(source, Path):
            self.img = Image.open(source)
            self.source = source
        else:
            with BytesIO(source) as f:
                self.img = Image.open(f)
                self.img.load()

        self.final_extension = self.img.format or ''

        self.name_mods = []
        self.is_animated = hasattr(self.img, 'is_animated') and self.img.is_animated
        self.destiny_with_modifiers = destiny_with_modifiers

    @staticmethod
    def _memory_save(img: Image.Image,
                     format: Optional[str] = None,
                     optimize: bool = True,
                     save_all: bool = True,
                     append_images: Optional[Iterable[Image.Image]] = None):
        temp_path = Path(f'./temp/{uuid4()}.{format}')
        if not temp_path.parent.exists():
            temp_path.parent.mkdir()
        img.save(temp_path,
                 format=format or img.format,
                 optimize=optimize,
                 save_all=save_all,
                 **optional_dict(append_images=append_images),
                 quality=75)

        img = Image.open(temp_path)
        img.load()

        os.remove(temp_path)
        return img

    @staticmethod
    def _clean_format(format: str):
        format = format.replace('.', '')
        return format if format != 'jpg' else 'jpeg'

    def _resize_animated(self, dimensions: Tuple[int, int]):

        def _thumbnail_frames(image) -> Generator[Image.Image, None, None]:
            for frame in ImageSequence.Iterator(image):
                new_frame = frame.copy()
                new_frame.thumbnail(size=dimensions, resample=Image.Resampling.LANCZOS)
                yield new_frame

        frames = _thumbnail_frames(self.img)
        self.img = ImageTransformer._memory_save(img=next(frames),
                                                 format=ImageTransformer._clean_format(self.final_extension),
                                                 optimize=True,
                                                 save_all=True,
                                                 append_images=frames)

        return self

    def resize(self, dimensions: Tuple[int, int]):
        self.name_mods.append('x'.join([str(d) for d in dimensions]))

        if self.is_animated:
            return self._resize_animated(dimensions)

        self.img.thumbnail(size=dimensions, resample=Image.Resampling.LANCZOS)
        self.img = ImageTransformer._memory_save(self.img,
                                                 format=ImageTransformer._clean_format(self.final_extension),
                                                 optimize=True,
                                                 save_all=False)

        return self

    def convert_to_jpeg(self):
        self.final_extension = '.jpeg'

        self.img = self.img.convert('RGB')
        self.img = ImageTransformer._memory_save(self.img, format="jpeg", optimize=True, save_all=False)
        self.is_animated = False

        return self

    def convert_to_png(self):
        self.final_extension = '.png'

        self.img = ImageTransformer._memory_save(self.img, format="png", optimize=True, save_all=False)
        self.is_animated = False

        return self

    def convert_to_webp(self):
        self.final_extension = '.webp'

        self.img = ImageTransformer._memory_save(self.img, format="webp", optimize=True, save_all=True)

        return self

    def convert_to_avif(self):
        self.final_extension = '.avif'

        self.img = ImageTransformer._memory_save(self.img, format="avif", optimize=True, save_all=True)

        return self

    def compress(self):
        self.name_mods.append('compressed')
        self.img = ImageTransformer._memory_save(self.img,
                                                 format=ImageTransformer._clean_format(self.final_extension),
                                                 optimize=True,
                                                 save_all=self.is_animated)
        return self

    def save(self, destination: Optional[Path] = None) -> None:
        _destination = destination or self.source
        if not _destination:
            raise Exception('Destination not defined')

        mods = ''
        if not _destination.parent.exists():
            _destination.parent.mkdir()

        if self.destiny_with_modifiers:
            mods = '_' + '_'.join(self.name_mods) if self.name_mods else ''
        _destination = _destination.with_stem(f'{_destination.stem}' + mods).with_suffix(self.final_extension)

        self.img.save(_destination, **self.img.info, save_all=self.is_animated, optimize=True)

    def get_bytes(self) -> bytes:
        with BytesIO() as in_mem_file:
            self.img.save(in_mem_file, format=self.img.format)
            in_mem_file.seek(0)

            return in_mem_file.getvalue()
