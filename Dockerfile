FROM stevenrbrandt/cyolauth
RUN apt-get update && apt-get install -y openjdk-16-jdk-headless python3-termcolor python3-matplotlib python3-numpy
COPY lsu-logo.png /usr/local/share/jupyterhub/static/images/logo.png
COPY login.html /usr/local/share/jupyterhub/templates/login.html
RUN mkdir -p /usr/local/python/
COPY csc4585.py /usr/local/python/
COPY bash.bashrc /etc/bash.bashrc
ENV PYTHONPATH /usr/local/python
COPY ParallelProgrammingJava.ipynb /etc/skel/
COPY ParallelProgrammingC.ipynb /etc/skel/
COPY ParallelProgrammingCC.ipynb /etc/skel/
COPY ParallelProgrammingFlour.ipynb /etc/skel/
COPY hello.ipynb /etc/skel/
COPY Lecture1.ipynb /etc/skel/
COPY startup.sh /startup.sh
COPY cyolauthenticator.py /usr/local/lib/python3.8/dist-packages/cyolauthenticator/cyolauthenticator.py
COPY flouri.jar /usr/local/
