FROM openjdk:17-jdk-buster

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-yaml python3-pip python3-setuptools python3-numpy && \
	pip3 install wheel && \
	pip3 install "bitstring<4.1.0" mutf8 && \
	pip3 install -U pyyaml && \
	cd /opt && \
	wget https://downloads.python.org/pypy/pypy3.8-v7.3.9-linux64.tar.bz2 && \
	tar xjf pypy3.8-v7.3.9-linux64.tar.bz2 && \
	rm -f pypy3.8-v7.3.9-linux64.tar.bz2 && \
	ln -s /opt/pypy3.8-v7.3.9-linux64/bin/pypy3 /usr/local/bin/pypy3 && \
	ln -s /opt/pypy3.8-v7.3.9-linux64/bin/pypy /usr/local/bin/pypy && \
	wget https://bootstrap.pypa.io/get-pip.py && \
	pypy3 get-pip.py && \
	rm -f get-pip.py && \
	pypy3 -m pip install wheel && \
	pypy3 -m pip install "bitstring<4.1.0" mutf8 && \
	pypy3 -m pip install -U pyyaml

COPY quarry /automation/quarry
COPY utility_code /automation/utility_code

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

COPY docker/monumenta.sh /
RUN chmod +x /monumenta.sh

USER $USERNAME
WORKDIR $USERHOME
CMD ["/monumenta.sh"]
