FROM openjdk:8-jdk-buster

RUN apt-get update && \
	apt-get -y install maven

WORKDIR /tmp
RUN git clone https://github.com/sk89q/warmroast.git && \
	cd warmroast && \
	mvn clean install

FROM openjdk:8-jdk-buster

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

COPY --from=0 /tmp/warmroast/target/warmroast-1.0.0-SNAPSHOT.jar /
COPY monumenta.sh warmroast.sh /
RUN chmod +x /monumenta.sh /warmroast.sh

USER $USERNAME
WORKDIR $USERHOME
CMD ["/monumenta.sh"]
