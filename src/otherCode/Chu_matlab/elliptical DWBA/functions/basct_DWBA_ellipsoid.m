function  out=basct_DWBA_elliposid(para)
% Acoustic backscattering by a fluid weakly scattering elliposid
% using DWBA - based on the talk given at the 2008 SEAFACTS symposium
% return the differential backscattering cross section
% INPUT parameters:
%% shape parameters
%         .shape.a:   semi-minor axis (height/2 in mm) - dorsal aspect  
%         .shape.b:   semi-minor axis (width/2 in mm)  - vental aspect  
%         .shape.c:   semi-major axis (length/2 in mm) - head-end aspect 
%      Note: a & b < c prolate spheroid; a & b > c oblate spheroid; a=b=c sphere
%% physical properties
%     para.phy.g:   density contrast
%         .phy.h:   sound speed contrast
%% simulation parameters
%         .simu.cw;               % sound speed in water (m/s)
%         .simu.freq;             % frequrncy (Hz)
%         .simu.theta;            % mean angle of incidence in deg    (0 for broadside)
%         .simu.phi;              % azimuth angle of incidence in deg (0 for dorsal aspect)
%         .out_flag;              % 1 = back scattering amplitude
%                                 % 2 = differential backscattering cross section
%                                 % 3 = target strength
% OUTPUT:
%     out.fun                     % output function
% Dezhang Chu  June 28, 2011
% Modified May 14, 2019 - updated comments
% Modified Aug 04, 2021 - updated comments (a, b, c)

%%%% Input parameters
%% physical properties of the scattering object
g=para.phy.g;           
h=para.phy.h;
%% geometric shape of the object
a=para.shape.a*1e-3;                 % semi-minor axis (height in mm --> m)
b=para.shape.b*1e-3;                 % semi-minor axis (width in mm --> m)
c=para.shape.c*1e-3;                 % semi-major axis (length in mm --> m)
%% simulation parameters
cw=para.simu.cw;                % sound speed in water (m/s)
freq=para.simu.freq;            % frequrncy (Hz)
th=para.simu.theta*pi/180;      % angle of incidence in deg, converting to radians   (0 for broadside)
phi=para.simu.phi*pi/180;       % azimuth angle of incidence in deg, converting to radians ( 0 for dorsal aspect)

Cb=(1-g*h*h)/(g*h*h)-(g-1)/g;   

if length(th) > 1 & length(phi) > 1 & length(freq) > 1
    fprintf('Only any two of the three varibles: Len, theta, and phi can be arrays!!\n');
    out=-1;
    return
elseif length(freq) > 1 & length(th) > 1  % TS vs freq and theta (polor angle)
    if  para.simu.ave_flag <= 1 | para.simu.ave_flag == 3
        n=length(freq);
        m=length(th);
        freq=reshape(freq,1,n);
        th=th(:);
    else
        n=length(th);
        m=length(freq);
        th=reshape(th,1,n);
        freq=freq(:);
    end
elseif length(freq) > 1 & length(phi) > 1 % TS vs freq and phi (azimuth  angle)
    if para.simu.ave_flag <= 1 | para.simu.ave_flag == 3
        n=length(freq);
        m=length(phi);
        freq=reshape(freq,1,n);
        phi=phi(:);
    else
        n=length(phi);
        m=length(freq);
        phi=reshape(phi,1,n);
        freq=freq(:);
    end
elseif length(th) > 1 & length(phi) > 1   % TS vs theta and phi
    if para.simu.ave_flag == 0 | ~isfield(para.simu, 'ave_angle_type') | para.simu.ave_angle_type == 1 
        n=length(th);
        m=length(phi);
        th=th(:);
        phi=reshape(phi,1,m);
    else
        n=length(phi);
        m=length(th);
        th=reshape(th,1,m);
        phi=phi(:);
    end
end

k=2*pi*freq/cw;
k1=k/h;
if (para.simu.ave_flag <= 1 | para.simu.ave_flag == 4) & length(th) > 1 & length(phi) > 1
    if para.simu.ave_flag == 0 | ~isfield(para.simu, 'ave_angle_type') | para.simu.ave_angle_type == 1  % average over theta
        mu_x=2*cos(th)*cos(phi);
        mu_y=2*cos(th)*sin(phi);
        mu_z=2*sin(th)*ones(1,m);
    else                              % average over phi
        mu_x=2*cos(phi)*cos(th);
        mu_y=2*sin(phi)*cos(th);
        mu_z=2*ones(n,1)*sin(th);
    end
else
    if  para.simu.ave_flag == 0   % no average
        mu_x=2*cos(th)*cos(phi);
        mu_y=2*cos(th)*sin(phi);
        mu_z=2*sin(th);
    else   % average over length
        mu_x=2*cos(phi)*cos(th);
        mu_y=2*sin(phi)*cos(th);
        mu_z=2*sin(th);
    end
end
mu_th=sqrt(mu_x.*mu_x+(b/a*mu_y).^2+(c/a*mu_z).^2);

if para.simu.ave_flag <= 1 | para.simu.ave_flag == 3
    arg=mu_th*k1*a+eps;
else
    arg=k1*mu_th*a+eps;
end
J1_5=besselj(1.5,arg+eps);
jn=sqrt(pi./(2*(arg+eps))).*J1_5;

fact=Cb*k.*k.*a*b*c;
[m,n]=size(jn);
if length(k) > 1
    fact=fact(ones(m,1),:);
else
    fact=ones(m,n)*fact;
end

func0=jn./(arg+eps);
% scattering amplitude
out.fun=fact.*func0;
% differntial backscattering cross section
out.fun=abs(out.fun).^2;



end
