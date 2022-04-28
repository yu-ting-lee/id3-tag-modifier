## Description

A desktop application that can search and modify ID3 tags of audio files

## Get Started

```
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
```

#### Run Directly

```
cd src && python3 main.py
```

#### Create Executable

```
pyinstaller --onefile src/main.py
cp src/alt.png src/config.ini dist/
cd dist && ./main
```

## Support Tags

`title`, `artist`, `album`, `track number`, `total tracks`, `disc number`, `cover image`
