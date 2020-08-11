# Brownie Learn
Brownie Learn is an app that can learn your objects.

## How to setup
1. Update firmware to maixpy_v0.5.0_9_g8eba07d_m5stickv.bin
http://dl.sipeed.com/MAIX/MaixPy/release/master/maixpy_v0.5.0_9_g8eba07d
2. Copy files in brownie_learn directory into microSD card
3. run!

## How to use

1. Scan QR code and shoot your object that you want to train.
2. that's all!

* QR code 'reset.png' is a special code to reset your model.

-------------------
エディタの操作は
http://ssj.siosalt.tokyo/?cat=21
または
https://scrapbox.io/saitotetsuya/M5StickV

M5StickV MicroPython Instructions
https://qiita.com/Lathe/items/7fbfccafb879de4bf11e

M5StickVをさわってみるメモ.md
https://gist.github.com/yoggy/86c979fbbae7c3de00c0e6b5c9787475

MaixPy Documentation
https://maixpy.sipeed.com/en/

MicroPython ドキュメンテーション
https://micropython-docs-ja.readthedocs.io/ja/latest/index.html

【M5STICKV】PWMでサーボモータを動かす
【解説】M5STICKVのPYTHONプログラミング　～液晶編～ｓ
https://hellobreak.net/

M5StickVのGroveコネクタを使う - ブザーを鳴らす
https://hrkz.tokyo/m5stickv-grove/

Seeed-Studio / grove.py
https://github.com/Seeed-Studio/grove.py/tree/master/doc

MaixPy(MicroPython)でBlinkする
https://beta-notes.way-nifty.com/blog/2020/01/post-531c9b.html

Grove端子を利用する - UART
https://riscv.love/024




AI+IoTなデバイスをお手軽に作れるM5StickVとSORACOM LTE-M Button Plus
(ノートブックで転移学習)
http://masato-ka.hatenablog.com/entry/2019/09/04/002317


M5StickVやUnitVで使えるkmodelファイルをローカル環境で作成する。
https://raspberrypi.mongonta.com/howto-make-kmodel-on-ubuntu/
複数のオブジェクトを認識できるkmodelファイルを作成する
https://raspberrypi.mongonta.com/howto-make-kmodel-of-multiple-object/


サンプル
https://github.com/mongonta0716/m5stickv-tips

https://gist.github.com/ksasao
https://github.com/anoken/purin_wo_motto_mimamoru_gijutsu

-------------------
ＱＲ
https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=ichi
https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=ni
https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=san
https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=yon
https://chart.googleapis.com/chart?cht=qr&chs=200x200&chl=go



音声
http://open-jtalk.sp.nitech.ac.jp/
http://cloud.ai-j.jp/hackathon/index.php


-------------
プログラム実行は、import でなく下記のほうがいい

with open("hello.py") as f:
    exec(f.read())


---------------------------
#MaixHub Online CompileでMaixPyをカスタマイズする
https://qiita.com/nnn112358/items/1575206bda278235774f

https://www.maixhub.com/compile.html

MaixPy IDE Support 以外をOFFで構わない？
