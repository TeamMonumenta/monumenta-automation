FROM debian:stable

RUN apt-get update && \
	apt-get install -y git tree ncdu curl wget openssh-server vim

# Check for mandatory build arguments
ARG USERNAME
ARG PASS
ARG UID
ARG GID
RUN : "${USERNAME:?'USERNAME' argument needs to be set and non-empty.}"
RUN : "${UID:?'UID' argument needs to be set and non-empty.}"
RUN : "${GID:?'GID' argument needs to be set and non-empty.}"
RUN : "${PASS:?'PASS' argument needs to be set and non-empty.}"

ENV USERHOME /home/$USERNAME

RUN groupadd --non-unique -g $GID $USERNAME && \
	# NOTE! -l flag prevents creation of gigabytes of sparse log file for some reason
	useradd -lmNs /bin/bash -u $UID -g $GID $USERNAME && \
	mkdir /var/run/sshd && \
	echo "$USERNAME:$PASS" | chpasswd && \
	mkdir $USERHOME/.ssh && \
	echo "\
Port 22                                                \n\
PermitRootLogin no                                     \n\
PasswordAuthentication yes                             \n\
ChallengeResponseAuthentication no                     \n\
UsePAM yes                                             \n\
AllowAgentForwarding yes                               \n\
AllowTcpForwarding no                                  \n\
GatewayPorts no                                        \n\
X11Forwarding no                                       \n\
PrintMotd no                                           \n\
TCPKeepAlive yes                                       \n\
PermitTunnel no                                        \n\
AcceptEnv LANG LC_*                                    \n\
Subsystem       sftp    /usr/lib/openssh/sftp-server   \n\
AllowUsers $USERNAME" > /etc/ssh/sshd_config

COPY authorized_keys $USERHOME/.ssh/authorized_keys

RUN chown -R $USERNAME:$USERNAME $USERHOME/.ssh && \
	chmod go-rwx $USERHOME/.ssh

EXPOSE 22

USER root
CMD ["/usr/sbin/sshd", "-D"]
