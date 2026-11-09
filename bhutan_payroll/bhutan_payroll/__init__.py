__version__ = "0.0.1"

import sys
# Alias bhutan_payroll.bhutan_payroll to this package for Frappe's report loader
sys.modules['bhutan_payroll.bhutan_payroll'] = sys.modules[__name__]