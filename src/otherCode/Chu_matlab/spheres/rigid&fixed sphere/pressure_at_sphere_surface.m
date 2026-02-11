%  Simple script to compute the scattered pressure field at the surface the a
%  rigid/fixed sphere
%  Dezhang Chu, NWFGSC, NOAA Fisheries, 06 July 2017


a = 0.25;
c = 1500;
ka = 1;
r_to_a = 1;

proc_flag = 2;			% form function vs angle
obj_type = 1;           % 1 = rigid/fixed; 2 = soft
scale = 1;				% linear spacing in ka
out_flag = 2;	        % complex form function
n=361;					% number of computation points 
theta=180;				% backscattering
ang = linspace(-180, 180, n);


freq=ka.*c./(2*pi*a);
nfreq=length(freq);

% Loop over frequencies
for i=1:nfreq
    para_rgd=[n ang(1) ang(end) ka(i) round(ka(i))+10 r_to_a];
    [th, ps_i]=nf_rgd_sft_fs(proc_flag,obj_type,scale,out_flag,para_rgd);
    %% th is in radians and ps_i is the complex pressure
    ps(i,1:n) = ps_i;
    figure(1)
    h1 = plot(ang, abs(ps(i,:)), '.-', th*180/pi, abs(ps(i,:)).^2, 'or');
%     set(gca, 'ylim', [0 1])
    title(sprintf('ka = %4.2f', ka(i)))
    xlabel('ANGLE (deg)')
    ylabel('PRESSURE')
    figure(2)
    h2 = polarplot(th, abs(ps(i,:)), '-');
%     set(get(h2, 'parent'), 'xlim', 2*[-0.5 0.5], 'ylim', 2*[-0.5 0.5])
    title(sprintf('ka = %4.2f', ka(i)))
    pause(1)
end

