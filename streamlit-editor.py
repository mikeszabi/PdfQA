# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 10:31:23 2023

@author: Szabi
"""

import streamlit as st

from streamlit_ace import st_ace

# Spawn a new Ace editor
content = st_ace()

# Display editor's content as you type
content