from typing import Optional, Callable
from enum import IntEnum
import webcface.field
import webcface.member
import webcface.message


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


class Image(webcface.field.Field):
    def __init__(self, base: "webcface.field.Field", field: str = "") -> None:
        """Imageを指すクラス

        このコンストラクタを直接使わず、
        Member.image(), Member.images(), Member.onImageEntry などを使うこと
        """
        super().__init__(
            base._data, base._member, field if field != "" else base._field
        )

    @property
    def member(self) -> "webcface.member.Member":
        """Memberを返す"""
        return webcface.member.Member(self)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._field

    def on_change(self, func: Callable) -> Callable:
        """値が変化したときのイベント

        コールバックの引数にはImageオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._data_check()
        if self._member not in data.on_image_change:
            data.on_image_change[self._member] = {}
        data.on_image_change[self._member][self._field] = func
        return func

    def child(self, field: str) -> "Image":
        """子フィールドを返す

        :return: 「(thisのフィールド名).(子フィールド名)」をフィールド名とするImage
        """
        return Image(self, self._field + "." + field)

    def _try_request(self) -> None:
        # req_dataがNoneの場合以前のreq_dataは上書きされない
        req = self._data_check().image_store.add_req(self._member, self._field)
        if req > 0:
            self.request()

    def request(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        color_mode: Optional[int] = None,
        compress_mode: Optional[int] = None,
        quality: Optional[int] = None,
        frame_rate: Optional[int] = None,
    ) -> None:
        """画像の受信をリクエストする

        :param width: 画像の幅
        :param height: 画像の高さ
            width, height のどちらかのみがNoneの場合縦横比を保ってリサイズし、
            どちらもNoneの場合は元画像のサイズになる
        :param color_mode: 画像の色フォーマット (Noneの場合元画像のフォーマット)
        :param cmp_mode: 圧縮モード
        :param quality: 圧縮のパラメータ
            * jpeg → 0〜100 (大きいほうが高品質)
            * png → 0〜9 (大きいほうが圧縮後のサイズが小さい)
            * webp → 1〜100 (大きいほうが高品質)
        :param frame_rate: 画像を受信する頻度 (指定しない場合元画像が更新されるたびに受信する)
        """
        img_req = ImageReq(
            width, height, color_mode, compress_mode, quality, frame_rate
        )
        req = self._data_check().image_store.add_req(self._member, self._field, img_req)
        if req > 0:
            self._data_check().queue_msg_req(
                [
                    webcface.message.ImageReq.new(
                        self._member,
                        self._field,
                        req,
                        img_req,
                    )
                ]
            )

    def try_get(self) -> "Optional[ImageFrame]":
        """画像を返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        return self._data_check().image_store.get_recv(self._member, self._field)

    def get(self) -> "ImageFrame":
        """画像を返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else ImageFrame(0, 0, b"", 0, 0)

    def exists(self) -> bool:
        """このフィールドにデータが存在すればtrue

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._field in self._data_check().image_store.get_entry(self._member)

    def set(self, data: "ImageFrame") -> "Image":
        """画像をセットする"""
        self._set_check().image_store.set_send(self._field, data)
        on_change = (
            self._data_check().on_image_change.get(self._member, {}).get(self._field)
        )
        if on_change is not None:
            on_change(self)
        return self
