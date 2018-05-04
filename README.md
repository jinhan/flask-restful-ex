# flask-restful-ex

### Create virtual environment
	conda create -n election python=3.6
	source activate election

### Install Prerequisites
	conda install -c conda-forge geopandas
	conda uninstall fiona
	wget https://files.pythonhosted.org/packages/cc/d9/6cd92c169f3f9837892eff6e0f4be310d6b93e3ac4125ff88d2a50c5fe0c/Fiona-1.7.11.post2-cp36-cp36m-manylinux1_x86_64.whl
	pip install Fiona-1.7.11.post2-cp36-cp36m-manylinux1_x86_64.whl
	pip install git+git://github.com/geopandas/geopandas.git
	pip install -r requirements.txt

### Run Server
	python api.py

### Usage
	/api?type=1&region=11210000
	/api?type=1&region=1&party=1&candidate=1
