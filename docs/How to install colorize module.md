# 上色的配置
## Torch7 ：
1. gcc g++ 6 版本：
apt gcc-6 和 g++-6
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-6 10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 10
2. 编译错误 `export TORCH_NVCC_FLAGS="-D__CUDA_NO_HALF_OPERATORS__`
3. nn 模块：[https://www.cnblogs.com/darkknightzh/p/5653864.html](https://www.cnblogs.com/darkknightzh/p/5653864.html)
4. image 和 nngraph 按照 github 安装 `luarocks install xxx` 即可
5. 安装的包：
`libjpeg 
sudo apt install libqt4-designer libqt4-opengl libqt4-svg libqtgui4 libqtwebkit4 libgraphicsmagick1-dev nodejs npm libfftw3-dev sox libsox-dev libsox-fmt-all`

参考脚本：
```sh
 sudo apt-get update
        # python-software-properties is required for apt-add-repository
        sudo apt-get install -y python-software-properties
        echo "==> Found Ubuntu version ${ubuntu_major_version}.xx"
        if [[ $ubuntu_major_version -lt '12' ]]; then
            echo '==> Ubuntu version not supported.'
            exit 1
        elif [[ $ubuntu_major_version -lt '14' ]]; then
            sudo add-apt-repository -y ppa:chris-lea/zeromq
            sudo add-apt-repository -y ppa:chris-lea/node.js
        elif [[ $ubuntu_major_version -lt '15' ]]; then
            sudo add-apt-repository -y ppa:jtaylor/ipython
        else
            sudo apt-get install -y software-properties-common \
                libgraphicsmagick1-dev nodejs npm libfftw3-dev sox libsox-dev \
                libsox-fmt-all
        fi

        gcc_major_version=$(gcc --version | grep ^gcc | awk '{print $4}' | \
                            cut -c 1)
        if [[ $gcc_major_version == '5' ]]; then
            echo '==> Found GCC 5, installing GCC 4.9.'
            sudo apt-get install -y gcc-4.9 libgfortran-4.9-dev g++-4.9
        fi

        sudo apt-get update
        sudo apt-get install -y build-essential gcc g++ curl \
            cmake libreadline-dev git-core libqt4-core libqt4-gui \
            libqt4-dev libjpeg-dev libpng-dev ncurses-dev \
            imagemagick libzmq3-dev gfortran unzip gnuplot \
            gnuplot-x11 ipython libreadline-dev

        if [[ $ubuntu_major_version -lt '14' ]]; then
            # Install from source after installing git and build-essential
            install_openblas || true
        else
            sudo apt-get install -y libopenblas-dev liblapack-dev
        fi
```
6. 模块测试 `th colorize.lua  sm_jw.jpg out_sm_jw.jpg`
# 参考
[编译错误 issue](https://github.com/torch/cutorch/issues/797)