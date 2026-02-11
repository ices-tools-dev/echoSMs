% convergence study
% Dezhang Chu, NOAA Fisheries, NWFSC
% 2015-04-10

clear
addpath(genpath('C:/bin'))% matlab Sphere  -end

out_flag=2;				% complex form function
scale=1;				% linear spacing in ka
proc_flag=1;			% form function vs ka
n0=2;					% number of computation points 
theta=180;				% backscattering

ka=10;					% starting ka value
dka=1e-6;		        % end ka = ka+dka
object_index=1;
dN=40;
switch object_index
    case 1   % ridig & fixed
        para_rgd=[n0 ka ka+dka theta];
        for n=1:round(ka)+dN
            para_rgd(5)=n;
            [x, f_inf]=rgd_sft_fs(proc_flag,2,scale,out_flag,para_rgd);
            fm(n)=abs(f_inf(1));
        end
    case 2
        %% bubble at surface
        g=0.0012;h=0.2335;
        %% weakly scattering
%         g=1.002;h=1.002;
        para_fld=[n0 ka ka+dka g h theta];
        for n=1:round(ka)+dN
            para_fld(7)=n;
            [x, f_inf]=fluid_fs(proc_flag,scale,out_flag,para_fld);
            fm(n)=abs(f_inf(1));
        end
        %[ka, fm]=fluid_fs(proc_flag,scale,out_flag,para_fld);
    case 3
        %% stainless steel
        g=7.8;					% density ratio
        hc=3.74;			    % compressional sound speed contrast
        hs=2.08;			    % sheer speed contrast
        % tungsten carbide
        g=14.9160;
        hc=4.6135;
        hs=2.8312;
        para_ela=[n0 ka ka+dka g hc hs theta];
        for n=1:round(ka)+dN
            para_ela(8)=n;
            [x, f_inf]=elastic_fs(proc_flag,scale,out_flag,para_ela);
            fm(n)=abs(f_inf(1));
        end
%        [ka, fm]=elastic_fs(proc_flag,scale,out_flag,para_ela);
end
err5=fm(end-dN+5:end-dN+5)-fm(end);
err10=fm(end-dN+10:end-dN+10)-fm(end);
err5_str=sprintf('%5.3e',err5);
err10_str=sprintf('%5.3e',err10);

figure(1)
ni=1:length(fm);
plot(ni,abs(fm),'.-',[ka ka],[0 1.5*max(abs(fm))],'--r')
xlabel('Number of Terms','fontsize',20)
ylabel('Form Function |f_{\infty}(ka)|','fontsize',20)
text(ka+0.5,0.9*max(abs(fm)),sprintf('ka = %3.1f',ka),'fontsize',12,'fontweight','bold')
text(0.8,0.95,['\epsilon_{ka+5} = ' err5_str],'sc','fontsize',12,'fontweight','bold')
text(0.8,0.85,['\epsilon_{ka+10} = ' err10_str],'sc','fontsize',12,'fontweight','bold')
axis([0 round(ka)+dN 0 1.2*max(abs(fm))])