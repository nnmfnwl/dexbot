### 1. Operating system dependencies setup and dexsetup files download

**Update system and install git:**
   * estimated time on very slow machine few minutes
   * system upgrade will be prompted for root password
```
su - -c "apt update; apt full-upgrade; apt install git; exit"
```

**Create root directory(~/Downloads/ccwallets) and download all dexsetup files**
   * estimated time on very slow machine 1 minute
```
mkdir -p ~/Downloads/ccwallets/dexsetup \
&& cd ~/Downloads/ccwallets/dexsetup \
&& git clone https://github.com/nnmfnwl/dexsetup.git ./
```

**Software dependencies installation**
   * installation script is using native repository system
   * packages are divided into 4 categories:
   *   clibuild - install mandatory console interface build dependencies and main console interface tools
   *   clitools - install console interface tools
   *   guibuild - install graphical interface build dependencies and main graphical tools
   *   guitools - install graphical user interface tools
   * for console interface only is recommended to install both cli categories
   * for graphical interface is recommended to install all categories
```
./setup.dependencies.sh clibuild clitools guibuild guitools
```
   * to get more details about usage and packages please use help
```
./setup.dependencies.sh help
```

**Proxychains configuration file update**
   * update file ~/proxychains/proxychains.conf
   * to allow localhost access
   * to update SOCKS version 4 to 5
   * it is recommended step
```
./setup.cfg.proxychains.sh install
```

**Update user permissions to use tor**
   * user permissions must be updated for ability to use tor network anonymity layer
   * it is recommended step
```
su - -c "usermod -a -G debian-tor ${USER}; exit"
```
