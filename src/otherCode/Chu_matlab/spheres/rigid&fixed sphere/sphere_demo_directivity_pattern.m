%% demo program to compute backscattering form function and Target strength of a rigid&fixed sphere

clear

addpath('functions')

a=0.25;
out_flag=2;				% complex form function
scale=1;				% linear spacing in ka


proc_flag=2;			% form function vs angle
n=200;					% number of computation points 
ka=1;				% backscattering

ang_0=0;					% starting ka value
ang_e=360;					    % end ka value
para_rgd=[n ang_0 ang_e ka round(ka)+10];
[th, fm]=rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd);

figure(1)
polar(th, abs(fm))



