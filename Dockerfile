FROM ubuntu:20.10

LABEL MAINTAINER abel.siqueira@esciencecenter.nl
ENV container docker

RUN mkdir /app
WORKDIR /app

# PACKAGES
#===========================================
RUN rm -f /etc/localtime && \
    ln -s /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y gcc git make cmake wget build-essential libssl-dev zlib1g-dev \
       libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
       libncurses5-dev libncursesw5-dev xz-utils tk-dev


# INSTALL PYTHON
#===========================================
RUN wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tgz && \
    tar -zxf Python-3.9.9.tgz && \
    cd Python-3.9.9 && \
    ./configure --with-ensurepip=install --enable-shared && make && make install && \
    ldconfig && \
    ln -sf python3 /usr/local/bin/python
ENV PYTHON /usr/bin/python

# INSTALL JULIA
RUN wget https://raw.githubusercontent.com/abelsiqueira/jill/main/jill.sh && \
    bash /app/jill.sh -y -v 1.6.4 && \
    julia -e 'using Pkg; Pkg.add("PyCall"); Pkg.add("Parsers")'

RUN python -m pip install --upgrade pip && \
    python -m pip install julia matplotlib numpy pandas pybind11[global] && \
    python -c 'import julia; julia.install()'

# INSTALL C++ (and packages)
RUN wget https://github.com/xtensor-stack/xtl/archive/refs/tags/0.7.4.tar.gz -O xtl.tar.gz && \
    tar -zxf xtl.tar.gz && \
    cd /app/xtl-0.7.4 && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr && \
    make install

RUN wget https://github.com/xtensor-stack/xtensor/archive/refs/tags/0.24.0.tar.gz -O xtensor.tar.gz && \
    tar -zxf xtensor.tar.gz && \
    cd /app/xtensor-0.24.0 && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr && \
    make install

RUN wget https://github.com/xtensor-stack/xtensor-python/archive/refs/tags/0.26.0.tar.gz -O xtensor-python.tar.gz && \
    tar -zxf xtensor-python.tar.gz && \
    cd /app/xtensor-python-0.26.0 && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr && \
    make install

RUN git clone https://github.com/TICCLAT/ticcl-output-reader && \
    python -m pip install ./ticcl-output-reader
COPY scalability_test.py scalability_analysis.py jl_* /app/


# CLEAN UP
#===========================================

RUN rm -rf /var/cache/pacman/pkg/* /app/jill.sh /opt/julias/*.tar.gz /app/*.tar.gz

ENTRYPOINT ["python", "-u", "/app/scalability_test.py"]
CMD ["2"]


# docker run --rm --volume "./gen-data:/app/gen-data" --volume "./out:/app/out" jl-from-py:0.1.0