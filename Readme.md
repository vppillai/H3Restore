# Harmony 3 Repo restore

We often need to switch between different dependency versions of Microchip Harmony3 components. However, when we do this in bulk using the dependencies button of the content manager or using an example manifest file, it is difficult to restore all the dependencies back to the latest versions. This tool helps you do just that. 

## Running the tool

```
usage: H3restore [-h] -p PATH [-l] [-C] [-F] [-m MANIFEST]

Tool to restore Harmony3 Git repos to the latest tag v1.4.0

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            Just list the changes. do not move the tags
  -C, --noclean         Do not clean and reset the repos. Might result in failures if there are uncommitted changes interfering with the tag change
  -F, --nofetch         Do not fetch latest repo versions from origin
  -m MANIFEST, --manifest MANIFEST
                        manifest file to be used to restore repos. Takes precedence over fetched versions

required arguments:
  -p PATH, --path PATH  Location of Harmony3 repo
```

![demo](https://user-images.githubusercontent.com/3634378/119480067-eae72080-bd6e-11eb-8160-336c567d5fa3.gif)


## EXE release
The executable was created using pyinstaller for people who have difficulty installing python.

``` sh
pyinstaller --onefile .\H3restore.py -i .\favicon.ico --clean
```

## License

"THE BEER-WARE LICENSE" (Revision 42): <vysakhpillai@gmail.com> wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return —Vysakh P Pillai
