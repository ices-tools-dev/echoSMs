function  out=basct_DWBA_elliposid(para)
% Acoustic backscattering by a fluid weakly scattering elliptical slice
% using DWBA - based on the talk given at the 2008 SEAFACTS symposium
% return the differential backscattering cross section
% INPUT parameters:
%% shape parameters
%         .shape.a:   semi-minor axis (height in mm) - dorsal aspect  
%         .shape.b:   semi-minor axis (width in mm)  - lateral aspect  
%      
%% physical properties
%     para.phy.g:   density contrast
%         .phy.h:   sound speed contrast
%% simulation parameters
%         .simu.cw;               % sound speed in water (m/s)
%         .simu.freq;             % frequrncy (Hz)
%         .simu.theta;            % mean angle of incidence in deg    (0 for broadside)
%         .simu.phi;              % azimuth angle of incidence in deg (0 for dorsal aspect)
% OUTPUT:
%     out.fun                     % output function
% Dezhang Chu  Dec 11, 2019
% 

%%%% Input parameters
%% physical properties of the scattering object
g=para.phy.g;           
h=para.phy.h;

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

    %% geometric shape of the object as a function of z
z = para.shape.z*1e-3;           % lengthwise position vector in mm --> m
a=para.shape.a*1e-3;          % semi-minor axis (height in mm) --> m
b=para.shape.b*1e-3;          % semi-minor axis (width in mm)  --> m
xm=para.shape.xm*1e-3;        % semi-minor axis (width in mm)  --> m
dz = z(2) - z(1);
fact0=Cb*k.*k./2;
L = z(end);
%% ref phase at the center
phs_z0 = k1*L/2;
func0 = 0;

z = z - mean(z);

% load ref_out
for i = 1:para.simu.ni
    if i == 1 | rem(i,100) == 0
        fprintf('  --- %d of %d\n', i, para.simu.ni);
    end
    mu_th=sqrt(mu_x.*mu_x+(b(i)/(a(i)+eps)*mu_y).^2);
    
    if para.simu.ave_flag <= 1 | para.simu.ave_flag == 3
        arg=mu_th*k1*a(i) + eps;
    else
        arg=k1*mu_th*a(i) + eps;
    end
    ind = find( (abs(arg) <= eps ) == 1);
    J1=besselj(1,arg);
    if ~isempty(ind)
        J1(ind) = 0.5*arg;
    end
    if size(mu_z, 1) > size(k, 1) | size(mu_x, 1) > size(k, 1)
        %% phase offset resulting from z-direction devoation relative to the incident wave
        phs_z = mu_z*k1*z(i);
        %% phase offset resulting from x-direction devoation relative to the incident wave
        phs_x = mu_x*k*xm(i);
    else
        %% phase offset resulting from z-direction devoation relative to the incident wave
        phs_z = k1*mu_z*z(i);
        %% phase offset resulting from x-direction devoation relative to the incident wave
        phs_x = k*mu_x*xm(i);
    end
    %% total phase offset
    phs_tot = 0*phs_z0 + phs_z + phs_x;
    
    [m,n]=size(J1);
    if i == 1
        if length(k) > 1
            fact=fact0(ones(m,1),:);
        else
            fact=ones(m,n)*fact0;
        end
    end
    %% integration
    sincJ = J1./arg;        % arg << 1, sincJ = 0.5
    I0 = a(i)*b(i)*sincJ.*exp(-1i*phs_tot);
%     I1(i, 1:2) = I0(i,:).*sincJ;
    func0 = func0 + I0;
%     if i == 1
%         fprintf('    Analy: %10.5f \t %10.6f \t %10.6f \n', fact1, phs_z0, du)
%         fprintf('Numerical: %10.5f \t %10.6f \t %10.6f \n', fact0, mu_z(2)*k1, dz)
%     end
%         
%     fprintf('i = %d\n --------- \n', i)
%     fprintf('    Analy: %10.5f \t %10.6f \t %10.5f \t %10.6f \t %4.2f\n', ai(i), bi(i), Ia(i), I(i), 0.5)
%     fprintf('Numerical: %10.5f \t %10.6f \t %10.5f \t %10.6f \t %4.2f\n', a(i), b(i), I0(i, 2), I1(i, 2), sincJ(2))
end

% integrated scattering amplitude
out.fun=abs(fact.*func0*dz).^2;
% 10*log10(out.fun)



end
