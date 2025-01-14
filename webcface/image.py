from typing import Optional, Callable
import webcface.field
import webcface.member
import webcface.message
import webcface.image_frame


class Image:
    _base: "webcface.field.Field"

    def __init__(self, base: "webcface.field.Field", field: str = "") -> None:
        """Imageを指すクラス

        このコンストラクタを直接使わず、
        Member.image(), Member.images(), Member.onImageEntry などを使うこと
        """
        self._base = webcface.field.Field(
            base._data, base._member, field if field != "" else base._field
        )

    @property
    def member(self) -> "webcface.member.Member":
        """Memberを返す"""
        return webcface.member.Member(self._base)

    @property
    def name(self) -> str:
        """field名を返す"""
        return self._base._field

    def on_change(self, func: Callable) -> Callable:
        """値が変化したときのイベント

        コールバックの引数にはImageオブジェクトが渡される。

        まだ値をリクエストされてなければ自動でリクエストされる
        """
        self.request()
        data = self._base._data_check()
        if self._base._member not in data.on_image_change:
            data.on_image_change[self._base._member] = {}
        data.on_image_change[self._base._member][self._base._field] = func
        return func

    def child(self, field: str) -> "Image":
        """「(thisの名前).(追加の名前)」を新しい名前とするImage"""
        return Image(self._base.child(field))

    def _try_request(self) -> None:
        # req_dataがNoneの場合以前のreq_dataは上書きされない
        req = self._base._data_check().image_store.add_req(
            self._base._member, self._base._field
        )
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
        img_req = webcface.image_frame.ImageReq(
            width, height, color_mode, compress_mode, quality, frame_rate
        )
        req = self._base._data_check().image_store.add_req(
            self._base._member, self._base._field, img_req
        )
        if req > 0:
            self._base._data_check().queue_msg_req(
                [
                    webcface.message.ImageReq.new(
                        self._base._member,
                        self._base._field,
                        req,
                        img_req,
                    )
                ]
            )

    def try_get(self) -> "Optional[webcface.image_frame.ImageFrame]":
        """画像を返す、まだリクエストされてなければ自動でリクエストされる"""
        self.request()
        return self._base._data_check().image_store.get_recv(
            self._base._member, self._base._field
        )

    def get(self) -> "webcface.image_frame.ImageFrame":
        """画像を返す、まだリクエストされてなければ自動でリクエストされる"""
        v = self.try_get()
        return v if v is not None else webcface.image_frame.ImageFrame(0, 0, b"", 0, 0)

    def exists(self) -> bool:
        """このフィールドにデータが存在すればtrue

        try_get() などとは違って、実際のデータを受信しない。
        リクエストもしない。
        """
        return self._base._field in self._base._data_check().image_store.get_entry(
            self._base._member
        )

    def set(self, data: "webcface.image_frame.ImageFrame") -> "Image":
        """画像をセットする"""
        self._base._set_check().image_store.set_send(self._base._field, data)
        on_change = (
            self._base._data_check()
            .on_image_change.get(self._base._member, {})
            .get(self._base._field)
        )
        if on_change is not None:
            on_change(self)
        return self
