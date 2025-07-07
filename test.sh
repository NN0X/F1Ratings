#!/bin/bash
source venv/bin/activate
python main.py gen
python main.py dump
python main.py print
python main.py plot 'Max Verstappen' 'Juan Fangio' 'Fernando Alonso' 'Lewis Hamilton' 'Sebastian Vettel' 'Niki Lauda' 'Alain Prost' 'Lance Stroll' 'Andrea de Cesaris'
