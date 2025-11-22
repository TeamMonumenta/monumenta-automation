FROM ubuntu:24.04

# Check for mandatory build arguments
ARG USERNAME
ARG UID
ARG GID
RUN : "${USERNAME:?'USERNAME' argument needs to be set and non-empty.}"
RUN : "${UID:?'UID' argument needs to be set and non-empty.}"
RUN : "${GID:?'GID' argument needs to be set and non-empty.}"

ENV USERHOME=/home/$USERNAME

ENV PIP_BREAK_SYSTEM_PACKAGES=true

RUN apt-get update && \
	apt-get install -y build-essential curl && \
# Install redis tools
	cd /tmp && \
	curl -O https://download.redis.io/releases/redis-7.4.0.tar.gz && \
	tar xzf redis-7.4.0.tar.gz && \
	cd redis-7.4.0 && \
	make -j 4 && \
	make install && \
	apt-get update && \
	apt-get install -y software-properties-common && \
	add-apt-repository -y ppa:pypy/ppa && \
	apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-yaml python3-pip python3-setuptools python3-numpy python3-git zip unzip pigz python3-dev libtool curl liblz4-tool netcat-openbsd pypy3 git parallel patch mariadb-client rsync wget bzip2 && \
	rm -rf /var/lib/apt/lists/* && \
	pip3 install wheel discord.py kubernetes pika "redis<4.2.0" "bitstring<4.1.0" kanboard git+https://github.com/gentlegiantJGC/mutf8.git && \
# Install rclone
	curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip && \
	unzip rclone-current-linux-amd64.zip && \
	cd rclone-*-linux-amd64 && \
	cp rclone /usr/bin/ && \
	chown root:root /usr/bin/rclone && \
	chmod 755 /usr/bin/rclone && \
	rclone --version && \
	# Remove default ubuntu user
	userdel --remove ubuntu && \
	# Add the new user
	groupadd -g $GID $USERNAME && \
	# NOTE! -l flag prevents creation of gigabytes of sparse log file for some reason
	useradd -lms /bin/bash -u $UID -g $GID $USERNAME && \
	wget https://downloads.python.org/pypy/pypy3.11-v7.3.20-linux64.tar.bz2 && \
	tar xjf pypy3.11-v7.3.20-linux64.tar.bz2 && \
	rm -f pypy3.11-v7.3.20-linux64.tar.bz2 && \
	ln -s /opt/pypy3.11-v7.3.20-linux64/bin/pypy3 /usr/local/bin/pypy3 && \
	ln -s /opt/pypy3.11-v7.3.20-linux64/bin/pypy /usr/local/bin/pypy && \
	pypy3 -m pip install wheel pika redis "bitstring<4.1.0" kanboard git+https://github.com/gentlegiantJGC/mutf8.git

# These are included in Debian (and thus Ubuntu) and need to be skipped:
	#pip3 install flask && \
	#pip3 install -U pyyaml && \
	#wget https://bootstrap.pypa.io/pip/3.8/get-pip.py && \
	#pypy3 get-pip.py && \
	#rm -f get-pip.py && \
	#pypy3 -m pip install flask && \
	#pypy3 -m pip install pyyaml

USER $USERNAME

RUN git config --global user.name "Automation Bot" && \
	git config --global user.email "monumentammo@gmail.com"

ENV PYTHONIOENCODING=UTF-8

COPY quarry $USERHOME/MCEdit-And-Automation/quarry
COPY rust/bin $USERHOME/MCEdit-And-Automation/rust/bin
COPY leaderboards.yaml $USERHOME/MCEdit-And-Automation/leaderboards.yaml
COPY discord_bots $USERHOME/MCEdit-And-Automation/discord_bots
COPY utility_code $USERHOME/MCEdit-And-Automation/utility_code

WORKDIR $USERHOME/MCEdit-And-Automation
CMD ["./discord_bots/automation_bot/automation_bot.py"]
