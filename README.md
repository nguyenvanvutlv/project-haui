# A project-haui Flet app

An example of a minimal Flet app.

To run the app:

```
flet run [app_directory]
```

# cài đặt môi trường (hệ điều hành Linux)

* Yêu cầu cần có GPU
* 

# phần fix lỗi không chạy được flet trên linux

```text
error while loading shared libraries: libmpv.so.1: cannot open shared object file: No such file or directory
```

```commandline
sudo apt update

sudo apt install libmpv-dev libmpv2

sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1
```