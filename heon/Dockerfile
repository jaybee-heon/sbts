# 기본 이미지로 Ubuntu 최신 버전 사용
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    git \
    openjdk-8-jdk \
    subversion \
    perl \
    build-essential \
    wget \
    make \
    curl \
    unzip \
    python3 \
    python3-pip \
    vim

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install tqdm --break-system-packages

# JAVA_HOME 환경 변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

ENV PERL_MM_USE_DEFAULT=1

RUN echo "yes" | cpan \
    && cpan App::cpanminus \
        && cpan DBI@1.643 DBD::CSV@0.58 URI@1.76 JSON@2.97 JSON::Parse@0.55 List::Util@1.50

WORKDIR /app

RUN git clone https://github.com/jaybee-heon/defects4j.git
WORKDIR /app/defects4j
RUN cpanm --installdeps .

RUN ./init.sh
ENV PATH="${PATH}:/app/defects4j/framework/bin"

# 컨테이너 실행 시 기본 명령 설정
CMD ["/bin/bash"]
