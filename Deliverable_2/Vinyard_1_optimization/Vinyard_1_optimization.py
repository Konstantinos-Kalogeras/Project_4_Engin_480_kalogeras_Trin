import numpy as np
from topfarm.cost_models.cost_model_wrappers import CostModelComponent
from topfarm import TopFarmProblem
from topfarm.plotting import NoPlot, XYPlotComp
from topfarm.easy_drivers import EasyScipyOptimizeDriver
from topfarm.constraint_components.boundary import XYBoundaryConstraint
from topfarm.constraint_components.spacing import SpacingConstraint
import topfarm

from py_wake.literature.gaussian_models import Bastankhah_PorteAgel_2014, Zong_PorteAgel_2020, Niayifar_PorteAgel_2016, CarbajoFuertes_etal_2018, Blondel_Cathelain_2020
from py_wake.utils.gradients import autograd
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine
from py_wake.site.shear import PowerShear
import pickle
from Vinyard_wind.Vinyard_Wind_1_quardinates_and_boundarys import VinyardWind2, Haliade_X


with open('utm_boundary.pk1', 'rb') as f:
    boundary = np.array(pickle.load(f))

with open('utm_layout.pk1', 'rb') as f:
    xinit,yinit = np.array(pickle.load(f))


maxiter = 1000
tol = 1e-6


turbine = Haliade_X()

site = VinyardWind2()

sim_res = Bastankhah_PorteAgel_2014(site, turbine, k = 0.0324555)
    
def aep_func(x,y):
        # sim_res = Bastankhah_PorteAgel_2014(VinyardWind2(), Haliade_X(), k = 0.0324555)
        aep = sim_res(x,y).aep().sum()
        return aep
    
boundary_closed = np.vstack([boundary, boundary[0]])

cost_comp = CostModelComponent(input_keys=['x', 'y'],
                                          n_wt = len(xinit),
                                          cost_function = aep_func,
                                          objective=True,
                                          maximize=True,
                                          output_keys=[('AEP', 0)]
                                          )
    
problem = TopFarmProblem(design_vars= {'x': xinit, 'y': yinit},
                         constraints=[XYBoundaryConstraint(boundary),
                                      SpacingConstraint(334)],
                        cost_comp=cost_comp,
                        driver=EasyScipyOptimizeDriver(optimizer='SLSQP', maxiter=maxiter, tol=tol),
                        n_wt=len(xinit),
                        expected_cost=0.001,
                        plot_comp=XYPlotComp()
                        )


cost, state, recorder = problem.optimize()

recorder.save('optimization_revwind')

print('done')

print('done')
