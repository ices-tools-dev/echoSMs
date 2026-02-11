% The Zooplankton BackScattering (ZBS) program package is GUI driven 
% software to computing acoustic backscattering by weakly scattering 
% zooplankton in terms of various parameters such as nagle of orientation, 
% size and material properties.
% 
% Witten by Dezhang Chu, Woods Hole Oceanographic Institution
%	June 21, 1999
%  
%% This program is distributed in the hope that it will be useful, 
% but WITHOUT ANY WARRANTY.

%% Contact Dr. Chu at dchu@whoi.edu with enhancements or suggestions for changes.


clear all
global para status misc dat

para.info.home_dir=pwd;

addpath(genpath(para.info.home_dir))
misc.cw=1500;
h=config;
