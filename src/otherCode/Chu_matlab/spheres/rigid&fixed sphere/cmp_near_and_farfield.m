%% compare the backscattering of a rigid&fixed sphere
% from a nearfield and farfield

clear

[p, ~, ~] = fileparts(mfilename('fullpath'));
addpath(fullfile(p, '../functions'))

a = 0.25;               % radius of the sphere
out_flag = 2;           % complex form function
scale = 1;				% linear spacing in ka
n=100;					% number of computation points 
r_to_a = 100;          % ratio of receiver range to the radius of the sphere

%% scattering pattern
proc_flag = 1;			% 1 = vs ka; 2 = vs angle

if proc_flag == 1
    theta = 180;				% backscattering
    x0 = 0.1;					% starting ka value
    xe = 10;					    % end ka value
    para_rgd_ff = [n x0 xe theta round(xe)+10];
    [ka, fs_ff] = rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd_ff);
    para_rgd_nf = [n x0 xe theta round(xe)+10 r_to_a];
    [ka, ps_nf] = nf_rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd_nf);
    ps_ff = ps_nf*r_to_a/(2*a);
    figure(1)
    plot(ka, abs(ps_ff), '.-')
    hold on
    plot(ka, abs(fs_ff), '-or')
    hold off    
    legend('Normalized Near Field', 'Farfield', 'location', 'southeast')
    xlabel('ka')
else    
    ka = 1;				        % backscattering
    ang_0 = 0;					% starting ka value
    ang_e = 360;			    % end ka value
    para_rgd_ff = [n ang_0 ang_e ka round(ka)+10];
    [th, fs_ff] = rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd_ff);
    para_rgd_nf = [n ang_0 ang_e ka round(ka)+10 r_to_a];
    [th, ps_nf] = nf_rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd_nf);
    ps_ff = ps_nf*r_to_a/(2*a);
    figure(1)
    polarplot(th, abs(ps_ff), '.-')
    hold on
    polarplot(th, abs(fs_ff), 'or')
    hold off    
    legend('Normalized Near Field', 'Farfield')
end



