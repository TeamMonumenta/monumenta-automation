FROM debian:stable

RUN apt-get update && \
	apt-get install -y git tree ncdu curl wget openssh-server rsync vim

# Check for mandatory build arguments
ARG USERNAME
ARG UID
ARG GID
RUN : "${USERNAME:?'USERNAME' argument needs to be set and non-empty.}"
RUN : "${UID:?'UID' argument needs to be set and non-empty.}"
RUN : "${GID:?'GID' argument needs to be set and non-empty.}"

ENV USERHOME=/home/$USERNAME

RUN groupadd --non-unique -g $GID $USERNAME && \
	# NOTE! -l flag prevents creation of gigabytes of sparse log file for some reason
	useradd -lmNs /bin/bash -u $UID -g $GID $USERNAME && \
	mkdir -p /var/run/sshd && \
	mkdir -p $USERHOME/.ssh && \
	echo "\
Port 22                                                \n\
PermitRootLogin no                                     \n\
PasswordAuthentication no                              \n\
ChallengeResponseAuthentication no                     \n\
UsePAM yes                                             \n\
AllowAgentForwarding yes                               \n\
AllowTcpForwarding yes                                 \n\
GatewayPorts no                                        \n\
X11Forwarding no                                       \n\
PrintMotd no                                           \n\
TCPKeepAlive yes                                       \n\
PermitTunnel no                                        \n\
AcceptEnv LANG LC_*                                    \n\
Subsystem       sftp    /usr/lib/openssh/sftp-server   \n\
AllowUsers $USERNAME" > /etc/ssh/sshd_config && \
echo 'if [[ -e "$HOME/.localrc" ]]; then source "$HOME/.localrc"; fi' >> $USERHOME/.bashrc

RUN chown -R $USERNAME:$USERNAME $USERHOME/.ssh && \
	chmod go-rwx $USERHOME/.ssh

COPY image_config/basic-ssh-dev/USERHOME/.localrc $USERHOME/.localrc
RUN chown $USERNAME:$USERNAME $USERHOME/.localrc
RUN chmod 664 $USERHOME/.localrc

EXPOSE 22

USER root
CMD ["/usr/sbin/sshd", "-D"]
