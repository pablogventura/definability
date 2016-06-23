Definability
================================================


Instalación
-----------

1. Se necesita el siguiente software:

   - Git
   - Pip
   - Python 3.4 o posterior
   - Virtualenv
   - `Minion 1.8 <http://constraintmodelling.org/minion/download/>`_ en ~/minion-1.8/bin/minion
   - `LADR 2009 11A <https://www.cs.unm.edu/~mccune/mace4/download/>`_ en ~/LADR-2009-11A/bin

   En un sistema basado en Debian (como Ubuntu), se puede hacer::

    sudo apt-get install git python-pip python3.4 python3-tk virtualenv

2. Crear y activar un nuevo
   `virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`_.
   Recomiendo usar `virtualenvwrapper
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

    cd definability/package/src/definability
    pip install -r requirements.txt


Ejecución
---------

1. Activar el entorno virtual con::

    workon py3def

2. Al correr python ya se corre Python 3

3. Para correr ipython en Python 3 correr ipython3

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

    flake8 languagemodeling
