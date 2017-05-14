#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import colorlog
import os

from logging.handlers import RotatingFileHandler

def getLogger(name='tw', file_level = logging.INFO, stream_level = logging.WARNING):
    if file_level == 'DEBUG':
        file_level = logging.DEBUG
    elif file_level == 'INFO':
        file_level = logging.INFO
    elif file_level == 'WARNING':
        file_level = logging.WARNING
    elif file_level == 'ERROR':
        file_level = logging.ERROR
    elif file_level == 'CRITICAL':
        file_level = logging.CRITICAL

    if stream_level == 'DEBUG':
        stream_level = logging.DEBUG
    elif stream_level == 'INFO':
        stream_level = logging.INFO
    elif stream_level == 'WARNING':
        stream_level = logging.WARNING
    elif stream_level == 'ERROR':
        stream_level = logging.ERROR
    elif stream_level == 'CRITICAL':
        stream_level = logging.CRITICAL
    log_file = './logs/%s.log'%name

    # création de l'objet logger qui va nous servir à écrire dans les logs
    log = logging.getLogger(name)
    if log.handlers:
        return log
    # on met le niveau du logger à DEBUG, comme ça il écrit tout
    log.setLevel(logging.INFO)

    # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    # création d'un handler qui va rediriger une écriture du log vers
    # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
    file_handler = RotatingFileHandler(log_file, 'w', 10000000, 50, encoding='utf8')
    # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
    # créé précédement et on ajoute ce handler au logger
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    # création d'un second handler qui va rediriger chaque écriture de log
    # sur la console
    stream_handler = colorlog.StreamHandler()
    colored_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(message)s',
        log_colors={
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        }
    )
    stream_handler.setFormatter(colored_formatter)
    stream_handler.setLevel(stream_level)
    log.addHandler(stream_handler)
    return log
