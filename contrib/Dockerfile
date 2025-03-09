FROM archlinux:base-devel

RUN pacman -Syu --needed --noconfirm grep sed curl git

RUN useradd -m builder && \
    echo 'builder ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/builder

USER builder

WORKDIR /home/builder

RUN git clone https://aur.archlinux.org/yay-bin.git && \
    cd yay-bin && \
    makepkg -si --noconfirm

RUN curl -SsL "$(curl -s "https://api.github.com/repos/miraikumiko/underground/releases/latest" | grep '"browser_download_url":' | sed -E 's/.*"([^"]+)".*/\1/')" -o underground-latest.pkg.tar.zst && \
    yay -S --noconfirm python-setuptools-scm python-apscheduler && \
    yay -U --noconfirm underground-latest.pkg.tar.zst

CMD ["underground"]
