# Copyright (C) 2012  Alex Nitz, Josh Willis
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#
"""
These are the unittests for the pycbc.waveform module
"""
import sys
import pycbc
import unittest
from pycbc.types import *
from pycbc.scheme import *
from pycbc.filter import *
from pycbc.waveform import *
import pycbc.fft
import numpy
from utils import parse_args_all_schemes, simple_exit

_scheme, _context = parse_args_all_schemes("Waveform")

class TestWaveform(unittest.TestCase):
    def setUp(self,*args):
        self.context = _context
        self.scheme = _scheme

    def test_generation(self):
        with self.context:
            for waveform in td_approximants():
                print waveform
                hc,hp = get_td_waveform(approximant=waveform,mass1=20,mass2=20,delta_t=1.0/4096,f_lower=40)
                self.assertTrue(len(hc)> 0)
            for waveform in fd_approximants():
                print waveform
                htilde, g = get_fd_waveform(approximant=waveform,mass1=20,mass2=20,delta_f=1.0/256,f_lower=40)
                self.assertTrue(len(htilde)> 0)

    def test_spatmplt(self):
        fl = 25
        delta_f = 1.0 / 256

        for m1 in [1, 1.4, 20]:
            for m2 in [1.4, 20]:
                for s1 in [-1, -.5, 0, 0.5, 1.0, 10]:
                    for s2 in [-10, -.5, 0, 0.5, 1.0]:
                        # Generate TaylorF2 from lalsimulation, restricting to the capabilities of spatmplt
                        hpr,_ = get_fd_waveform( mass1=m1, mass2=m2, spin1z=s1, spin2z=s2, delta_f=delta_f, f_lower=fl,
                        approximant="TaylorF2", amplitude_order=0, spin_order=5, phase_order=7)
                        hpr=hpr.astype(complex64)

                        with self.context:
                            # Generate the spatmplt waveform
                            out = zeros(len(hpr), dtype=complex64)
                            hp = get_waveform_filter(out, mass1=m1, mass2=m2, spin1z=s1, spin2z=s2, delta_f=delta_f, f_lower=fl, approximant="SPAtmplt", amplitude_order=0, spin_order=5, phase_order=7)
                            #import pylab
                            #pylab.plot(hp.numpy())
                            #pylab.plot(hpr.numpy())
                            #pylab.show()
                            mag = abs(hpr).sum()

                            # Check the diff is sane
                            diff = abs(hp - hpr).sum() / mag
                            self.assertTrue(diff < 0.0013)

                            # Point to point overlap (no phase or time maximization)
                            o =  overlap(hp, hpr)
                            self.assertAlmostEqual(1.0, o, places=4)

                            print "..checked m1: %s m2:: %s s1z: %s s2z: %s" % (m1, m2, s1, s2)

    def test_errors(self):
        func = get_fd_waveform
        self.assertRaises(ValueError,func,approximant="BLAH")
        self.assertRaises(ValueError,func,approximant="TaylorF2",mass1=3)
        self.assertRaises(ValueError,func,approximant="TaylorF2",mass1=3,mass2=3)
        self.assertRaises(ValueError,func,approximant="TaylorF2",mass1=3,mass2=3,phase_order=7)
        self.assertRaises(ValueError,func,approximant="TaylorF2",mass1=3,mass2=3,phase_order=7)
        self.assertRaises(ValueError,func,approximant="TaylorF2",mass1=3)

        for func in [get_fd_waveform,get_td_waveform]:
            self.assertRaises(ValueError,func,approximant="BLAH")
            self.assertRaises(ValueError,func,approximant="IMRPhenomB",mass1=3)
            self.assertRaises(ValueError,func,approximant="IMRPhenomB",mass1=3,mass2=3)
            self.assertRaises(ValueError,func,approximant="IMRPhenomB",mass1=3,mass2=3,phase_order=7)
            self.assertRaises(ValueError,func,approximant="IMRPhenomB",mass1=3,mass2=3,phase_order=7)
            self.assertRaises(ValueError,func,approximant="IMRPhenomB",mass1=3)


suite = unittest.TestSuite()
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestWaveform))

if __name__ == '__main__':
    results = unittest.TextTestRunner(verbosity=2).run(suite)
    simple_exit(results)
