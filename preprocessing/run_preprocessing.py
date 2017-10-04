#  -*- coding: utf-8 -*-
import xml.sax
import xml.etree.ElementTree as ET
import re
import pickle
from operator import itemgetter
import os.path
import sys
import codecs
import numpy as np
import collections as col
import preprocessing


parser = xml.sax.make_parser()
parser.setContentHandler(WikiContentHandler())
parser.parse(open("../../../wikipedia/enwiki-20170820-pages-meta-current.xml","r", encoding="utf8"))

