FROM jupyter/scipy-notebook:hub-2.1.1

WORKDIR /workdir
EXPOSE 8888

# python package installation
RUN pip install jupyterlab_vim && \
    pip install openpyxl && \
    pip install japanize-matplotlib && \
    pip install cmocean

RUN pip install twine && \
    pip install wheel
