# Start from a CUDA base image
FROM nvidia/cuda:11.0.3-base-ubuntu20.04

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Install vim 
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*

# Install libopenmpi 
RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get install -y libopenmpi-dev && \
	rm -rf /var/lib/apt/lists/*

# Install libxrender
RUN apt-get update && \
	apt-get install libxrender1 && \
	rm -rf /var/lib/apt/lists/*

# Install Python and modules from molDQN requirements.txt
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    pip3 install --upgrade pip && \
    pip3 install jupyter && \
    pip3 install absl-py==2.0.0 && \
    pip3 install networkx==3.1 && \
    pip3 install numpy==1.24.3 && \
    pip3 install rdkit==2023.09.1 && \
    pip3 install tensorflow==2.13.1 && \    
    pip3 install tf_slim==1.1.0 && \ 
    pip3 install scipy==1.10.1 && \
    pip3 install gym==0.26.2 && \
    pip3 install pandas==2.0.0 && \
    pip3 install lightgbm==3.3.5 && \
    pip3 install xgboost==1.0.2 && \
    rm -rf /var/lib/apt/lists/* 

# Set the working directory
WORKDIR /workspace

# Clone rl_mol_gen git repo
RUN git clone -b master https://github.com/AsyaOrlova/rl_mol_gen.git

# Clone RAscore git repo
RUN git clone -b master https://github.com/reymond-group/RAscore.git

# Set environmental variables
ENV PYTHONPATH=/workspace/rl_mol_gen/:$PYTHONPATH
ENV PYTHONPATH=/workspace/RAscore/:$PYTHONPATH

# Change optimizers.py in tf_slim
COPY ./optimizers.py /usr/local/lib/python3.8/dist-packages/tf_slim/layers

# Set the default command
CMD ["/bin/bash"]