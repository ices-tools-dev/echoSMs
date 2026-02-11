%% demo program to call elastic_fs.m

clear

addpath c:/bin/matlab  -end

out_flag=1;				% modular of form function
proc_flag=1;			% complex form function vs angle
scale=1;				% linear(1)/log(2) spacing in freq or angle 
n=5000;			        % number of computation points 
cw=1500;                % sound speed in water
freq=38e3;              % frequency in Hz
a=0.5e-2;               % equivalent spherical radius of the fish swimbladder
ka=2*pi*freq*a/cw;      % ka value
ang_st=180;               % starting scattering angle: 0 is forward
ang_end=360;		    % end ka value
D=0;                  % depth in m  (Boyle's law)
g=0.00123*sqrt(1+D/10);  % density contrast at 
h=0.22;					% compressional sound speed contrast
g=0.2;
h=0.5;

ka_st=0.01;
ka_end=10;
m=40;
para_fldm=[n ka_st ka_end g h ang_st m];
para_fld=[n ka_st ka_end g h ang_st 30];

[var, fx]=fluid_fs(proc_flag,scale,out_flag,para_fld);
[var1, fxm]=fluid_fs(proc_flag,scale,out_flag,para_fldm);

if proc_flag == 1
    figure(1)
%     semilogx(var,20*log10(abs(fx)),'-',var,20*log10(abs(fxm)),'-r','linewidth',2)
    fac=1/(4*pi);
%     semilogx(var,fac*(abs(fx).^2),'-',var,fac*(abs(fxm).^2),'-r','linewidth',2)
    plot(var,(abs(fx).^2),'-',var,(abs(fxm).^2),'-r','linewidth',2)

    text(0.9,0.95,sprintf('n=%d',m),'sc','color','r')
    xlabel('ka')
%     ylabel('Form Function |f|')
    ylabel('\sigma_{fwd}/(4*\pi)')
    grid
    %% compute Q
    [var_max,find]=max(abs(fx));
    
else
    figure(1)
    hdl=polar(var,real(fx));
    set(hdl,'linewidth',2)
    title('Re(Form_function)')
    axis square
    figure(2)
    hdl=polar(var,imag(fx));
    set(hdl,'linewidth',2)
    title('Im(Form_function)')
    axis square
    figure(3)
    hdl=polar(var,abs(fx));
    set(hdl,'linewidth',2)
    title('|Form_function|')
    axis square
end

