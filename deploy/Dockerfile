FROM docker:20.10.12
FROM debian:12-slim

# can change this in k8s deployment yaml to serve from another directory
ENV PHEWEB_DIR /mnt/nfs/pheweb
ENV CLOUD_SQL_PROXY_CREDENTIAL_FILE /etc/gcp/cloud-sql-credentials.json
ENV CLOUD_SQL_PROXY_INSTANCES phewas-development:europe-west1:production-releases-pheweb-database=tcp:3306
RUN groupadd -r -g 1000 cloudsdk && \
    useradd -r -u 1000 -m -s /bin/bash -g cloudsdk cloudsdk

# create and setup the en_US.UTF-8 locale
RUN apt-get upgrade --yes && apt-get update --yes && apt-get install locales --yes
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN locale-gen en_US && locale-gen en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

RUN apt-get update --allow-releaseinfo-change
RUN apt-get install make gcc libz-dev libbz2-dev liblzma-dev zlib1g-dev  cmake libcurl4-openssl-dev  --yes

# install nodejs
RUN apt-get install curl software-properties-common gnupg --yes
RUN apt-get update; \
    apt-get install -y ca-certificates curl gnupg; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
     | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
     > /etc/apt/sources.list.d/nodesource.list; \
    apt-get -qy update; \
    apt-get -qy install nodejs;

RUN apt-get update && apt-get install --no-install-recommends texlive wget bzip2 --yes
# install cloudsql
RUN wget --no-check-certificate https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/local/bin/cloud_sql_proxy && \
    chmod +x /usr/local/bin/cloud_sql_proxy

RUN curl -LO https://github.com/samtools/htslib/releases/download/1.9/htslib-1.9.tar.bz2 && \
    tar -xvjf htslib-1.9.tar.bz2 && cd htslib-1.9 && \
    ./configure && make && make install && cd .. && rm -rf htslib-1.9*

# install gsutil
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-sdk -y

# install python packages and perquisites
RUN apt-get update && apt-get install default-libmysqlclient-dev git python3-pip python3-venv libffi-dev libz-dev  libbz2-dev liblzma-dev libssl-dev rustc --yes --fix-missing
RUN apt-get install --reinstall pkg-config cmake-data --yes --fix-missing

RUN python3 -m venv /opt/env
RUN /opt/env/bin/pip install cython
RUN /opt/env/bin/pip install --upgrade pip
ADD . /pheweb
RUN /opt/env/bin/pip install /pheweb
RUN /opt/env/bin/pip freeze

# create react js bundle
RUN cd /pheweb/ui && npm config set fetch-retries 10 && npm install
RUN cd /pheweb/ui && npm run build
RUN cp -R /pheweb/pheweb/serve/static/* /opt/env/lib/python3.11/site-packages/pheweb/serve/static/
RUN rm -r /pheweb

ADD . /pheweb
ADD pheweb/load/external_matrix.py /opt/env/bin/

# remove build tools
RUN apt-get purge git gcc rustc cmake --yes
RUN apt-get autoremove --yes
# important: add virtual environment to path
ENV PATH="/opt/env/bin:$PATH"
EXPOSE 8080
CMD cloud_sql_proxy -instances=$CLOUD_SQL_PROXY_INSTANCES -credential_file=$CLOUD_SQL_PROXY_CREDENTIAL_FILE & cd $PHEWEB_DIR && pheweb serve --port 8080 --num-workers 1
