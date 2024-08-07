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
