from __future__ import annotations
from typing import Callable, Optional
import webcface.field
import webcface.data
import webcface.view
import webcface.func


class Member(webcface.field.Field):
    def __init__(self, base: webcface.field.Field, member: str = "") -> None:
        """Memberを指すクラス

        このコンストラクタを直接使わず、
        Client.member(), Client.members(), Client.onMemberEntry などを使うこと

        詳細は `Memberのドキュメント <https://na-trium-144.github.io/webcface/md_02__member.html>`_ を参照
        """
        super().__init__(base.data, member if member != "" else base._member)

    @property
    def name(self) -> str:
        """Member名"""
        return self._member

    def value(self, field: str) -> webcface.data.Value:
        """Valueを参照する"""
        return webcface.data.Value(self, field)

    def text(self, field: str) -> webcface.data.Text:
        """Textを参照する"""
        return webcface.data.Text(self, field)

    def view(self, field: str) -> webcface.view.View:
        """Viewを参照する"""
        return webcface.view.View(self, field)

    def func(
        self, arg: Optional[str | Callable] = None, **kwargs
    ) -> webcface.func.Func | webcface.func.AnonymousFunc:
        """FuncオブジェクトまたはAnonymousオブジェクトを生成

        #. member.func(arg: str)
            * 指定した名前のFuncオブジェクトを生成・参照する。
        #. member.func(arg: Callable, [**kwargs])
            * Funcの名前を決めずに一時的なFuncオブジェクト(AnonymoudFuncオブジェクト)を作成し、関数をセットする。
        #. @member.func(arg: str, [**kwargs])
            * デコレータとして使い、デコレートした関数を指定した名前でセットする。
            * デコレート後、関数は元のまま返す。
        #. @member.func([**kwargs])
            * 3と同じだが、名前はデコレートした関数から自動で取得される。

        2,3,4について、関数のセットに関しては Func.set() を参照。

        :return: 1→ Func, 2→ AnonymousFunc
        """
        if isinstance(arg, str):
            return webcface.func.Func(self, arg, **kwargs)
        else:
            return webcface.func.AnonymousFunc(self, arg, **kwargs)
