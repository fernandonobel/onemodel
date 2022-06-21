%% Example driver script for simulating "ex05_protein_induced" model.
% This file was automatically generated by OneModel.
% Any changes you make to it will be overwritten the next time
% the file is generated.

clear all;
close all;

% Init model.
m = ex05_protein_induced();

% Solver options.
opt = odeset('AbsTol',1e-8,'RelTol',1e-8);
opt = odeset(opt,'Mass',m.M);

% Simulation time span.
tspan = [m.opts.t_init m.opts.t_end];

[t,x] = ode15s(@(t,x) m.ode(t,x,m.p),tspan,m.x0,opt);
out = m.simout2struct(t,x,m.p);

% Plot result.
m.plot(out);
