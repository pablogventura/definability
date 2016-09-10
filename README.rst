Definability
================================================


Instalación
-----------

1. Se necesita el siguiente software:

   - Git
   - Pip
   - Ant
   - Python 3.4 o posterior
   - `Jython <http://www.jython.org/downloads.html>`_ en ~/jython2.7.0 (descargar y hacer 'java -jar jython_installer-2.7.0.jar')
   - Virtualenv
   - `Minion 1.8 <http://constraintmodelling.org/minion/download/>`_ en ~/minion-1.8/bin/minion
   - `LADR 2009 11A <https://www.cs.unm.edu/~mccune/mace4/download/>`_ en ~/LADR-2009-11A/bin
   - `LatDraw 2.0 <http://www.latdraw.org/>`_ en ~/LatDraw2.0/dist/lib (descargar el source en tar y compilar con ant dist)
   - `UACalc <http://www.uacalc.org/>`_ en ~/uacalccli (descargar el source de github y compilar con ant dist)

   En un sistema basado en Debian (como Ubuntu), se puede hacer::

    sudo apt-get install git python-pip python3.4 python3-tk virtualenv ant


2. Crear y activar un nuevo
   `virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`_.
   usando `virtualenvwrapper
   <http://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation>`_.
   Se puede instalar así::

    sudo pip install virtualenvwrapper

   Y luego agregando la siguiente línea al final del archivo ``.bashrc``::

    [[ -s "/usr/local/bin/virtualenvwrapper.sh" ]] && source "/usr/local/bin/virtualenvwrapper.sh"

   Para crear y activar nuestro virtualenv::

    mkvirtualenv --system-site-packages --python=/usr/bin/python3.4 py3def

3. Bajar el código::

    git clone https://github.com/pablogventura/definability.git
   


4. Instalarlo::

    cd definability/
   
   Para instalar Minion, LADR y LatDraw en el Home se puede usar el script install.sh con::
   
    ./install.sh
   
   Para instalar UACalcCli se puede usar el script installuacalccli con::
   
    ./installuacalccli
   
   Para instalar los paquetes Python que utiliza Definability::
   
    pip install -r requirements.txt


Ejecución
---------

1. Activar el entorno virtual con::

    workon py3def

2. Al correr python ya se corre Python 3

3. Para correr ipython en Python 3 correr ipython3

4. Para correr el interprete interactivo para Definability basta con correr::

    python main.py

Nombres de versiones
--------------------

Segun `Semantic Versioning <http://semver.org/>`_.

Testing
-------

Correr nose::

    nosetests


Chequear Estilo de Código
-------------------------

Correr flake8 sobre el paquete o módulo que se desea chequear. Por ejemplo::

    flake8
