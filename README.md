Introduction
============

Marcus is billingual blog engine, written Ivan Sagalaev (http://softwaremaniacs.org/about/).

Installation
============

Via pip:

<pre><code>pip install -e git://github.com/adw0rd/marcus.git#egg=marcus
</code></pre>
and install additional requirements: https://github.com/adw0rd/marcus/blob/master/requirements.txt

From sources:

<pre><code>git clone git://github.com/adw0rd/marcus.git
cd marcus
mkdir venv
virtualenv --no-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
python ./manage.py runserver 8000
</code></pre>