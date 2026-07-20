# This is the 'public' SSH dockerfile, which is heavily restricted.
# Used for both play/build-ssh and play/mod-ssh
# Only SFTP / file management is allowed
FROM debian:stable

# SFTP-only file server. Intentionally minimal: only openssh-server is installed
# so there is nothing to execute, compile, or fetch with even if a shell were obtained.
RUN apt-get update && \
	apt-get install -y --no-install-recommends openssh-server && \
	rm -rf /var/lib/apt/lists/*

# Check for mandatory build arguments
ARG USERNAME
ARG UID
ARG GID
RUN : "${USERNAME:?'USERNAME' argument needs to be set and non-empty.}"
RUN : "${UID:?'UID' argument needs to be set and non-empty.}"
RUN : "${GID:?'GID' argument needs to be set and non-empty.}"

ENV USERHOME /home/$USERNAME

RUN groupadd --non-unique -g $GID $USERNAME && \
	# NOTE! -l flag prevents creation of gigabytes of sparse log file for some reason.
	# nologin shell: forced internal-sftp means the shell is never invoked anyway.
	# -p '*' sets a disabled (but NOT locked) password: pubkey auth is allowed,
	# password auth is not. A locked '!' field makes sshd reject login under UsePAM no.
	useradd -lmNs /usr/sbin/nologin -p '*' -u $UID -g $GID $USERNAME && \
	# Drop the /etc/skel dotfiles copied in by useradd -m: the shell is never
	# invoked (nologin + forced internal-sftp), so they are dead files at the chroot root.
	rm -f $USERHOME/.bashrc $USERHOME/.bash_logout $USERHOME/.profile && \
	mkdir -p /var/run/sshd && \
	# Generate host keys at build time: the runtime root filesystem is read-only,
	# so keys cannot be generated on first boot.
	ssh-keygen -A && \
	mkdir $USERHOME/.ssh && \
	echo "\
Port 22                                                \n\
PermitRootLogin no                                     \n\
PasswordAuthentication no                              \n\
KbdInteractiveAuthentication no                        \n\
UsePAM no                                              \n\
UseDNS no                                              \n\
AllowAgentForwarding no                                \n\
AllowTcpForwarding no                                  \n\
GatewayPorts no                                        \n\
X11Forwarding no                                       \n\
PrintMotd no                                           \n\
TCPKeepAlive yes                                       \n\
PermitTunnel no                                        \n\
PidFile /run/sshd.pid                                  \n\
AcceptEnv LANG LC_*                                    \n\
Subsystem       sftp    internal-sftp                  \n\
AllowUsers $USERNAME                                   \n\
Match User $USERNAME                                   \n\
\tChrootDirectory $USERHOME                            \n\
\tForceCommand internal-sftp                           \n\
\tPermitTTY no" > /etc/ssh/sshd_config

# ChrootDirectory and every parent must be owned by root and not group/world
# writable. Note: chown is non-recursive, so .ssh keeps the ownership set below.
RUN chown root:root $USERHOME && \
	chmod 755 $USERHOME && \
	# .ssh must be owned/traversable by the login user: sshd reads authorized_keys
	# as that user (before chroot), so a root-owned 0700 .ssh would block it.
	chown $USERNAME:$USERNAME $USERHOME/.ssh && \
	chmod 700 $USERHOME/.ssh

EXPOSE 22

USER root
# Prepare the privilege-separation dir + pidfile location on the writable /run
# tmpfs (the root filesystem is read-only at runtime), then exec sshd.
CMD ["/bin/sh", "-c", "mkdir -p /run/sshd && chmod 0755 /run/sshd && exec /usr/sbin/sshd -D -e"]
