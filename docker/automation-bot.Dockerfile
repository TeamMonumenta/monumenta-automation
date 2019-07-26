FROM debian:stable

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-yaml python3-kubernetes python3-pip && \
	pip3 install discord.py

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

COPY quarry $USERHOME/MCEdit-And-Automation/quarry
COPY discord_bots $USERHOME/MCEdit-And-Automation/discord_bots
COPY utility_code $USERHOME/MCEdit-And-Automation/utility_code

WORKDIR $USERHOME/MCEdit-And-Automation
CMD ["./discord_bots/server_shell_bots/bot.py"]
