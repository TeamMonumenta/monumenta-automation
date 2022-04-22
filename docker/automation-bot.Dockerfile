FROM ubuntu:20.04

RUN apt-get update && \
	apt-get install -y build-essential curl

# Install redis tools
RUN cd /tmp && \
	curl -O https://download.redis.io/releases/redis-5.0.14.tar.gz && \
	tar xzf redis-5.0.14.tar.gz && \
	cd redis-5.0.14 && \
	make -j 4 && \
	make install

FROM ubuntu:20.04

RUN apt-get update && \
	apt-get install -y software-properties-common && \
	add-apt-repository -y ppa:pypy/ppa && \
	apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-yaml python3-pip python3-setuptools python3-numpy zip unzip pigz python3-dev libtool curl liblz4-tool netcat pypy3 && \
	rm -rf /var/lib/apt/lists/*

RUN pip3 install wheel && \
	pip3 install discord.py kubernetes pika "redis<4.2.0" bitstring kanboard flask mutf8 && \
	pip3 install -U pyyaml

# Install rclone
RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip && \
	unzip rclone-current-linux-amd64.zip && \
	cd rclone-*-linux-amd64 && \
	cp rclone /usr/bin/ && \
	chown root:root /usr/bin/rclone && \
	chmod 755 /usr/bin/rclone && \
	rclone --version

# Install redis-cli from container 0
COPY --from=0 /usr/local/bin/redis-cli /usr/local/bin/redis-cli

# Check for mandatory build arguments
ARG USERNAME
ARG UID
ARG GID
RUN : "${USERNAME:?'USERNAME' argument needs to be set and non-empty.}"
RUN : "${UID:?'UID' argument needs to be set and non-empty.}"
RUN : "${GID:?'GID' argument needs to be set and non-empty.}"

ENV USERHOME /home/$USERNAME

RUN groupadd --non-unique -g $GID $USERNAME && \
	# NOTE! -l flag prevents creation of gigabytes of sparse log file for some reason
	useradd -lmNs /bin/bash -u $UID -g $GID $USERNAME

USER $USERNAME

RUN cd /tmp && \
	curl -O https://bootstrap.pypa.io/get-pip.py && \
	pypy3 get-pip.py && \
	rm get-pip.py && \
	pypy3 -m pip install wheel pika redis bitstring kanboard flask mutf8 pyyaml

ENV PYTHONIOENCODING UTF-8

COPY quarry $USERHOME/MCEdit-And-Automation/quarry
COPY rust/bin $USERHOME/MCEdit-And-Automation/rust/bin
COPY leaderboards.yaml $USERHOME/MCEdit-And-Automation/leaderboards.yaml
COPY discord_bots $USERHOME/MCEdit-And-Automation/discord_bots
COPY utility_code $USERHOME/MCEdit-And-Automation/utility_code

WORKDIR $USERHOME/MCEdit-And-Automation
CMD ["./discord_bots/automation_bot/automation_bot.py"]
