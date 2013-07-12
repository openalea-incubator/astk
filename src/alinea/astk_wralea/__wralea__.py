
# This file has been generated at Tue Jul 02 10:08:48 2013

from openalea.core import *


__name__ = 'alinea.astk'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '1.0.0'
__authors__ = ''
__institutes__ = None
__icon__ = ''


__all__ = ['astk_TimeControl_TimeControl']



astk_TimeControl_TimeControl = Factory(name='TimeControl',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='alinea.astk.TimeControl',
                nodeclass='TimeControl',
                inputs=[{'interface': IInt, 'name': 'delay', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'steps', 'value': None, 'desc': ''}, {'interface': None, 'name': 'model', 'value': None, 'desc': ''}, {'interface': None, 'name': 'weather', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'start_date', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'out', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




