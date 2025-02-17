#
# Wordless: Measures - Bayes Factor
#
# Copyright (C) 2018-2021  Ye Lei (叶磊)
#
# This source file is licensed under GNU GPLv3.
# For details, see: https://github.com/BLKSerene/Wordless/blob/master/LICENSE.txt
#
# All other rights reserved.
#

import math

def bayes_factor_t_test(t_statistic, number_sections):
    return t_statistic ** 2 - math.log(number_sections, math.e)

def bayes_factor_log_likelihood_ratio_test(log_likelihood_ratio, number_tokens):
    return log_likelihood_ratio - math.log(number_tokens, math.e)
