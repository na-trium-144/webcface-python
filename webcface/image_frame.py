from typing import Optional
from enum import IntEnum

try:
    import numpy
except ModuleNotFoundError:
    pass


class ImageColorMode(IntEnum):
    GRAY = 0
    BGR = 1
    BGRA = 2
    RGB = 3
    RGBA = 4


class ImageCompressMode(IntEnum):
    RAW = 0
    JPEG = 1
    WEBP = 2
    PNG = 3


class ImageFrame:
    """画像データ (ver2.4〜)

    * 8bitのグレースケール, BGR, BGRAフォーマットのみを扱う
    * 画像受信時にはjpegやpngなどにエンコードされたデータが入ることもある
    """

    _width: int
    _height: int
    _data: bytes
    _color_mode: int
    _cmp_mode: int

    def __init__(
        self, width: int, height: int, data: bytes, color_mode: int, compress_mode: int
    ) -> None:
        self._width = width
        self._height = height
        self._data = data
        self._color_mode = color_mode
        self._cmp_mode = compress_mode
        assert width * height * self.channels == len(data)

    def empty(self) -> bool:
        """画像が空かどうかを返す"""
        return len(self._data) == 0

    @property
    def width(self) -> int:
        """画像の幅"""
        return self._width

    @property
    def height(self) -> int:
        """画像の高さ"""
        return self._height

    @property
    def channels(self) -> int:
        """1ピクセルあたりのデータサイズ(byte数)"""
        if self._color_mode == ImageColorMode.GRAY:
            return 1
        if self._color_mode == ImageColorMode.BGR:
            return 3
        if self._color_mode == ImageColorMode.RGB:
            return 3
        if self._color_mode == ImageColorMode.BGRA:
            return 3
        if self._color_mode == ImageColorMode.RGBA:
            return 3
        raise ValueError("Unknown color format")

    @property
    def color_mode(self) -> int:
        """色の並び順

        compress_modeがRAWでない場合意味をなさない。

        ImageColorMode のenumを参照
        """
        return self._color_mode

    @property
    def compress_mode(self) -> int:
        """画像の圧縮モード

        ImageCompressMode のenumを参照
        """
        return self._cmp_mode

    @property
    def data(self) -> bytes:
        """画像データ

        compress_modeがRAWの場合、height * width * channels
        要素の画像データ。 それ以外の場合、圧縮された画像のデータ
        """
        return self._data

    @staticmethod
    def from_numpy(img: "numpy.ndarray", color_mode: int) -> "ImageFrame":
        """numpy配列からImageFrameを作成する

        color_mode がGRAYの場合 (height, width) または (height, width, 1),
        color_mode がBGR,RGBの場合 (height, width, 3),
        color_mode がBGRA,RGBAの場合 (height, width, 4)
        のuint8配列のみが使用可能
        """
        import numpy

        assert isinstance(img, numpy.ndarray), "img must be numpy.ndarray"
        assert img.dtype == numpy.uint8, "only dtype uint8 is supported"
        if color_mode == ImageColorMode.GRAY:
            assert len(img.shape) == 2 or (
                len(img.shape) == 3 and img.shape[2] == 1
            ), "shape must be (height, width) or (height, width, 1)"
        elif color_mode == ImageColorMode.BGR or color_mode == ImageColorMode.RGB:
            assert (
                len(img.shape) == 3 and img.shape[2] == 3
            ), "shape must be (height, width, 3)"
        elif color_mode == ImageColorMode.BGRA or color_mode == ImageColorMode.RGBA:
            assert (
                len(img.shape) == 3 and img.shape[2] == 4
            ), "shape must be (height, width, 4)"
        else:
            raise ValueError("Unknown color format")

        return ImageFrame(
            img.shape[1],
            img.shape[0],
            img.tobytes(),
            color_mode,
            ImageCompressMode.RAW,
        )

    def numpy(self) -> "numpy.ndarray":
        """numpy配列に変換する

        color_mode がGRAYの場合 (height, width, 1),
        color_mode がBGR,RGBの場合 (height, width, 3),
        color_mode がBGRA,RGBAの場合 (height, width, 4)
        のuint8配列を返す

        compress_mode がRAWでない場合はエラー
        """
        import numpy

        assert (
            self._cmp_mode == ImageCompressMode.RAW
        ), "compressed image is not supported"

        return numpy.frombuffer(self._data, dtype=numpy.uint8).reshape(
            self._height, self._width, self.channels
        )


class ImageReq:
    width: Optional[int]
    height: Optional[int]
    color_mode: Optional[int]
    compress_mode: Optional[int]
    quality: Optional[int]
    frame_rate: Optional[float]

    def __init__(self, width, height, color_mode, compress_mode, quality, frame_rate):
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.compress_mode = compress_mode
        self.quality = quality
        self.frame_rate = frame_rate

    def __eq__(self, obj) -> bool:
        return (
            isinstance(obj, ImageReq)
            and self.width == obj.width
            and self.height == obj.height
            and self.color_mode == obj.color_mode
            and self.compress_mode == obj.compress_mode
            and self.quality == obj.quality
            and self.frame_rate == obj.frame_rate
        )

    def __ne__(self, obj) -> bool:
        return not self == obj
