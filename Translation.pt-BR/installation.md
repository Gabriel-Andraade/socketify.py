Usando install via requirements.txt
```text
socketify
```
```bash
pip install -r ./requirements.txt
#ou especifique PyPy3
pypy3 -m pip install -r ./requirements.txt
```

Se você estiver usando Linux ou macOS, pode ser necessário instalar libuv e zlib em seu sistema

macOS
```bash
brew install libuv
brew install zlib
```

Linux
```bash
apt install libuv1 zlib1g
```

### Próximo [Getting started](getting-started.md)