%% demo program to call elastic_fs.m

clear

addpath(genpath('C:/bin'))% matlab Sphere  -end

out_flag=1;				% complex form function
scale=1;				% linear spacing in ka
proc_flag=2;			% form function vs ka
n=1000;					% number of computation points 
theta=0.8378;				% backscattering

object_index=1;
switch object_index
    case 3
        %% stainless steel
        g=7.8;					% density ratio
        hc=3.74;			    % compressional sound speed contrast
        hs=2.08;			    % sheer speed contrast
        x0=0.01;					% starting ka value
        xe=30;					% end ka value
        g=14.9160;
        hc=4.6135;
        hs=2.8312;
%         x0=0.1;
%         xe=50;
        Nmax=round(xe)+10;
        para_ela=[n x0 xe g hc hs theta Nmax];
        [ka, fm]=elastic_fs(proc_flag,scale,out_flag,para_ela);
    case 2
        %% bubble at surface
        x0=0.001;			    % starting ka value
        xe=20;					% end ka value
        g=0.0012;h=0.22;ka0=1;
        para_fld=[n x0 xe g h theta];
        scale=2;                % log scale
        [ka, fm]=fluid_fs(proc_flag,scale,out_flag,para_fld);
    case 1   % ridig & fixed
        if proc_flag == 1
            x0=0.01;					% starting ka value
            xe=30;					    % end ka value
            para_rgd=[n x0 xe theta round(xe)+20];
        else
            th0 = 0;
            th1 = 360;
            ka0 = theta;
            para_rgd=[n th0 th1 ka0 round(ka0)+20];
        end
        [ka, fm]=rgd_sft_fs(proc_flag,1,scale,out_flag,para_rgd);
end

figure(1)
if proc_flag == 1
    if scale == 1
        plot(ka,abs(fm),'linewidth',1.5)
        xlabel('ka')
    else
        loglog(ka,abs(fm),'linewidth',1.5)
        xlabel('ka')
    end
    ylabel('Form Function |f|')
    
    figure(2)
    RTS=20*log10(abs(fm));
    if scale == 1
        plot(ka,RTS,'linewidth',1.5)
        xlabel('ka')
    else
        semilogx(ka,RTS,'linewidth',1.5)
        xlabel('ka')
    end
    ylabel('Reduced TS (dB)')
    grid
else
    ths = ka;
    amp = abs(fm);
    polar(ths, amp)
end

