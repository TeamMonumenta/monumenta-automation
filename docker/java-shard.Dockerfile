FROM openjdk:8-jdk-stretch

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

COPY monumenta.sh /
RUN wget "http://builds.enginehub.org/job/warmroast/4523/download/warmroast-1.0.0-SNAPSHOT.jar" && \
	chmod +x /monumenta.sh

USER $USERNAME
WORKDIR $USERHOME
CMD ["/monumenta.sh"]