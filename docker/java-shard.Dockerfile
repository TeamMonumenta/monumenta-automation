FROM openjdk:16-jdk-buster

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-yaml python3-pip python3-setuptools python3-numpy && \
	pip3 install wheel && \
	pip3 install bitstring && \
	pip3 install -U pyyaml

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
