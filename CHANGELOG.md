## [2.1.0] - 2024-10-05
### Changed
* Logの名前を指定可能にする新Logメッセージに移行 (#32)
    * Member.log_entries, on_log_entry 追加
    * Log.name
    * Log.handler, Log.io
### Added
* Clientコンストラクタに auto_sync 機能追加 (#33)
### Fixed
* sync() でtimeoutの判定が間違っているバグを修正 (#33)
* log_handlerがstderrに出力と書いてあったのに実際にはstdoutに出力していたバグ?を修正 (#32)

## [2.0.0] - 2024-09-22
### Changed
(#31: C++版クライアントver2.0に対応した更新です)
* 受信処理をClient.sync()を呼んだスレッドで行うようにした
* Func.set()でセットした関数はrecv()と同じスレッドでそのまま呼ばれるように仕様変更
    * その代わりとして Func.set_async() 追加
* Client.sync() にtimeout引数追加
* Clientコンストラクタにauto_reconnect引数追加
* AsyncFuncResult → Promise
    * Promise.started, result をdeprecatedにした
    * Promise.reached, found, on_reach, wait_reach, finished, response, rejection, on_finish, wait_finish 追加
* サーバーに接続していない間各種リクエストや関数呼び出しを送らないようにした
    * Func.run_async()時に未接続なら即座に呼び出しは失敗するようになった
* イベント処理にblinkerライブラリを使わないようにした
    * イベントのコールバック設定の関数がすべて仕様変更しました (connect() がなくなったので)
* AnonymousFunc クラス削除
* Func.hidden 削除
* floatを受け取るAPIのほとんどをSupportsFloat型に変更
    * numpyの数値型なども自動的にfloatに変換されるようにしました
### Added
* Client.on_ping(), ping_status がClient自身にも使えるようになった
* Client.wait_connection() はSyncInitEndが完了するまで待機するようにした
* Client.server_hostname 追加
* Member.request_ping_status()
* Variant, InputRef
* view_components に各種input とそのプロパティ
* 各種Field型にexists()追加
* LogEntryメッセージ対応
* Log.append()
* Log.keep_lines

## [1.1.3] - 2024-05-24
### Fixed
* Client.sync() を呼んでも最速で1秒おきにしかデータが送信されなかったのを修正 (#23)
* pythonを終了するときClientの終了処理に1秒かかっていたのを修正 (#23)

## [1.1.2] - 2024-03-09
### Fixed
* サーバーへの接続がエラーになった場合Client.close()で待機し続けてしまうのを修正 (#19)

## [1.1.1] - 2024-03-08
### Changed
* Value, Textで値が変化したときのみ送信するようにした (#18)
* webcface内部ログの表示形式を変更 (名前とログレベルがわかるようにした)
### Fixed
* pythonの終了時に確実にclose()されるようにした & Client.close() 時にキューに溜まっているデータがすべて送信されるようにした (#18)

## [1.1.0] - 2024-02-26
### Added
* Canvas2D, Canvas3D (#12)
### Changed
* values → value_entries など名前変更
### Fixed
* Client.wait_connection()で通信がstartしないのを修正 (#12)

## [1.0.2] - 2023-12-21
### Added
* `__version__`を追加 (#10)
### Fixed
* v1.0.1でsyncInitがバージョン番号として1.0.0を返していた

## [1.0.1] - 2023-12-21
### Fixed
* value.set()にfloatを入れても送信されないバグを修正 (#1)
* funcのint型引数にfloatが送られてくるとエラーになるバグを修正 (#1)
* view_component.button() の引数にkwargsを渡せるようにした (#2)

## [1.0.0] - 2023-12-08
