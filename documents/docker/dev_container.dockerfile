FROM ubuntu: latest

# BASIC SETUP ~~~~~~~~~~~~~~~~~
WORKDIR /root
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y vim
RUN apt-get install -y wget
RUN apt-get install -y unzip
RUN rm -rf /var/lib/apt/lists/*

# ARG VARIABLES ~~~~~~~~~~~~~~~~~
WORKDIR /root
# pass in arguments from local machine using --build-arg flag for sensitive information
ARG OPENAI_KEY

# ENV VARIABLES ~~~~~~~~~~~~~~~~~
# set passed arguments as environment variables
WORKDIR /root
ENV OPENAI_KEY=$OPENAI_KEY

# MAKE DIRECTORIES ~~~~~~~~~~~~~~~~~
# make directories
WORKDIR /root
RUN mkdir /root/documents
RUN mkdir /root/documents/repos
RUN mkdir /root/documents/mount
RUN mkdir /root/downloads

# MOUNT POINTS ~~~~~~~~~~~~~~~~~
# declaring mount point does nothing. Reminder to use -v flag when running container
WORKDIR /root
VOLUME /root/documents/mount

# CLONE ALL GIT REPOS ~~~~~~~~~~~~~~~~~
WORKDIR /root/documents/repos
# clone all git repos
COPY clone_all_repos.sh .
RUN chmod +x clone_all_repos.sh
RUN ./clone_all_repos.sh
RUN rm clone_all_repos.sh


# # VSCODE INSIDERS SETUP ~~~~~~~~~~~~~~~~~

# # install vscode insiders

# WORKDIR /root

# RUN curl -L https://code.visualstudio.com/sha/download?build=insider&os=linux-deb-×64 -o vscode.deb
# RUN apt install ./vscode.deb -y
# RUN rm vscode.deb

# CONDA SETUP ~~~~~~~~~~~~~~~~~
# install miniconda
WORKDIR /root
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-×86_64.sh
RUN bash Miniconda3-latest-Linux-×86_64.sh -b -p /opt/conda
RUN rm Miniconda3-latest-Linux-×86_64.sh
ENV PATH="/opt/conda/bin:${PATH}"
# Make /opt/conda world-writable to allow hardlinks during tests
RUN chmod -R o+w /opt/conda/pkgs/*-*-*

# configure conda channels
RUN conda config --add channels conda-forge
RUN conda config --set channel_priority strict

# # update conda base using environment.yml on local machine
# COPY environment.yml
# RUN conda env update --file environment.yml -n base --prune
# RUN conda clean -afy

# # create new coda environment using environment.ym] on local machine
# COPY environment.yml
# RUN conda env create -f environment.yml
# set conda base as default environment in bash
# https://pythonspeed.com/articles/activate-conda-dockerfile/
RUN touch /root/.bashrc
RUN echo "conda activate base" ›› /root/.bashrc

# run subsequent commands in conda base environment
SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]
# install conda packages
RUN conda install -y python=3.11.3
RUN conda install -y pip
RUN conda install -y jupyterlab
RUN conda install -y ipywidgets
RUN conda install -y ipykernel
RUN conda install -y pandas
RUN conda install -y numpy
RUN conda install -y matplotlib
RUN conda clean -afy

# END SETUP ~~~~~~~~~~~~~~~~~
WORK /root/documents
RUN echo "Welcome!"

# open as a dev remote in vscode-insiders
# CMD ["code-insiders", "."]

# open as bach terminal
CMD ["bash"]