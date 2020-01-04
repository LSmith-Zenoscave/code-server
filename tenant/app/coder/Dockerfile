FROM codercom/code-server:v2

ARG CODER_USER

RUN sudo adduser --gecos '' --disabled-password ${CODER_USER}
RUN sudo bash -c "echo ${CODER_USER} ALL=\\(ALL\\) NOPASSWD:ALL >> /etc/sudoers.d/nopasswd"
RUN sudo mkdir -p /home/${CODER_USER}/.local/bin
RUN sudo mv /usr/local/bin/code-server /home/${CODER_USER}/.local/bin/code-server
RUN sudo chown -R ${CODER_USER} /home/${CODER_USER}

USER ${CODER_USER}
VOLUME ["/home/${CODER_USER}/project"]
WORKDIR "/home/${CODER_USER}"
ENTRYPOINT ["dumb-init", ".local/bin/code-server", "--host", "0.0.0.0"]
